# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime, Float, JSON, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# Таблица для связи многих ко многим (продукты в заказе)
order_items = Table(
    'order_items',
    Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id')),
    Column('product_id', Integer, ForeignKey('products.id')),
    Column('quantity', Integer, default=1),
    Column('price_at_time', Integer)
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String, nullable=True)
    role = Column(String, default="developer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    
    products = relationship("Product", back_populates="developer")
    orders = relationship("Order", back_populates="user")
    downloads = relationship("Download", back_populates="user")




class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Integer)  # в копейках/центах
    category = Column(String)
    developer_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    download_url = Column(String)
    file_size = Column(Float, nullable=True)  # размер в МБ
    version = Column(String, nullable=True)
    downloads_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)

    
    developer = relationship("User", back_populates="products")
    orders = relationship("Order", secondary=order_items, back_populates="products")
    downloads = relationship("Download", back_populates="product")
    
    def get_tags_list(self):
        """Возвращает список тегов"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")  # pending, paid, completed, cancelled
    total_amount = Column(Integer)  # общая сумма в копейках
    payment_method = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True, unique=True)
    
    user = relationship("User", back_populates="orders")
    products = relationship("Product", secondary=order_items, back_populates="orders")

class Download(Base):
    __tablename__ = "downloads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    downloaded_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    user = relationship("User", back_populates="downloads")
    product = relationship("Product", back_populates="downloads")

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    product_count = Column(Integer, default=0)