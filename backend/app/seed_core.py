# -*- coding: utf-8 -*-
"""
Начальное наполнение БД: базовые категории, тестовые пользователи
и несколько демо-товаров.

Идемпотентно: если в базе уже есть хоть один пользователь или товар —
ничего не делает. Вызывается автоматически при каждом старте приложения
(см. app/main.py), поэтому при обычной работе через docker-compose
отдельно запускать ничего не нужно — база сама заполнится при первом
поднятии контейнера.

Логика перенесена сюда из backend/init_db.py, который теперь — тонкая
обёртка для ручного запуска (см. его комментарий).
"""
import os
from sqlalchemy.orm import Session
from . import models
from .auth import get_password_hash

# Пароли демо-аккаунтов берутся из окружения (см. .env.example).
# Дефолты — длинные уникальные строки, которых нет в базах утечек
# (старые admin123/dev123 есть в утечках — из-за них Chrome после каждого
# входа предлагал сменить пароль).
# "or" вместо второго аргумента getenv: docker-compose передаёт незаданные
# переменные как ПУСТЫЕ строки, а getenv с дефолтом их не подменяет.
SEED_ADMIN_PASSWORD = os.getenv("SEED_ADMIN_PASSWORD") or "Sup3r-Adm1n!mp2026"
SEED_DEV_PASSWORD = os.getenv("SEED_DEV_PASSWORD") or "D3v-Us3r!mp2026"
SEED_USER_PASSWORD = os.getenv("SEED_USER_PASSWORD") or "Dem0-Us3r!mp2026"


def run(db: Session) -> None:
    users_count = db.query(models.User).count()
    products_count = db.query(models.Product).count()

    if users_count != 0 or products_count != 0:
        return  # уже инициализировано — ничего не делаем

    # В проде демо-аккаунты с известными логинами — готовая дыра.
    # Создаём их только если это явно разрешено переменной SEED_DEMO_USERS=true.
    if os.getenv("ENV", "development") == "production" and os.getenv("SEED_DEMO_USERS") != "true":
        print("⚠️  [seed_core] production: демо-данные не создаются (SEED_DEMO_USERS != true)")
        return

    print("🌱 [seed_core] База пуста — создаю тестовые категории, пользователей и товары…")

    # 1. Категории
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

    # 2. Пользователи
    users_data = [
        {"username": "superuser", "email": "super@example.com", "password": SEED_ADMIN_PASSWORD,
         "full_name": "Super Admin", "role": "superuser", "bio": "Главный администратор"},
        {"username": "admin", "email": "admin@example.com", "password": SEED_ADMIN_PASSWORD,
         "full_name": "Admin User", "role": "admin", "bio": "Системный администратор"},
        {"username": "dev_ivan", "email": "ivan@example.com", "password": SEED_DEV_PASSWORD,
         "full_name": "Иван Петров", "role": "developer", "bio": "Разработчик интеграций"},
        {"username": "dev_maria", "email": "maria@example.com", "password": SEED_DEV_PASSWORD,
         "full_name": "Мария Соколова", "role": "developer", "bio": "BI-аналитик"},
        {"username": "manager_alex", "email": "alex@example.com", "password": SEED_USER_PASSWORD,
         "full_name": "Алексей Иванов", "role": "manager", "bio": "Менеджер по автоматизации"},
        {"username": "buyer_anna", "email": "anna@example.com", "password": SEED_USER_PASSWORD,
         "full_name": "Анна Смирнова", "role": "user", "bio": "Руководитель отдела"},
    ]
    for user_data in users_data:
        db.add(models.User(
            username=user_data["username"],
            email=user_data["email"],
            hashed_password=get_password_hash(user_data["password"]),
            full_name=user_data["full_name"],
            role=user_data["role"],
            bio=user_data["bio"],
        ))
    db.commit()

    dev_ivan = db.query(models.User).filter(models.User.username == "dev_ivan").first()
    dev_maria = db.query(models.User).filter(models.User.username == "dev_maria").first()

    # 3. Продукты
    products_data = [
        {"name": "Интеграция 1С ↔ Telegram", "description": "Отправка отчетов из 1С в Telegram",
         "price": 45000, "category": "Интеграции", "developer": dev_ivan, "downloads": 89, "file_size": 2.5, "version": "2.1.0"},
        {"name": "Сборщик данных Wildberries", "description": "Парсинг статистики продаж",
         "price": 35000, "category": "Аналитика", "developer": dev_ivan, "downloads": 156, "file_size": 1.8, "version": "3.2.0"},
        {"name": "CRM-воронка для Bitrix24", "description": "Кастомные отчеты по воронке",
         "price": 79000, "category": "CRM/ERP", "developer": dev_maria, "downloads": 234, "file_size": 5.2, "version": "1.5.0"},
        {"name": "Генератор коммерческих предложений", "description": "Автосборка КП из шаблонов",
         "price": 25000, "category": "Документооборот", "developer": dev_maria, "downloads": 312, "file_size": 1.2, "version": "4.0.0"},
        {"name": "API-шлюз для онлайн-кассы", "description": "Интеграция с АТОЛ, Штрих-М",
         "price": 65000, "category": "Финансы", "developer": dev_ivan, "downloads": 67, "file_size": 8.5, "version": "1.2.0"},
        {"name": "Telegram-бот для корпоративного портала", "description": "Интеграция с Active Directory",
         "price": 38000, "category": "Интеграции", "developer": dev_ivan, "downloads": 178, "file_size": 0.9, "version": "2.3.0"},
        {"name": "ETL-коннектор для Power BI", "description": "Выгрузка данных в дашборды",
         "price": 55000, "category": "Аналитика", "developer": dev_maria, "downloads": 203, "file_size": 4.5, "version": "1.8.0"},
    ]
    for p_data in products_data:
        db.add(models.Product(
            name=p_data["name"],
            description=p_data["description"],
            price=p_data["price"],
            category=p_data["category"],
            developer_id=p_data["developer"].id,
            download_url=f"https://example.com/download/{p_data['name'].lower().replace(' ', '_')}",
            file_size=p_data["file_size"],
            version=p_data["version"],
            downloads_count=p_data["downloads"],
            is_active=True,
        ))
    db.commit()

    print(f"✅ [seed_core] Готово: {len(users_data)} пользователей, "
          f"{len(products_data)} товаров, {len(categories)} категорий")
