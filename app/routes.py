from fastapi import APIRouter, HTTPException, Depends, Header
from app.schemas import OrderCreate, OrderResponse, OrderItemCreate, OrderItemResponse, OrderPaymentUpdate
from app.database import get_db_session as get_db
from app import models
from typing import List, Optional
from sqlalchemy.orm import Session
from app.grpc import payment_client

router = APIRouter()

def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> str:
    """Extract tenant ID from header, default to public"""
    return x_tenant_id or "public"

def get_db_with_schema(tenant_id: str = Depends(get_tenant_id)):
    """Dependency to inject DB session with dynamic schema from X-Tenant-ID header"""
    return get_db(schema=tenant_id)

@router.get("/", response_model=List[OrderResponse])
def list_order(db: Session = Depends(get_db_with_schema)):
    return db.query(models.Order).all()

@router.post("/", response_model=OrderResponse, status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db_with_schema), tenant_id: str = Depends(get_tenant_id)):
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

    # call payment service with grpc and create payment
    payment = payment_client.create_payment(
        order_id=db_order.id,
        user_id=order.user_id,
        amount=order.amount,
        tenant_id=tenant_id
    )

    # store payment to DB
    db_order.payment_id = payment.payment_id
    db.commit()

    # return information to frontend
    return db_order

@router.get("/items", response_model=List[OrderItemResponse])
def list_order_items(db: Session = Depends(get_db_with_schema)):
    return db.query(models.OrderItem).all()

@router.get("/items/{item_id}", response_model=OrderItemResponse)
def get_order_item(item_id: int, db: Session = Depends(get_db_with_schema)):
    order_item = db.query(models.OrderItem).filter(models.OrderItem.id == item_id).first()

    if not order_item:
        raise HTTPException(status_code=404, detail="Order not found")

    return order_item

@router.patch("/{order_id}/payment", response_model=OrderResponse)
def update_order_payment(order_id: int, update: OrderPaymentUpdate, db: Session = Depends(get_db_with_schema)):
    # Fetch the order
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Update payment info
    order.payment_id = update.payment_id
    order.payment_status = update.payment_status
    
    db.commit()
    db.refresh(order)
    
    return order

@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db_with_schema)):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    return order
