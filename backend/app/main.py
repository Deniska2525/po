import os
from contextlib import asynccontextmanager, AsyncExitStack
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .rate_limit import limiter
from .database import engine, Base, SessionLocal
from .schema_sync import sync_schema
from . import seed_core
from . import seed_extra
from .routers import users, products, search, admin, orders, downloads, ai_search, favorites
from . import models
from .mcp_tools import mcp

# Создаём таблицы, если их ещё нет. НЕ удаляет и не трогает существующие данные
# (в отличие от прежней версии с Base.metadata.drop_all — та стирала всю базу
# при каждом рестарте контейнера). Тестовые данные заполняются один раз,
# отдельной командой `python init_db.py` (см. этот файл — он идемпотентен
# и ничего не делает, если данные уже есть).
Base.metadata.create_all(bind=engine)

# Дополнительно: безопасно добавляем недостающие КОЛОНКИ в уже существующие
# таблицы (create_all этого не делает — см. schema_sync.py). Нужно, потому что
# на бесплатном Render нет Shell, чтобы прогнать ALTER TABLE вручную после
# каждого изменения models.py.
sync_schema(engine, Base)

# Заполняем базу тестовыми пользователями/категориями/товарами при первом
# запуске (см. seed_core.py), затем расширяем каталог демо-товарами для
# разнообразия (см. seed_extra.py). Оба идемпотентны: на пустой базе
# отрабатывают один раз, при повторных рестартах ничего не дублируют.
_seed_db = SessionLocal()
try:
    seed_core.run(_seed_db)
    seed_extra.run(_seed_db)
finally:
    _seed_db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ВАЖНО: у FastMCP свой session manager, который обязательно нужно
    # запустить через контекст-менеджер приложения — иначе MCP-эндпоинт
    # будет отвечать ошибкой "Task group is not initialized" на каждый запрос.
    # См. https://gofastmcp.com/integrations/fastapi
    async with AsyncExitStack() as stack:
        await stack.enter_async_context(mcp.session_manager.run())
        yield


app = FastAPI(title="Marketplace PO API", lifespan=lifespan)

# Rate limiting (slowapi): лимиты на /users/login и /users/register
# защищают от перебора паролей и спама регистраций (см. rate_limit.py)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Настройка CORS: явные списки методов/заголовков вместо "*" —
# с allow_credentials=True лучше не давать шире, чем нужно
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost",
        FRONTEND_URL,  # Сюда подставится URL из Render
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Подключение роутеров
app.include_router(users.router)
app.include_router(products.router)
app.include_router(search.router)
app.include_router(admin.router)
app.include_router(orders.router)
app.include_router(downloads.router)
app.include_router(ai_search.router)
app.include_router(favorites.router)

# MCP-сервер каталога — доступен по /mcp для внешних ИИ-агентов
# (Claude Desktop и т.п.). Публичный, без авторизации: это read-only поиск
# по каталогу, то же самое, что виден любому посетителю сайта.
app.mount("/mcp", mcp.streamable_http_app())

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Welcome to Marketplace PO API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
