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


print("ИНИЦИАЛИЗАЦИЯ БАЗЫ ДАННЫХ")
print(f"🔍 DATABASE_URL: {os.getenv('DATABASE_URL', 'не задана!')[:80]}...")


# Проверяем подключение к БД
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Подключение к БД успешно")
except Exception as e:
    print(f"❌ Ошибка подключения к БД: {e}")
    exit(1)

# Создаем таблицы (только если их нет)
print("Создание таблиц (если не существуют)...")
Base.metadata.create_all(bind=engine)
print("✅ Таблицы созданы/проверены")

db = SessionLocal()

try:
    # Проверяем, есть ли уже данные
    users_count = db.query(models.User).count()
    products_count = db.query(models.Product).count()
    
    print(f"📊 Текущие данные: пользователей={users_count}, продуктов={products_count}")
    
    if users_count == 0 and products_count == 0:
        print("Заполнение базы данных тестовыми данными...")
        
        # Создание категорий
    print("\nСоздание категорий...")
    categories = [
        models.Category(name="Интеграции", description="API, webhooks, синхронизация систем", icon="🔌"),
        models.Category(name="Аналитика и BI", description="Дашборды, отчеты, визуализация данных", icon="📊"),
        models.Category(name="CRM и ERP", description="Bitrix24, 1С, AmoCRM, Salesforce", icon="👥"),
        models.Category(name="Документооборот", description="КП, договоры, счета, ЭДО", icon="📄"),
        models.Category(name="Финансы и налоги", description="Кассы, ФНС, банки, 54-ФЗ", icon="💰"),
        models.Category(name="Автоматизация", description="Скрипты, роботы, workflow, RPA", icon="⚡"),
        models.Category(name="Маркетинг", description="Email-рассылки, сегментация, воронки", icon="📧"),
        models.Category(name="Склад и логистика", description="Управление запасами, WMS, маркировка", icon="🚚"),
        models.Category(name="Корпоративные коммуникации", description="Боты, порталы, мессенджеры", icon="💬"),
        models.Category(name="Базы данных", description="SQL, NoSQL, ETL, миграции", icon="🗄️"),
        models.Category(name="Безопасность", description="Аутентификация, шифрование, аудит", icon="🔒"),
        models.Category(name="Искусственный интеллект", description="NLP, компьютерное зрение, прогнозирование", icon="🧠"),
    ]
    for cat in categories:
        db.add(cat)
    db.commit()
    print(f"✅ Добавлено {len(categories)} категорий")
        
        # 2. Пользователи
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
        
        # Получаем объекты
        dev_ivan = db.query(models.User).filter(models.User.username == "dev_ivan").first()
        dev_maria = db.query(models.User).filter(models.User.username == "dev_maria").first()
        
        # 3. Продукты
        products_data = [
        # Интеграции (1-10)
        {"name": "Интеграция 1С с Telegram", "description": "Автоматическая отправка отчетов из 1С в Telegram. Поддержка PDF, Excel, графиков.", "price": 45000, "category": "Интеграции", "dev": dev_ivan, "downloads": 89, "file_size": 2.5, "version": "2.1.0"},
        {"name": "Интеграция Bitrix24 с WhatsApp", "description": "Двусторонняя синхронизация чатов WhatsApp с карточками сделок в Bitrix24.", "price": 35000, "category": "Интеграции", "dev": dev_ivan, "downloads": 156, "file_size": 1.8, "version": "1.5.0"},
        {"name": "API-шлюз для онлайн-касс", "description": "Интеграция с АТОЛ, Штрих-М, Эвотор. Отправка чеков, работа с ФНС.", "price": 65000, "category": "Интеграции", "dev": dev_ivan, "downloads": 67, "file_size": 8.5, "version": "1.2.0"},
        {"name": "Синхронизация 1С и Wildberries", "description": "Автоматическая выгрузка товаров, остатков и цен на Wildberries.", "price": 55000, "category": "Интеграции", "dev": dev_maria, "downloads": 234, "file_size": 3.2, "version": "2.0.0"},
        {"name": "Интеграция AmoCRM с Telegram", "description": "Уведомления о новых сделках, лидах и задачах в Telegram.", "price": 25000, "category": "Интеграции", "dev": dev_alexey, "downloads": 312, "file_size": 1.2, "version": "1.8.0"},
        {"name": "Связка Google Sheets и 1С", "description": "Обмен данными между Google Sheets и 1С:Предприятие.", "price": 30000, "category": "Интеграции", "dev": dev_maria, "downloads": 178, "file_size": 1.5, "version": "1.3.0"},
        {"name": "Интеграция Jira с Telegram", "description": "Уведомления о задачах, комментариях и смене статусов.", "price": 28000, "category": "Интеграции", "dev": dev_alexey, "downloads": 203, "file_size": 0.9, "version": "2.2.0"},
        {"name": "Синхронизация CRM и Email", "description": "Автоматическая синхронизация контактов и рассылок.", "price": 32000, "category": "Интеграции", "dev": dev_elena, "downloads": 145, "file_size": 1.1, "version": "1.4.0"},
        {"name": "Интеграция МойСклад с 1С", "description": "Двусторонняя синхронизация товаров, остатков и заказов.", "price": 48000, "category": "Интеграции", "dev": dev_ivan, "downloads": 92, "file_size": 2.8, "version": "1.1.0"},
        {"name": "API-шлюз для платежных систем", "description": "Единый API для Tinkoff, Sberbank, ЮKassa, Stripe.", "price": 58000, "category": "Интеграции", "dev": dev_maria, "downloads": 67, "file_size": 4.2, "version": "2.0.0"},
        
        # Аналитика и BI (11-20)
        {"name": "Дашборд для руководителя (Power BI)", "description": "KPI по продажам, загрузке склада, дебиторской задолженности.", "price": 55000, "category": "Аналитика и BI", "dev": dev_maria, "downloads": 203, "file_size": 4.5, "version": "1.8.0"},
        {"name": "Анализ отзывов (NLP)", "description": "Мониторинг отзывов с маркетплейсов. Анализ тональности, категоризация.", "price": 42000, "category": "Аналитика и BI", "dev": dev_maria, "downloads": 187, "file_size": 2.1, "version": "1.4.0"},
        {"name": "Прогнозирование продаж (ML)", "description": "Модель машинного обучения для прогноза продаж на 30 дней.", "price": 89000, "category": "Аналитика и BI", "dev": dev_alexey, "downloads": 45, "file_size": 12.5, "version": "1.0.0"},
        {"name": "ETL-коннектор для Tableau", "description": "Выгрузка данных из 1С, CRM, ERP в Tableau.", "price": 48000, "category": "Аналитика и BI", "dev": dev_maria, "downloads": 78, "file_size": 3.8, "version": "1.2.0"},
        {"name": "Анализ конкурентов на WB/Ozon", "description": "Сбор и анализ цен, остатков, рейтингов конкурентов.", "price": 38000, "category": "Аналитика и BI", "dev": dev_ivan, "downloads": 234, "file_size": 2.2, "version": "2.1.0"},
        {"name": "Дашборд для отдела продаж", "description": "Воронка продаж, конверсии, средний чек, прогнозы.", "price": 35000, "category": "Аналитика и BI", "dev": dev_maria, "downloads": 312, "file_size": 2.5, "version": "1.5.0"},
        {"name": "Анализ эффективности рекламы", "description": "Сбор данных из Яндекс.Директ, VK Реклама, MyTarget.", "price": 29000, "category": "Аналитика и BI", "dev": dev_elena, "downloads": 156, "file_size": 1.8, "version": "1.3.0"},
        {"name": "Сборщик данных для Google Looker", "description": "ETL-процессы для Google Looker Studio.", "price": 32000, "category": "Аналитика и BI", "dev": dev_alexey, "downloads": 89, "file_size": 2.0, "version": "1.1.0"},
        {"name": "Анализ LTV и CAC клиентов", "description": "Расчет LTV, CAC, ROI, удержания клиентов.", "price": 39000, "category": "Аналитика и BI", "dev": dev_maria, "downloads": 167, "file_size": 1.9, "version": "1.4.0"},
        {"name": "Мониторинг соцсетей (бренд-аналитика)", "description": "Сбор упоминаний бренда в соцсетях и СМИ.", "price": 44000, "category": "Аналитика и BI", "dev": dev_elena, "downloads": 123, "file_size": 2.3, "version": "1.2.0"},
        
        # CRM и ERP (21-30)
        {"name": "CRM-воронка для Bitrix24", "description": "Кастомные отчеты по воронке продаж, визуализация этапов.", "price": 79000, "category": "CRM и ERP", "dev": dev_maria, "downloads": 234, "file_size": 5.2, "version": "1.5.0"},
        {"name": "Модуль закупок для 1С", "description": "Автоматизация закупок, работа с поставщиками.", "price": 89000, "category": "CRM и ERP", "dev": dev_ivan, "downloads": 67, "file_size": 6.5, "version": "2.0.0"},
        {"name": "Управление проектами в Bitrix24", "description": "Расширенный функционал для управления проектами.", "price": 49000, "category": "CRM и ERP", "dev": dev_alexey, "downloads": 178, "file_size": 3.2, "version": "1.3.0"},
        {"name": "Складской учет в 1С", "description": "Адресное хранение, сборка заказов, инвентаризация.", "price": 69000, "category": "CRM и ERP", "dev": dev_ivan, "downloads": 92, "file_size": 4.8, "version": "1.8.0"},
        {"name": "Модуль КДП для AmoCRM", "description": "Карточки договоров, этапы, уведомления.", "price": 35000, "category": "CRM и ERP", "dev": dev_maria, "downloads": 203, "file_size": 1.5, "version": "1.2.0"},
        {"name": "Интеграция 1С с сайтом на Bitrix", "description": "Синхронизация заказов, товаров, остатков.", "price": 45000, "category": "CRM и ERP", "dev": dev_ivan, "downloads": 156, "file_size": 2.8, "version": "2.1.0"},
        {"name": "Модуль командировок для 1С", "description": "Учет командировок, авансов, отчетов.", "price": 29000, "category": "CRM и ERP", "dev": dev_alexey, "downloads": 89, "file_size": 1.2, "version": "1.0.0"},
        {"name": "Управление лидами в AmoCRM", "description": "Автораспределение лидов, скоринг, воронки.", "price": 38000, "category": "CRM и ERP", "dev": dev_maria, "downloads": 234, "file_size": 1.8, "version": "1.4.0"},
        {"name": "Модуль кадрового учета", "description": "Штатное расписание, приказы, табель.", "price": 49000, "category": "CRM и ERP", "dev": dev_elena, "downloads": 67, "file_size": 3.5, "version": "1.1.0"},
        {"name": "Управление складами (WMS)", "description": "Паллетное хранение, маркировка, сборка.", "price": 99000, "category": "CRM и ERP", "dev": dev_ivan, "downloads": 45, "file_size": 8.2, "version": "1.0.0"},
        
        # Документооборот (31-35)
        {"name": "Генератор коммерческих предложений", "description": "Автосборка КП из шаблонов, поддержка PDF, Excel.", "price": 25000, "category": "Документооборот", "dev": dev_maria, "downloads": 312, "file_size": 1.2, "version": "4.0.0"},
        {"name": "Электронный документооборот (ЭДО)", "description": "Обмен документами с контрагентами через операторов ЭДО.", "price": 59000, "category": "Документооборот", "dev": dev_ivan, "downloads": 89, "file_size": 3.8, "version": "1.2.0"},
        {"name": "Автоматизация договоров", "description": "Шаблоны, согласование, электронная подпись.", "price": 45000, "category": "Документооборот", "dev": dev_alexey, "downloads": 156, "file_size": 2.5, "version": "1.5.0"},
        {"name": "Генератор счетов и актов", "description": "Автоматическое создание счетов и актов из CRM.", "price": 19000, "category": "Документооборот", "dev": dev_maria, "downloads": 234, "file_size": 0.8, "version": "2.0.0"},
        {"name": "Модуль первичных документов", "description": "Счета-фактуры, накладные, УПД, ТОРГ-12.", "price": 35000, "category": "Документооборот", "dev": dev_elena, "downloads": 178, "file_size": 1.5, "version": "1.3.0"},
        
        # Финансы и налоги (36-40)
        {"name": "Автоматическая выгрузка в ФНС", "description": "Отправка отчетности, поддержка XML, ЭЦП.", "price": 89000, "category": "Финансы и налоги", "dev": dev_ivan, "downloads": 92, "file_size": 3.2, "version": "3.0.0"},
        {"name": "Интеграция с банками (API)", "description": "Выгрузка выписок, платежные поручения.", "price": 49000, "category": "Финансы и налоги", "dev": dev_maria, "downloads": 145, "file_size": 2.1, "version": "1.4.0"},
        {"name": "Расчет зарплаты и налогов", "description": "Автоматический расчет зарплаты, НДФЛ, страховых.", "price": 69000, "category": "Финансы и налоги", "dev": dev_alexey, "downloads": 67, "file_size": 4.5, "version": "1.1.0"},
        {"name": "Модуль НДС для 1С", "description": "Ведение книги покупок/продаж, расчет НДС.", "price": 39000, "category": "Финансы и налоги", "dev": dev_ivan, "downloads": 123, "file_size": 2.2, "version": "2.0.0"},
        {"name": "Интеграция с ЕГАИС", "description": "Учет алкогольной продукции, отправка отчетов.", "price": 79000, "category": "Финансы и налоги", "dev": dev_maria, "downloads": 34, "file_size": 5.5, "version": "1.0.0"},
        
        # Автоматизация (41-45)
        {"name": "Telegram-бот для корпоративного портала", "description": "Интеграция с Active Directory, запрос справок, отпусков.", "price": 38000, "category": "Автоматизация", "dev": dev_ivan, "downloads": 178, "file_size": 0.9, "version": "2.3.0"},
        {"name": "RPA-робот для Excel", "description": "Автоматическая обработка Excel-отчетов.", "price": 29000, "category": "Автоматизация", "dev": dev_alexey, "downloads": 234, "file_size": 1.2, "version": "1.2.0"},
        {"name": "Автоматическая рассылка отчетов", "description": "Отправка отчетов по email и Telegram по расписанию.", "price": 22000, "category": "Автоматизация", "dev": dev_maria, "downloads": 312, "file_size": 0.7, "version": "1.5.0"},
        {"name": "Workflow-движок на Camunda", "description": "BPMN 2.0, согласование заявок, маршрутизация.", "price": 120000, "category": "Автоматизация", "dev": dev_maria, "downloads": 45, "file_size": 12.3, "version": "0.9.5"},
        {"name": "Чат-бот для сайта (AI)", "description": "ИИ-бот для ответов на вопросы клиентов.", "price": 49000, "category": "Автоматизация", "dev": dev_alexey, "downloads": 89, "file_size": 2.8, "version": "1.0.0"},
        
        # Маркетинг (46-50)
        {"name": "Email-рассылка через Unisender", "description": "Автоматические триггерные рассылки.", "price": 25000, "category": "Маркетинг", "dev": dev_elena, "downloads": 156, "file_size": 1.1, "version": "1.3.0"},
        {"name": "Сегментация клиентов (RFM)", "description": "RFM-анализ, сегментация клиентской базы.", "price": 32000, "category": "Маркетинг", "dev": dev_maria, "downloads": 203, "file_size": 1.5, "version": "1.2.0"},
        {"name": "Автоворонка для Telegram", "description": "Создание цепочек сообщений, рассылок, опросов.", "price": 28000, "category": "Маркетинг", "dev": dev_ivan, "downloads": 234, "file_size": 0.8, "version": "1.4.0"},
        {"name": "Сбор email-адресов с сайта", "description": "Виджеты, popup, интеграция с CRM.", "price": 18000, "category": "Маркетинг", "dev": dev_alexey, "downloads": 312, "file_size": 0.5, "version": "2.0.0"},
        {"name": "Анализ конкурентов в соцсетях", "description": "Мониторинг активности конкурентов в VK, Telegram.", "price": 35000, "category": "Маркетинг", "dev": dev_elena, "downloads": 145, "file_size": 1.8, "version": "1.1.0"},
    ]
        
        for p_data in products_data:
            product = models.Product(
                name=p_data["name"],
                description=p_data["description"],
                price=p_data["price"],
                category=p_data["category"],
                developer_id=p_data["developer"].id,
                download_url=f"https://example.com/download/{p_data['name'].lower().replace(' ', '_')}",
                file_size=p_data["file_size"],
                version=p_data["version"],
                downloads_count=p_data["downloads"],
                is_active=True
            )
            db.add(product)
        
        db.commit()
        print(f"✅ Добавлено {len(products_data)} продуктов")
        
        print("=" * 60)
        print("✅ ИНИЦИАЛИЗАЦИЯ УСПЕШНО ЗАВЕРШЕНА")
        print("=" * 60)
        
        # Финальная статистика
        print(f"\n📊 Статистика базы данных:")
        print(f"   - Пользователей: {db.query(models.User).count()}")
        print(f"   - Категорий: {db.query(models.Category).count()}")
        print(f"   - Продуктов: {db.query(models.Product).count()}")
    else:
        print("Данные уже существуют, инициализация пропущена")
        
except Exception as e:
    print(f"❌ ОШИБКА: {e}")
    import traceback
    traceback.print_exc()
    db.rollback()
finally:
    db.close()

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
