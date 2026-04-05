from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base, SessionLocal
from .routers import users, products, search, admin, orders, downloads
from . import models
import os
from .auth import get_password_hash
from datetime import datetime

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

def init_database():
    """Инициализация базы данных тестовыми данными"""
    db = SessionLocal()
    try:
        # Проверяем, есть ли пользователи
        if db.query(models.User).count() > 0:
            return {"message": "База данных уже содержит данные", "status": "already"}
        
        print("Создание тестовых данных...")
        
        # 1. Создаем категории
        categories = [
            models.Category(name="Интеграции", description="API, webhooks, синхронизация", icon="🔌"),
            models.Category(name="Аналитика", description="BI, дашборды, отчеты", icon="📊"),
            models.Category(name="CRM/ERP", description="Bitrix24, 1С, AmoCRM", icon="👥"),
            models.Category(name="Документооборот", description="КП, договоры, ЭДО", icon="📄"),
            models.Category(name="Автоматизация", description="Скрипты, роботы, workflow", icon="⚡"),
        ]
        for cat in categories:
            db.add(cat)
        db.commit()
        print("✅ Категории созданы")
        
        # 2. Создаем пользователей
        users_data = [
            {"username": "admin", "email": "admin@example.com", "password": "admin123", "full_name": "Admin User", "role": "admin"},
            {"username": "superuser", "email": "super@example.com", "password": "admin123", "full_name": "Super User", "role": "superuser"},
            {"username": "dev_ivan", "email": "ivan@example.com", "password": "dev123", "full_name": "Иван Петров", "role": "developer"},
            {"username": "dev_maria", "email": "maria@example.com", "password": "dev123", "full_name": "Мария Соколова", "role": "developer"},
            {"username": "buyer_anna", "email": "anna@example.com", "password": "buyer123", "full_name": "Анна Смирнова", "role": "user"},
        ]
        
        for user_data in users_data:
            user = models.User(
                username=user_data["username"],
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
                full_name=user_data["full_name"],
                role=user_data["role"],
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
        db.commit()
        print("✅ Пользователи созданы")
        
        # 3. Получаем разработчика
        dev_ivan = db.query(models.User).filter(models.User.username == "dev_ivan").first()
        
        # 4. Создаем продукты
        products_data = [
            {"name": "Интеграция 1С с Telegram", "description": "Отправка отчетов из 1С в Telegram. Поддержка PDF, Excel, графиков.", "price": 45000, "category": "Интеграции", "downloads": 89},
            {"name": "Сборщик данных Wildberries", "description": "Парсинг статистики продаж, остатков и цен конкурентов.", "price": 35000, "category": "Аналитика", "downloads": 156},
            {"name": "CRM-воронка для Bitrix24", "description": "Кастомные отчеты по воронке продаж. Визуализация этапов сделок.", "price": 79000, "category": "CRM/ERP", "downloads": 234},
            {"name": "Генератор коммерческих предложений", "description": "Автоматическая сборка КП из шаблонов. Поддержка PDF, Excel.", "price": 25000, "category": "Документооборот", "downloads": 312},
            {"name": "API-шлюз для онлайн-кассы", "description": "Интеграция с АТОЛ, Штрих-М. Отправка чеков, работа с ФНС.", "price": 65000, "category": "Интеграции", "downloads": 67},
            {"name": "Telegram-бот для корпоративного портала", "description": "Интеграция с Active Directory. Запрос справок, отпусков.", "price": 38000, "category": "Интеграции", "downloads": 178},
            {"name": "ETL-коннектор для Power BI", "description": "Выгрузка данных из 1С, CRM в Power BI. Автообновление дашбордов.", "price": 55000, "category": "Аналитика", "downloads": 203},
            {"name": "Анализ отзывов (NLP)", "description": "Мониторинг отзывов с маркетплейсов. Анализ тональности, алерты.", "price": 42000, "category": "Аналитика", "downloads": 187},
        ]
        
        for p_data in products_data:
            product = models.Product(
                name=p_data["name"],
                description=p_data["description"],
                price=p_data["price"],
                category=p_data["category"],
                developer_id=dev_ivan.id,
                download_url=f"https://example.com/download/{p_data['name'].lower().replace(' ', '_')}",
                file_size=round(p_data["downloads"] / 100, 1),
                version="1.0.0",
                downloads_count=p_data["downloads"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(product)
        db.commit()
        print("✅ Продукты созданы")
        
        return {"message": "База данных успешно инициализирована", "status": "success"}
        
    except Exception as e:
        db.rollback()
        print(f"Ошибка: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

app = FastAPI(title="Marketplace PO API")
app.post("/admin/init-db")

# Настройка CORS
# Получаем URL фронтенда из переменной окружения
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
# Для разработки можно разрешить несколько URL
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Локальная разработка
    "http://localhost:3000",   # Альтернативный dev порт
    FRONTEND_URL,              # URL на Render'е (придет из переменной)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Теперь массив, а не строка
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
