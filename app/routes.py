from fastapi import APIRouter, HTTPException, Depends
from app.schemas import OrderCreate, OrderResponse, OrderItemCreate, OrderItemResponse
from app.database import get_db
from app import models
from typing import List
from sqlalchemy.orm import Session

router = APIRouter()

@router.get("/", response_model=List[OrderResponse])
def list_order(db: Session = Depends(get_db)):
    return db.query(models.Order).all()


@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # create Order instance
    db_order = models.Order(user_id=order.user_id)
    # create OrderItem instances
    db_order.items = [
        models.OrderItem(offer_id=item.offer_id, quantity=item.quantity)
        for item in order.items
    ]
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.get("/items", response_model=List[OrderItemResponse])
def list_order_items(db: Session = Depends(get_db)):
    return db.query(models.OrderItem).all()

@router.get("/items/{item_id}", response_model=OrderItemResponse)
def get_order_item(item_id: int, db: Session = Depends(get_db)):
    order_item = db.query(models.OrderItem).filter(models.OrderItem.id == item_id).first()

    if not order_item:
        raise HTTPException(status_code=404, detail="Order not found")

    return order_item

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order
