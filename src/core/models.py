from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Table, Boolean
from sqlalchemy.orm import relationship
from src.core.database import Base

# Table d'association pour les produits similaires
similar_products = Table(
    'similar_products',
    Base.metadata,
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True),
    Column('similar_product_id', Integer, ForeignKey('products.id'), primary_key=True)
)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    material = Column(String)
    color = Column(String)
    pattern = Column(String)
    dimensions = Column(String)
    stock_quantity = Column(Integer)
    image_urls = Column(String)  # JSON array
    embedding = Column(String)  # Vector embedding for similarity search
    similar_products = relationship(
        'Product',
        secondary=similar_products,
        primaryjoin=(id == similar_products.c.product_id),
        secondaryjoin=(id == similar_products.c.similar_product_id),
        lazy='dynamic'
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    whatsapp_id = Column(String, unique=True, index=True)
    name = Column(String)
    preferences = Column(String)  # JSON
    consent_marketing = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    orders = relationship("Order", back_populates="customer")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    status = Column(String)  # pending, confirmed, paid, shipped, delivered
    total_amount = Column(Float)
    payment_status = Column(String)
    shipping_address = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    customer = relationship("Customer", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    price_at_time = Column(Float)
    
    order = relationship("Order", back_populates="items")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    interaction_type = Column(String)  # message, image, voice, purchase
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    metadata = Column(String)  # JSON