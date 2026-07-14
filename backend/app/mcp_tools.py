"""
MCP-сервер маркетплейса.

Выставляет каталог товаров как MCP-инструменты, чтобы сторонние ИИ-агенты
(Claude Desktop, другие MCP-хосты) могли искать в нашем каталоге напрямую —
как в обычном подключаемом коннекторе, а не только через наш сайт.

Это отдельная от app/ai_search.py вещь:
  - app/ai_search.py — наш backend сам ходит в Claude API, чтобы обслужить
    поиск на нашей же главной странице.
  - mcp_tools.py (этот файл) — превращает наш каталог в инструмент, который
    МОГУТ вызывать чужие ИИ-агенты. Мы тут не вызываем никакой ИИ сами —
    только отдаём данные по протоколу MCP, вызывающая сторона сама решает,
    какую модель использовать.

Транспорт: Streamable HTTP, stateless (без долгоживущих сессий) — то, что
нужно для обычного веб-хостинга (в т.ч. бесплатный план Render), без вебсокетов
и sticky-сессий между инстансами.

Подключение из Claude.ai / Claude Desktop: добавить коннектор с URL
`https://<ваш-домен-бэкенда>/mcp`.
"""
from typing import Optional
from mcp.server.fastmcp import FastMCP
from .database import SessionLocal
from .product_search import filter_products

mcp = FastMCP(
    "marketplace-po",
    instructions=(
        "Маркетплейс программного обеспечения для бизнеса (интеграции, "
        "аналитика, CRM/ERP, автоматизация и т.д.). Используй search_products, "
        "чтобы найти товары под задачу пользователя, и list_categories, чтобы "
        "узнать, какие категории вообще есть в каталоге."
    ),
    stateless_http=True,
    json_response=True,
)


@mcp.tool()
def search_products(
    keywords: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
) -> list[dict]:
    """Ищет товары (ПО) в каталоге маркетплейса по ключевым словам, категории и цене.

    Все параметры необязательны. keywords ищет по названию и описанию товара.
    Цены — в рублях.
    """
    db = SessionLocal()
    try:
        products = filter_products(
            db, keywords=keywords, category=category, min_price=min_price, max_price=max_price
        )
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "category": p.category,
                "version": p.version,
            }
            for p in products
        ]
    finally:
        db.close()


@mcp.tool()
def list_categories() -> list[str]:
    """Возвращает список всех категорий товаров, доступных в каталоге."""
    from . import models

    db = SessionLocal()
    try:
        rows = db.query(models.Product.category).distinct().all()
        return [r[0] for r in rows if r[0]]
    finally:
        db.close()


@mcp.tool()
def get_product_details(product_id: int) -> dict:
    """Возвращает подробную информацию об одном товаре по его id."""
    from . import models

    db = SessionLocal()
    try:
        p = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not p:
            return {"error": f"Товар с id={product_id} не найден"}
        return {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "price": p.price,
            "category": p.category,
            "version": p.version,
            "downloads_count": p.downloads_count,
        }
    finally:
        db.close()
