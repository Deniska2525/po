"""
Расширение каталога: генерирует ~300 дополнительных товаров для разнообразия
ассортимента (демо-данные).

Как и schema_sync.py — запускается автоматически при каждом старте
приложения (см. main.py) и полностью идемпотентен:
  - каждый товар и категория проверяются по имени ПЕРЕД вставкой;
  - если товар/категория с таким именем уже есть — пропускаем;
  - никогда ничего не удаляет и не изменяет в существующих данных.
Поэтому безопасно гонять на каждом деплое/рестарте, в том числе в проде,
без Shell — то же самое решение, что и для авто-миграции колонок.

Генерация детерминирована (random.seed фиксирован), поэтому при каждом
перезапуске получается ровно один и тот же набор из ~300 названий —
это и делает проверку "уже существует по имени" надёжной.
"""
import random
from datetime import datetime
from sqlalchemy.orm import Session
from . import models
from .auth import get_password_hash

random.seed(42)

NEW_CATEGORIES = [
    ("HR и рекрутинг", "Подбор персонала, онбординг, кадровый учёт", "🧑‍💼"),
    ("Юридические сервисы", "Договоры, юридический due diligence, комплаенс", "⚖️"),
    ("Управление проектами", "Таск-трекеры, канбан, планирование ресурсов", "🗂️"),
    ("Веб- и мобильная разработка", "No-code/low-code, конструкторы, SDK", "💻"),
    ("Клиентская поддержка", "Хелпдеск, тикет-системы, чат-боты поддержки", "🎧"),
    ("Электронная коммерция", "Витрины, платежи, управление заказами", "🛒"),
    ("Производство", "MES, планирование производства, контроль качества", "🏭"),
    ("Недвижимость и строительство", "Учёт объектов, BIM, сметы", "🏗️"),
    ("Образование", "LMS, онлайн-курсы, тестирование знаний", "🎓"),
    ("Медицина", "МИС, запись пациентов, телемедицина", "🏥"),
    ("IoT и устройства", "Мониторинг оборудования, датчики, телеметрия", "📡"),
    ("Управление персоналом", "Тайм-трекинг, оценка эффективности, KPI", "📋"),
]

SYSTEMS = [
    "1С", "Bitrix24", "AmoCRM", "SAP", "Salesforce", "HubSpot", "Telegram",
    "WhatsApp", "VK", "Ozon", "Wildberries", "Яндекс.Маркет", "СБИС", "Контур",
    "Directum", "ELMA365", "Jira", "Confluence", "Slack", "MS Teams",
    "МойСклад", "Тинькофф Бизнес", "СберБизнес", "ФНС", "Kubernetes", "Docker",
    "PostgreSQL", "ClickHouse", "Power BI", "Tableau", "Looker", "Google Workspace",
    "Zoom", "Miro", "Trello", "Asana", "Notion", "GitLab", "GitHub", "1С:УТ",
    "1С:ЗУП", "РЖД", "Почта России", "СДЭК", "Avito", "hh.ru", "Superjob",
]

TEMPLATES = [
    "Интеграция {system} с {system2}",
    "Модуль {system} для категории «{category}»",
    "Синхронизация {system} и {system2}",
    "Коннектор {system}",
    "Дашборд {system}",
    "Автоматизация процессов в {system}",
    "Бот для {system}",
    "Плагин {system}",
    "Шлюз данных {system}",
    "Генератор отчётов {system}",
    "API-клиент {system}",
    "Мониторинг {system}",
]

DESC_TEMPLATES = [
    "Готовое решение для быстрой интеграции с {system}. Настройка без программирования, поддержка актуальных версий API.",
    "Автоматизирует рутинные операции в {system}, экономит время команды и снижает число ошибок.",
    "Двусторонняя синхронизация данных между {system} и внутренними системами компании в реальном времени.",
    "Расширяет стандартный функционал {system} под задачи бизнеса, гибкая настройка правил и сценариев.",
    "Простое подключение к {system} через REST API, подробная документация и техподдержка.",
]


def _generate_products(existing_categories: list[str]) -> list[dict]:
    all_categories = existing_categories + [c[0] for c in NEW_CATEGORIES]
    seen_names = set()
    products = []

    while len(products) < 300:
        category = random.choice(all_categories)
        template = random.choice(TEMPLATES)
        system = random.choice(SYSTEMS)
        system2 = random.choice([s for s in SYSTEMS if s != system])
        name = template.format(system=system, system2=system2, category=category)
        if name in seen_names:
            continue
        seen_names.add(name)

        desc = random.choice(DESC_TEMPLATES).format(system=system)
        products.append(
            {
                "name": name,
                "description": desc,
                "price": random.choice([9000, 15000, 19000, 25000, 29000, 35000, 45000, 55000, 65000, 79000, 89000, 99000]),
                "category": category,
                "downloads_count": random.randint(3, 320),
                "file_size": round(random.uniform(0.5, 15.0), 1),
                "version": f"{random.randint(1, 4)}.{random.randint(0, 9)}.{random.randint(0, 9)}",
                "tags": ", ".join(random.sample([system, system2, category], k=2)),
            }
        )

    return products


def run(db: Session):
    # 1. Категории — добавляем недостающие
    for name, desc, icon in NEW_CATEGORIES:
        if not db.query(models.Category).filter(models.Category.name == name).first():
            db.add(models.Category(name=name, description=desc, icon=icon))
    db.commit()

    existing_categories = [c.name for c in db.query(models.Category).all()]
    if not existing_categories:
        existing_categories = [c[0] for c in NEW_CATEGORIES]

    # 2. Разработчик для новых товаров — берём случайных из уже существующих,
    # либо создаём одного служебного, если в базе вообще никого нет
    developers = db.query(models.User).filter(models.User.role.in_(["developer", "admin"])).all()
    if not developers:
        bot = models.User(
            username="catalog_bot",
            email="catalog-bot@example.com",
            hashed_password=get_password_hash("not-a-real-account"),
            full_name="Каталог (демо)",
            role="developer",
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.add(bot)
        db.commit()
        db.refresh(bot)
        developers = [bot]

    # 3. Товары — добавляем только те, которых ещё нет по имени
    existing_names = {p.name for p in db.query(models.Product.name).all()}
    to_add = [p for p in _generate_products(existing_categories) if p["name"] not in existing_names]

    if not to_add:
        return  # уже всё добавлено раньше, ничего делать не нужно

    print(f"🌱 [seed_extra] Добавляю {len(to_add)} новых товаров в каталог…")
    for i, p in enumerate(to_add):
        developer = developers[i % len(developers)]
        db.add(
            models.Product(
                name=p["name"],
                description=p["description"],
                price=p["price"],
                category=p["category"],
                developer_id=developer.id,
                download_url=f"https://example.com/download/{p['name'].lower().replace(' ', '_')}",
                file_size=p["file_size"],
                version=p["version"],
                downloads_count=p["downloads_count"],
                tags=p["tags"],
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
        )
    db.commit()
    print(f"✅ [seed_extra] Готово, товаров добавлено: {len(to_add)}")
