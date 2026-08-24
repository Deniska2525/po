"""
Общая логика фильтрации товаров каталога.

Используется в двух местах:
  - app/ai_search.py — ИИ-поиск на самом сайте (внешняя LLM вызывает это как
    "инструмент" через tool use / function calling в OpenAI-совместимом API)
  - app/mcp_tools.py — тот же самый поиск, но выставленный наружу как MCP-инструмент
    для сторонних ИИ-агентов (Claude Desktop и т.п.)

Вынесено в отдельный модуль, чтобы не дублировать SQL-фильтрацию в двух местах.
"""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from . import models


def filter_products(
    db: Session,
    keywords: Optional[str] = None,
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    limit: int = 20,
) -> list[models.Product]:
    query = db.query(models.Product).filter(models.Product.is_active == True)

    if keywords:
        term = f"%{keywords}%"
        query = query.filter(
            or_(
                models.Product.name.ilike(term),
                models.Product.description.ilike(term),
                models.Product.tags.ilike(term),
            )
        )

    if category:
        query = query.filter(models.Product.category.ilike(f"%{category}%"))

    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)

    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)

    return query.limit(limit).all()


def product_to_dict(p: models.Product) -> dict:
    """Компактное представление товара для передачи ИИ (экономим токены)."""
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": p.price,
        "category": p.category,
    }
