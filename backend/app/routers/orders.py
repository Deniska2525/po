from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import stripe  # для платежей (опционально)
from .. import models, schemas, auth
from ..database import get_db
import uuid

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=schemas.Order)
def create_order(
    order_data: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    # Проверяем все продукты
    total_amount = 0
    products = []
    
    for item in order_data.items:
        product = db.query(models.Product).filter(
            models.Product.id == item.product_id,
            models.Product.is_active == True
        ).first()
        
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        
        products.append(product)
        total_amount += product.price * item.quantity
    
    # Создаем заказ
    order = models.Order(
        user_id=current_user.id,
        status="pending",
        total_amount=total_amount,
        payment_method=order_data.payment_method,
        transaction_id=str(uuid.uuid4())
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Добавляем продукты в заказ (через association table)
    for product in products:
        order.products.append(product)
    
    db.commit()
    
    return order

@router.get("/", response_model=List[schemas.Order])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    return db.query(models.Order).filter(
        models.Order.user_id == current_user.id
    ).order_by(models.Order.created_at.desc()).all()

@router.get("/{order_id}", response_model=schemas.Order)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != current_user.id and current_user.role not in ["admin", "superuser"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return order

@router.post("/{order_id}/pay")
def pay_order(
    order_id: int,
    payment_token: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.status != "pending":
        raise HTTPException(status_code=400, detail="Order already processed")
    
    # Здесь интеграция с платежной системой
    # Например, Stripe:
    try:
        # charge = stripe.Charge.create(
        #     amount=order.total_amount,
        #     currency="rub",
        #     source=payment_token,
        #     description=f"Order #{order.id}"
        # )
        
        # Имитация успешной оплаты
        order.status = "completed"
        order.transaction_id = f"txn_{uuid.uuid4()}"
        db.commit()
        
        return {"message": "Payment successful", "order_id": order.id}
    except Exception as e:
        order.status = "failed"
        db.commit()
        raise HTTPException(status_code=400, detail=str(e))