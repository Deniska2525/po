from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/", response_model=schemas.Product)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    if current_user.role not in ["developer", "superuser"]:
        raise HTTPException(status_code=403, detail="Only developers can create products")
    
    db_product = models.Product(**product.dict(), developer_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@router.get("/", response_model=List[schemas.Product])
def get_products(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return db.query(models.Product).offset(skip).limit(limit).all()

@router.get("/my", response_model=List[schemas.Product])
def get_my_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Поиск продуктов разработчика с сортировкой по убыванию ID
    return db.query(models.Product).filter(
        models.Product.developer_id == current_user.id
    ).order_by(models.Product.id.desc()).all()

@router.get("/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int,
    product_update: schemas.ProductCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.developer_id != current_user.id and current_user.role != "superuser":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    for key, value in product_update.dict().items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product.developer_id != current_user.id and current_user.role != "superuser":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
