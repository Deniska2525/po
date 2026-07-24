from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/favorites", tags=["favorites"])


@router.get("/", response_model=List[schemas.Product])
def get_my_favorites(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Список избранных товаров текущего пользователя"""
    favorites = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id
    ).order_by(models.Favorite.created_at.desc()).all()
    return [f.product for f in favorites]


@router.post("/{product_id}", response_model=schemas.Product)
def add_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Добавить товар в избранное (идемпотентно)"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    existing = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.product_id == product_id
    ).first()

    if not existing:
        db.add(models.Favorite(user_id=current_user.id, product_id=product_id))
        db.commit()

    return product


@router.delete("/{product_id}")
def remove_favorite(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Убрать товар из избранного"""
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == current_user.id,
        models.Favorite.product_id == product_id
    ).first()

    if favorite:
        db.delete(favorite)
        db.commit()

    return {"message": "Removed from favorites"}
