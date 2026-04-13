from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import users, products, search, admin, orders, downloads
from . import models
import os
import subprocess
from app.database import SessionLocal, engine, Base
from app import models
from app.auth import get_password_hash
from sqlalchemy import text

app = FastAPI(title="Marketplace PO API")

print("=" * 60)
print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
print("=" * 60)

db_path = engine.url.database
print(f"Путь к базе данных: {db_path}")

# ВСЕГДА пересоздаем таблицы (чистый старт)
print("\nПересоздание таблиц...")
Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("✅ Таблицы пересозданы")

db = SessionLocal()

try:
    # --- 1. Категории ---
    print("\nСоздание категорий...")
    categories_data = [
        ("Интеграции", "API, webhooks, синхронизация систем", "🔌"),
        ("Аналитика и BI", "Дашборды, отчеты, визуализация данных", "📊"),
        ("CRM и ERP", "Bitrix24, 1С, AmoCRM, Salesforce", "👥"),
        ("Документооборот", "КП, договоры, счета, ЭДО", "📄"),
        ("Финансы и налоги", "Кассы, ФНС, банки, 54-ФЗ", "💰"),
        ("Автоматизация", "Скрипты, роботы, workflow, RPA", "⚡"),
        ("Маркетинг", "Email-рассылки, сегментация, воронки", "📧"),
        ("Склад и логистика", "Управление запасами, WMS, маркировка", "🚚"),
        ("Корпоративные коммуникации", "Боты, порталы, мессенджеры", "💬"),
        ("Базы данных", "SQL, NoSQL, ETL, миграции", "🗄️"),
        ("Безопасность", "Аутентификация, шифрование, аудит", "🔒"),
        ("Искусственный интеллект", "NLP, компьютерное зрение, прогнозирование", "🧠"),
    ]
    for name, desc, icon in categories_data:
        # Проверяем, существует ли уже категория
        existing_cat = db.query(models.Category).filter(models.Category.name == name).first()
        if not existing_cat:
            cat = models.Category(name=name, description=desc, icon=icon)
            db.add(cat)
    db.commit()
    print(f"✅ Категории добавлены (всего: {len(categories_data)})")

    # --- 2. Пользователи ---
    print("\nСоздание пользователей...")
    users_data = [
        ("admin", "admin@example.com", "admin123", "Администратор", "admin"),
        ("superuser", "super@example.com", "admin123", "Суперпользователь", "superuser"),
        ("dev_ivan", "ivan@example.com", "dev123", "Иван Петров", "developer"),
        ("dev_maria", "maria@example.com", "dev123", "Мария Соколова", "developer"),
        ("dev_alexey", "alexey@example.com", "dev123", "Алексей Козлов", "developer"),
        ("dev_elena", "elena@example.com", "dev123", "Елена Морозова", "developer"),
        ("manager_alex", "alex@example.com", "manager123", "Алексей Иванов", "manager"),
        ("buyer_anna", "anna@example.com", "buyer123", "Анна Смирнова", "user"),
        ("buyer_company", "company@example.com", "buyer123", "ООО Технологии", "user"),
    ]
    for username, email, pwd, fullname, role in users_data:
        existing_user = db.query(models.User).filter(models.User.username == username).first()
        if not existing_user:
            user = models.User(
                username=username,
                email=email,
                hashed_password=get_password_hash(pwd),
                full_name=fullname,
                role=role,
                is_active=True,
                created_at=datetime.utcnow()
            )
            db.add(user)
    db.commit()
    print(f"✅ Пользователи добавлены (всего: {len(users_data)})")

    # Получаем разработчиков
    dev_ivan = db.query(models.User).filter(models.User.username == "dev_ivan").first()
    dev_maria = db.query(models.User).filter(models.User.username == "dev_maria").first()
    dev_alexey = db.query(models.User).filter(models.User.username == "dev_alexey").first()
    dev_elena = db.query(models.User).filter(models.User.username == "dev_elena").first()

    # --- 3. Продукты (50 штук) ---
    print("\nСоздание продуктов (50 шт)...")
    products_data = [
        # Интеграции (1-10)
        ("Интеграция 1С с Telegram", "Автоматическая отправка отчетов из 1С в Telegram. Поддержка PDF, Excel, графиков.", 45000, "Интеграции", dev_ivan, 89, 2.5, "2.1.0"),
        ("Интеграция Bitrix24 с WhatsApp", "Двусторонняя синхронизация чатов WhatsApp с карточками сделок в Bitrix24.", 35000, "Интеграции", dev_ivan, 156, 1.8, "1.5.0"),
        ("API-шлюз для онлайн-касс", "Интеграция с АТОЛ, Штрих-М, Эвотор. Отправка чеков, работа с ФНС.", 65000, "Интеграции", dev_ivan, 67, 8.5, "1.2.0"),
        ("Синхронизация 1С и Wildberries", "Автоматическая выгрузка товаров, остатков и цен на Wildberries.", 55000, "Интеграции", dev_maria, 234, 3.2, "2.0.0"),
        ("Интеграция AmoCRM с Telegram", "Уведомления о новых сделках, лидах и задачах в Telegram.", 25000, "Интеграции", dev_alexey, 312, 1.2, "1.8.0"),
        ("Связка Google Sheets и 1С", "Обмен данными между Google Sheets и 1С:Предприятие.", 30000, "Интеграции", dev_maria, 178, 1.5, "1.3.0"),
        ("Интеграция Jira с Telegram", "Уведомления о задачах, комментариях и смене статусов.", 28000, "Интеграции", dev_alexey, 203, 0.9, "2.2.0"),
        ("Синхронизация CRM и Email", "Автоматическая синхронизация контактов и рассылок.", 32000, "Интеграции", dev_elena, 145, 1.1, "1.4.0"),
        ("Интеграция МойСклад с 1С", "Двусторонняя синхронизация товаров, остатков и заказов.", 48000, "Интеграции", dev_ivan, 92, 2.8, "1.1.0"),
        ("API-шлюз для платежных систем", "Единый API для Tinkoff, Sberbank, ЮKassa, Stripe.", 58000, "Интеграции", dev_maria, 67, 4.2, "2.0.0"),
        # Аналитика и BI (11-20)
        ("Дашборд для руководителя (Power BI)", "KPI по продажам, загрузке склада, дебиторской задолженности.", 55000, "Аналитика и BI", dev_maria, 203, 4.5, "1.8.0"),
        ("Анализ отзывов (NLP)", "Мониторинг отзывов с маркетплейсов. Анализ тональности, категоризация.", 42000, "Аналитика и BI", dev_maria, 187, 2.1, "1.4.0"),
        ("Прогнозирование продаж (ML)", "Модель машинного обучения для прогноза продаж на 30 дней.", 89000, "Аналитика и BI", dev_alexey, 45, 12.5, "1.0.0"),
        ("ETL-коннектор для Tableau", "Выгрузка данных из 1С, CRM, ERP в Tableau.", 48000, "Аналитика и BI", dev_maria, 78, 3.8, "1.2.0"),
        ("Анализ конкурентов на WB/Ozon", "Сбор и анализ цен, остатков, рейтингов конкурентов.", 38000, "Аналитика и BI", dev_ivan, 234, 2.2, "2.1.0"),
        ("Дашборд для отдела продаж", "Воронка продаж, конверсии, средний чек, прогнозы.", 35000, "Аналитика и BI", dev_maria, 312, 2.5, "1.5.0"),
        ("Анализ эффективности рекламы", "Сбор данных из Яндекс.Директ, VK Реклама, MyTarget.", 29000, "Аналитика и BI", dev_elena, 156, 1.8, "1.3.0"),
        ("Сборщик данных для Google Looker", "ETL-процессы для Google Looker Studio.", 32000, "Аналитика и BI", dev_alexey, 89, 2.0, "1.1.0"),
        ("Анализ LTV и CAC клиентов", "Расчет LTV, CAC, ROI, удержания клиентов.", 39000, "Аналитика и BI", dev_maria, 167, 1.9, "1.4.0"),
        ("Мониторинг соцсетей (бренд-аналитика)", "Сбор упоминаний бренда в соцсетях и СМИ.", 44000, "Аналитика и BI", dev_elena, 123, 2.3, "1.2.0"),
        # CRM и ERP (21-30)
        ("CRM-воронка для Bitrix24", "Кастомные отчеты по воронке продаж, визуализация этапов.", 79000, "CRM и ERP", dev_maria, 234, 5.2, "1.5.0"),
        ("Модуль закупок для 1С", "Автоматизация закупок, работа с поставщиками.", 89000, "CRM и ERP", dev_ivan, 67, 6.5, "2.0.0"),
        ("Управление проектами в Bitrix24", "Расширенный функционал для управления проектами.", 49000, "CRM и ERP", dev_alexey, 178, 3.2, "1.3.0"),
        ("Складской учет в 1С", "Адресное хранение, сборка заказов, инвентаризация.", 69000, "CRM и ERP", dev_ivan, 92, 4.8, "1.8.0"),
        ("Модуль КДП для AmoCRM", "Карточки договоров, этапы, уведомления.", 35000, "CRM и ERP", dev_maria, 203, 1.5, "1.2.0"),
        ("Интеграция 1С с сайтом на Bitrix", "Синхронизация заказов, товаров, остатков.", 45000, "CRM и ERP", dev_ivan, 156, 2.8, "2.1.0"),
        ("Модуль командировок для 1С", "Учет командировок, авансов, отчетов.", 29000, "CRM и ERP", dev_alexey, 89, 1.2, "1.0.0"),
        ("Управление лидами в AmoCRM", "Автораспределение лидов, скоринг, воронки.", 38000, "CRM и ERP", dev_maria, 234, 1.8, "1.4.0"),
        ("Модуль кадрового учета", "Штатное расписание, приказы, табель.", 49000, "CRM и ERP", dev_elena, 67, 3.5, "1.1.0"),
        ("Управление складами (WMS)", "Паллетное хранение, маркировка, сборка.", 99000, "CRM и ERP", dev_ivan, 45, 8.2, "1.0.0"),
        # Документооборот (31-35)
        ("Генератор коммерческих предложений", "Автосборка КП из шаблонов, поддержка PDF, Excel.", 25000, "Документооборот", dev_maria, 312, 1.2, "4.0.0"),
        ("Электронный документооборот (ЭДО)", "Обмен документами с контрагентами через операторов ЭДО.", 59000, "Документооборот", dev_ivan, 89, 3.8, "1.2.0"),
        ("Автоматизация договоров", "Шаблоны, согласование, электронная подпись.", 45000, "Документооборот", dev_alexey, 156, 2.5, "1.5.0"),
        ("Генератор счетов и актов", "Автоматическое создание счетов и актов из CRM.", 19000, "Документооборот", dev_maria, 234, 0.8, "2.0.0"),
        ("Модуль первичных документов", "Счета-фактуры, накладные, УПД, ТОРГ-12.", 35000, "Документооборот", dev_elena, 178, 1.5, "1.3.0"),
        # Финансы и налоги (36-40)
        ("Автоматическая выгрузка в ФНС", "Отправка отчетности, поддержка XML, ЭЦП.", 89000, "Финансы и налоги", dev_ivan, 92, 3.2, "3.0.0"),
        ("Интеграция с банками (API)", "Выгрузка выписок, платежные поручения.", 49000, "Финансы и налоги", dev_maria, 145, 2.1, "1.4.0"),
        ("Расчет зарплаты и налогов", "Автоматический расчет зарплаты, НДФЛ, страховых.", 69000, "Финансы и налоги", dev_alexey, 67, 4.5, "1.1.0"),
        ("Модуль НДС для 1С", "Ведение книги покупок/продаж, расчет НДС.", 39000, "Финансы и налоги", dev_ivan, 123, 2.2, "2.0.0"),
        ("Интеграция с ЕГАИС", "Учет алкогольной продукции, отправка отчетов.", 79000, "Финансы и налоги", dev_maria, 34, 5.5, "1.0.0"),
        # Автоматизация (41-45)
        ("Telegram-бот для корпоративного портала", "Интеграция с Active Directory, запрос справок, отпусков.", 38000, "Автоматизация", dev_ivan, 178, 0.9, "2.3.0"),
        ("RPA-робот для Excel", "Автоматическая обработка Excel-отчетов.", 29000, "Автоматизация", dev_alexey, 234, 1.2, "1.2.0"),
        ("Автоматическая рассылка отчетов", "Отправка отчетов по email и Telegram по расписанию.", 22000, "Автоматизация", dev_maria, 312, 0.7, "1.5.0"),
        ("Workflow-движок на Camunda", "BPMN 2.0, согласование заявок, маршрутизация.", 120000, "Автоматизация", dev_maria, 45, 12.3, "0.9.5"),
        ("Чат-бот для сайта (AI)", "ИИ-бот для ответов на вопросы клиентов.", 49000, "Автоматизация", dev_alexey, 89, 2.8, "1.0.0"),
        # Маркетинг (46-50)
        ("Email-рассылка через Unisender", "Автоматические триггерные рассылки.", 25000, "Маркетинг", dev_elena, 156, 1.1, "1.3.0"),
        ("Сегментация клиентов (RFM)", "RFM-анализ, сегментация клиентской базы.", 32000, "Маркетинг", dev_maria, 203, 1.5, "1.2.0"),
        ("Автоворонка для Telegram", "Создание цепочек сообщений, рассылок, опросов.", 28000, "Маркетинг", dev_ivan, 234, 0.8, "1.4.0"),
        ("Сбор email-адресов с сайта", "Виджеты, popup, интеграция с CRM.", 18000, "Маркетинг", dev_alexey, 312, 0.5, "2.0.0"),
        ("Анализ конкурентов в соцсетях", "Мониторинг активности конкурентов в VK, Telegram.", 35000, "Маркетинг", dev_elena, 145, 1.8, "1.1.0"),
    ]
    
    for name, desc, price, category, developer, downloads, file_size, version in products_data:
        # Проверяем, существует ли уже продукт
        existing_product = db.query(models.Product).filter(models.Product.name == name).first()
        if not existing_product:
            product = models.Product(
                name=name,
                description=desc,
                price=price,
                category=category,
                developer_id=developer.id,
                download_url=f"https://example.com/download/{name.lower().replace(' ', '_')}",
                file_size=file_size,
                version=version,
                downloads_count=downloads,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(product)
    db.commit()
    print(f"✅ Продукты добавлены (всего: {len(products_data)})")

    # --- 4. Итоговая статистика ---
    print("\n" + "=" * 60)
    print("ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 60)
    print(f"👥 Пользователей: {db.query(models.User).count()}")
    print(f"📦 Продуктов: {db.query(models.Product).count()}")
    print(f"📂 Категорий: {db.query(models.Category).count()}")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()

finally:
    db.close()
    print("\n✅ Инициализация завершена")


FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        FRONTEND_URL,  # Сюда подставится URL из Render
    ],
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
