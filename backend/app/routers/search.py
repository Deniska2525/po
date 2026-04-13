from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/products", response_model=List[schemas.Product])
def search_products(
    q: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    db: Session = Depends(get_db)
):
    query = db.query(models.Product).filter(models.Product.is_active == True)
    
    if q:
        # Регистронезависимый поиск через ILIKE (для PostgreSQL) или LIKE (для SQLite)
        search_term = f"%{q}%"
        search_filter = or_(
            models.Product.name.ilike(search_term),  # ilike = регистронезависимый
            models.Product.description.ilike(search_term),
            models.Product.category.ilike(search_term)
        )
        query = query.filter(search_filter)
    
    if category:
        query = query.filter(models.Product.category == category)
    
    if min_price is not None:
        query = query.filter(models.Product.price >= min_price)
    
    if max_price is not None:
        query = query.filter(models.Product.price <= max_price)
    
    return query.all()

@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(models.Product.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]
