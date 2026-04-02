from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import users, products, search, admin, orders, downloads
from . import models
import os
from .database import SessionLocal
from . import models
from .auth import get_password_hash

def ensure_db_initialized():
    """Проверяет и инициализирует БД при запуске"""
    db = SessionLocal()
    try:
        if db.query(models.User).count() == 0:
            print("Инициализация базы данных...")
            # Создаем админа
            admin = models.User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✅ База данных инициализирована")
        else:
            print("✅ База данных уже содержит данные")
    except Exception as e:
        print(f"Ошибка инициализации: {e}")
    finally:
        db.close()

# Вызываем функцию при старте
ensure_db_initialized()

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketplace PO API")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vue dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(users.router)
app.include_router(products.router)
app.include_router(search.router)
app.include_router(admin.router)      
app.include_router(orders.router)     
app.include_router(downloads.router)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Welcome to Marketplace PO API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
