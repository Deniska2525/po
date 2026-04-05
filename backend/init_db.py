import os
from app.database import SessionLocal, engine, Base
from app import models
from app.auth import get_password_hash
import random
from datetime import datetime, timedelta

print("=" * 60)
print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
print("=" * 60)

# Создаем директорию для данных, если её нет
os.makedirs("data", exist_ok=True)

# ПЕРЕСОЗДАЁМ ВСЕ ТАБЛИЦЫ (удаляем старые и создаём новые)
print("Удаление старых таблиц...")
Base.metadata.drop_all(bind=engine)
print("✅ Старые таблицы удалены")

print("Создание новых таблиц...")
Base.metadata.create_all(bind=engine)
print("✅ Таблицы созданы")

db = SessionLocal()

try:
    print("Заполнение базы данных тестовыми данными...")
    
    # Создание категорий
    categories = [
        models.Category(name="Интеграции", description="API, webhooks, синхронизация", icon="🔌"),
        models.Category(name="Аналитика", description="BI, дашборды, отчеты", icon="📊"),
        models.Category(name="CRM/ERP", description="Bitrix24, 1С, AmoCRM", icon="👥"),
        models.Category(name="Документооборот", description="КП, договоры, ЭДО", icon="📄"),
        models.Category(name="Финансы", description="Касса, ФНС, 54-ФЗ", icon="💰"),
        models.Category(name="Автоматизация", description="Скрипты, роботы, workflow", icon="⚡"),
        models.Category(name="Маркетинг", description="Email, рассылки, сегментация", icon="📧"),
    ]
    for cat in categories:
        db.add(cat)
    db.commit()
    print(f"✅ Добавлено {len(categories)} категорий")
    
    # Создание пользователей
    users_data = [
        {"username": "superuser", "email": "super@example.com", "password": "admin123", 
         "full_name": "Super Admin", "role": "superuser", "bio": "Главный администратор"},
        {"username": "admin", "email": "admin@example.com", "password": "admin123", 
         "full_name": "Admin User", "role": "admin", "bio": "Системный администратор"},
        {"username": "dev_ivan", "email": "ivan@example.com", "password": "dev123", 
         "full_name": "Иван Петров", "role": "developer", "bio": "Разработчик интеграций"},
        {"username": "dev_maria", "email": "maria@example.com", "password": "dev123", 
         "full_name": "Мария Соколова", "role": "developer", "bio": "BI-аналитик"},
        {"username": "manager_alex", "email": "alex@example.com", "password": "manager123", 
         "full_name": "Алексей Иванов", "role": "manager", "bio": "Менеджер по автоматизации"},
        {"username": "buyer_anna", "email": "anna@example.com", "password": "buyer123", 
         "full_name": "Анна Смирнова", "role": "user", "bio": "Руководитель отдела"},
    ]
    
    for user_data in users_data:
        user = models.User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            bio=user_data["bio"]
        )
        db.add(user)
    db.commit()
    print(f"✅ Добавлено {len(users_data)} пользователей")
    
    # Получаем объекты для связей (через refresh или query)
    # Обновляем объекты, чтобы получить их ID
    for user in db.query(models.User).all():
        db.refresh(user)
    
    # Получаем разработчиков по username
    dev_ivan = db.query(models.User).filter(models.User.username == "dev_ivan").first()
    dev_maria = db.query(models.User).filter(models.User.username == "dev_maria").first()
    
    # Получаем категории для связей
    categories_dict = {}
    for cat in db.query(models.Category).all():
        categories_dict[cat.name] = cat
    
    # Создание продуктов
    products_data = [
        {"name": "Интеграция 1С ↔ Telegram", "description": "Отправка отчетов из 1С в Telegram", 
         "price": 45000, "category_name": "Интеграции", "developer": dev_ivan, "downloads": 89, "file_size": 2.5, "version": "2.1.0"},
        {"name": "Сборщик данных Wildberries", "description": "Парсинг статистики продаж", 
         "price": 35000, "category_name": "Аналитика", "developer": dev_ivan, "downloads": 156, "file_size": 1.8, "version": "3.2.0"},
        {"name": "CRM-воронка для Bitrix24", "description": "Кастомные отчеты по воронке", 
         "price": 79000, "category_name": "CRM/ERP", "developer": dev_maria, "downloads": 234, "file_size": 5.2, "version": "1.5.0"},
        {"name": "Генератор коммерческих предложений", "description": "Автосборка КП из шаблонов", 
         "price": 25000, "category_name": "Документооборот", "developer": dev_maria, "downloads": 312, "file_size": 1.2, "version": "4.0.0"},
        {"name": "API-шлюз для онлайн-кассы", "description": "Интеграция с АТОЛ, Штрих-М", 
         "price": 65000, "category_name": "Финансы", "developer": dev_ivan, "downloads": 67, "file_size": 8.5, "version": "1.2.0"},
        {"name": "Telegram-бот для корпоративного портала", "description": "Интеграция с Active Directory", 
         "price": 38000, "category_name": "Интеграции", "developer": dev_ivan, "downloads": 178, "file_size": 0.9, "version": "2.3.0"},
        {"name": "ETL-коннектор для Power BI", "description": "Выгрузка данных в дашборды", 
         "price": 55000, "category_name": "Аналитика", "developer": dev_maria, "downloads": 203, "file_size": 4.5, "version": "1.8.0"},
        {"name": "API Gateway для микросервисов", "description": "Маршрутизация и аутентификация запросов", 
         "price": 99000, "category_name": "Интеграции", "developer": dev_ivan, "downloads": 45, "file_size": 12.0, "version": "1.0.0"},
        {"name": "Дашборд продаж для AmoCRM", "description": "Визуализация воронки и прогнозов", 
         "price": 49000, "category_name": "CRM/ERP", "developer": dev_maria, "downloads": 98, "file_size": 3.2, "version": "2.1.0"},
        {"name": "Автоматизация выставления счетов", "description": "Интеграция 1С и банк-клиента", 
         "price": 125000, "category_name": "Финансы", "developer": dev_ivan, "downloads": 34, "file_size": 6.8, "version": "1.5.0"},
    ]
    
    for p_data in products_data:
        category = categories_dict.get(p_data["category_name"])
        if category:
            product = models.Product(
                name=p_data["name"],
                description=p_data["description"],
                price=p_data["price"],
                category_id=category.id,  # Используем ID вместо имени
                developer_id=p_data["developer"].id,
                download_url=f"https://example.com/download/{p_data['name'].lower().replace(' ', '_')}",
                file_size=p_data["file_size"],
                version=p_data["version"],
                downloads_count=p_data["downloads"],
                is_active=True
            )
            db.add(product)
        else:
            print(f"⚠️ Категория '{p_data['category_name']}' не найдена для продукта '{p_data['name']}'")
    
    db.commit()
    print(f"✅ Добавлено {len(products_data)} продуктов")
    
    # Добавляем несколько отзывов к продуктам
    print("Добавление отзывов...")
    products = db.query(models.Product).all()
    users = db.query(models.User).filter(models.User.role == "user").all()
    
    reviews_data = [
        {"product": "Интеграция 1С ↔ Telegram", "user": "buyer_anna", "rating": 5, 
         "comment": "Отличная интеграция, работает стабильно!"},
        {"product": "Сборщик данных Wildberries", "user": "buyer_anna", "rating": 4, 
         "comment": "Хороший инструмент, но иногда тормозит"},
        {"product": "CRM-воронка для Bitrix24", "user": "manager_alex", "rating": 5, 
         "comment": "Лучшее решение для отчетности!"},
        {"product": "Генератор коммерческих предложений", "user": "manager_alex", "rating": 5, 
         "comment": "Экономит часы работы"},
        {"product": "Telegram-бот для корпоративного портала", "user": "dev_ivan", "rating": 5, 
         "comment": "Сам себе ставлю 5 😊"},
    ]
    
    for review_data in reviews_data:
        product = db.query(models.Product).filter(models.Product.name == review_data["product"]).first()
        user = db.query(models.User).filter(models.User.username == review_data["user"]).first()
        if product and user:
            review = models.Review(
                product_id=product.id,
                user_id=user.id,
                rating=review_data["rating"],
                comment=review_data["comment"],
                created_at=datetime.now()
            )
            db.add(review)
    
    db.commit()
    print(f"✅ Добавлено отзывов: {len(reviews_data)}")
    
    # Обновляем счетчики продуктов (количество отзывов, средний рейтинг)
    print("Обновление статистики продуктов...")
    for product in db.query(models.Product).all():
        reviews = db.query(models.Review).filter(models.Review.product_id == product.id).all()
        if reviews:
            product.reviews_count = len(reviews)
            product.rating = sum(r.rating for r in reviews) / len(reviews)
    
    db.commit()
    
    print("=" * 60)
    print("✅ ИНИЦИАЛИЗАЦИЯ УСПЕШНО ЗАВЕРШЕНА")
    print("=" * 60)
    
    # Вывод статистики
    print(f"\n📊 Статистика базы данных:")
    print(f"   - Пользователей: {db.query(models.User).count()}")
    print(f"   - Категорий: {db.query(models.Category).count()}")
    print(f"   - Продуктов: {db.query(models.Product).count()}")
    print(f"   - Отзывов: {db.query(models.Review).count()}")
    
except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()
