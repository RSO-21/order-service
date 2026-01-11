from sqlalchemy import Column, Integer, ForeignKey, Numeric
from app.database import Base

# app/models.py
from sqlalchemy import Column, Integer, DateTime, String, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base
import uuid

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), nullable=False)
    partner_id = Column(String(36), nullable=True)
    order_status = Column(String(30), nullable=False, default="pending")
    payment_status = Column(String(30), nullable=False, default="unpaid")
    payment_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    items = relationship("OrderItem", back_populates="order", cascade="all, delete")


class OrderItem(Base):
    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"))
    offer_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    order = relationship("Order", back_populates="items")

class OrderLookup(Base):
    __tablename__ = "order_lookup"
    __table_args__ = {"schema": "public"}

    external_id = Column(
        String(255),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        nullable=False
    )
    order_id = Column(Integer, nullable=False)
    tenant_id = Column(String(100), nullable=False)
    user_id = Column(String(36), nullable=False, index=True)
    
    total_amount = Column(Numeric(10, 2))
    order_status = Column(String(30))
    partner_id = Column(String(36), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
