import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from .. import models, schemas, auth
from ..database import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])

# Проверка прав администратора
def check_admin(current_user: models.User = Depends(auth.get_current_active_user)):
    if current_user.role not in ["superuser", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ============== СТАТИСТИКА ==============

@router.get("/dashboard", response_model=schemas.DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Получить статистику для дашборда"""
    try:
        # Основные метрики
        total_users = db.query(models.User).count()
        total_products = db.query(models.Product).count()
        total_orders = db.query(models.Order).count()
        total_downloads = db.query(models.Download).count()
        total_revenue = db.query(func.sum(models.Order.total_amount)).filter(
            models.Order.status == "completed"
        ).scalar() or 0
        
        # Последние заказы
        recent_orders = db.query(models.Order).order_by(
            models.Order.created_at.desc()
        ).limit(10).all()
        
        # Популярные продукты
        popular_products = db.query(models.Product).order_by(
            models.Product.downloads_count.desc()
        ).limit(10).all()
        
        return {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_downloads": total_downloads,
            "total_revenue": total_revenue,
            "recent_orders": recent_orders,
            "popular_products": popular_products
        }
    except Exception:
        logger.exception("Error in dashboard stats")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/revenue", response_model=schemas.RevenueStats)
def get_revenue_stats(
    period: str = Query("month", pattern="^(day|month|year)$"),
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Получить статистику по выручке"""
    try:
        now = datetime.utcnow()
        
        if period == "day":
            start_date = now - timedelta(days=30)
            # Для SQLite используем strftime вместо date_trunc
            results = db.query(
                func.strftime('%Y-%m-%d', models.Order.created_at).label('date'),
                func.sum(models.Order.total_amount).label('revenue')
            ).filter(
                models.Order.created_at >= start_date,
                models.Order.status == "completed"
            ).group_by('date').all()
            return {"daily": [{"date": r.date, "revenue": r.revenue} for r in results], "monthly": [], "yearly": []}
            
        elif period == "month":
            start_date = now - timedelta(days=365)
            results = db.query(
                func.strftime('%Y-%m', models.Order.created_at).label('date'),
                func.sum(models.Order.total_amount).label('revenue')
            ).filter(
                models.Order.created_at >= start_date,
                models.Order.status == "completed"
            ).group_by('date').all()
            return {"daily": [], "monthly": [{"date": r.date, "revenue": r.revenue} for r in results], "yearly": []}
            
        else:  # year
            start_date = now - timedelta(days=365*3)
            results = db.query(
                func.strftime('%Y', models.Order.created_at).label('date'),
                func.sum(models.Order.total_amount).label('revenue')
            ).filter(
                models.Order.created_at >= start_date,
                models.Order.status == "completed"
            ).group_by('date').all()
            return {"daily": [], "monthly": [], "yearly": [{"date": r.date, "revenue": r.revenue} for r in results]}
            
    except Exception:
        logger.exception("Error in revenue stats")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============== УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ==============

@router.get("/users", response_model=List[schemas.User])
def get_all_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Получить всех пользователей с фильтрацией"""
    try:
        query = db.query(models.User)
        
        if role:
            query = query.filter(models.User.role == role)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (models.User.username.ilike(search_filter)) |
                (models.User.email.ilike(search_filter)) |
                (models.User.full_name.ilike(search_filter))
            )
        
        # Сортировка по id (новые сначала)
        query = query.order_by(models.User.id.desc())
        
        # Пагинация
        users = query.offset(skip).limit(limit).all()
        
        return users
    except Exception:
        logger.exception("Error getting users")
        raise HTTPException(status_code=500, detail="Internal server error")

def _check_role_escalation(admin: models.User, new_role: str) -> None:
    """Назначать роли admin/superuser может только superuser —
    иначе обычный админ мог бы создать себе второго суперпользователя."""
    if new_role in ("admin", "superuser") and admin.role != "superuser":
        raise HTTPException(status_code=403, detail="Only superuser can grant admin roles")

@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role_data: schemas.RoleUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Обновить роль пользователя"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Не даем понизить суперпользователя
    if user.role == "superuser" and admin.role != "superuser":
        raise HTTPException(status_code=403, detail="Cannot modify superuser")

    _check_role_escalation(admin, role_data.new_role)

    user.role = role_data.new_role
    db.commit()

    return {"message": f"User role updated to {role_data.new_role}"}

@router.put("/users/{user_id}")
def update_user_admin(
    user_id: int,
    user_data: schemas.AdminUserUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Обновить данные пользователя (имя, email, роль, статус)"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "superuser" and admin.role != "superuser":
        raise HTTPException(status_code=403, detail="Cannot modify superuser")

    updates = user_data.dict(exclude_unset=True)
    if "role" in updates:
        _check_role_escalation(admin, updates["role"])

    for key, value in updates.items():
        setattr(user, key, value)

    # При деактивации отзываем все сессии пользователя
    if updates.get("is_active") is False:
        auth.revoke_all_user_tokens(db, user.id)

    db.commit()
    db.refresh(user)
    return user

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Удалить пользователя"""
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Не даем удалить суперпользователя
        if user.role == "superuser":
            raise HTTPException(status_code=403, detail="Cannot delete superuser")
        
        # Не даем удалить самого себя
        if user.id == admin.id:
            raise HTTPException(status_code=400, detail="Cannot delete yourself")
        
        db.delete(user)
        db.commit()
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error deleting user")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============== УПРАВЛЕНИЕ ПРОДУКТАМИ ==============

@router.get("/products", response_model=List[schemas.Product])
def get_all_products_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Получить все продукты (для админа)"""
    try:
        query = db.query(models.Product)
        
        if not include_inactive:
            query = query.filter(models.Product.is_active == True)
        
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                (models.Product.name.ilike(search_filter)) |
                (models.Product.description.ilike(search_filter))
            )
        
        query = query.order_by(models.Product.id.desc())
        products = query.offset(skip).limit(limit).all()
        
        return products
    except Exception:
        logger.exception("Error getting products")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/products/{product_id}/toggle")
def toggle_product_status(
    product_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Включить/выключить продукт"""
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        product.is_active = not product.is_active
        db.commit()
        
        return {"message": f"Product status changed to {product.is_active}"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error toggling product")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/products/{product_id}")
def delete_product_admin(
    product_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Удалить любой продукт (доступно админу/суперпользователю, в отличие
    от DELETE /products/{id}, который разрешён только автору продукта)"""
    try:
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        db.delete(product)
        db.commit()
        return {"message": "Product deleted successfully"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error deleting product")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============== УПРАВЛЕНИЕ КАТЕГОРИЯМИ ==============

@router.post("/categories", response_model=schemas.Category)
def create_category(
    category: schemas.CategoryCreate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Создать категорию"""
    try:
        # Проверяем, существует ли уже такая категория
        existing = db.query(models.Category).filter(
            models.Category.name == category.name
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Category already exists")
        
        db_category = models.Category(**category.dict())
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error creating category")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/categories", response_model=List[schemas.Category])
def get_categories_admin(
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Получить все категории (для админа)"""
    try:
        categories = db.query(models.Category).all()
        return categories
    except Exception:
        logger.exception("Error getting categories")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Удалить категорию"""
    try:
        category = db.query(models.Category).filter(models.Category.id == category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        
        # Проверяем, есть ли продукты в этой категории
        products_count = db.query(models.Product).filter(
            models.Product.category == category.name
        ).count()
        
        if products_count > 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot delete category with {products_count} products"
            )
        
        db.delete(category)
        db.commit()
        
        return {"message": "Category deleted successfully"}
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error deleting category")
        raise HTTPException(status_code=500, detail="Internal server error")

# ============== УПРАВЛЕНИЕ ЗАКАЗАМИ ==============

@router.get("/orders", response_model=List[schemas.Order])
def get_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Получить все заказы"""
    try:
        query = db.query(models.Order)
        
        if status:
            query = query.filter(models.Order.status == status)
        
        query = query.order_by(models.Order.created_at.desc())
        orders = query.offset(skip).limit(limit).all()
        
        return orders
    except Exception:
        logger.exception("Error getting orders")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status_data: schemas.OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: models.User = Depends(check_admin)
):
    """Обновить статус заказа"""
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order.status = status_data.status
    db.commit()

    return {"message": f"Order status updated to {status_data.status}"}
