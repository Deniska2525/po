from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ===== Auth schemas =====
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# ===== User schemas =====
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    role: str = "developer"
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# ===== Product schemas =====
class ProductBase(BaseModel):
    name: str
    description: str
    price: int
    category: str
    download_url: str
    file_size: Optional[float] = None
    version: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    is_active: Optional[bool] = None

class Product(ProductBase):
    id: int
    developer_id: int
    created_at: datetime
    updated_at: datetime
    downloads_count: int
    is_active: bool
    developer: Optional[User] = None
    
    class Config:
        from_attributes = True

# ===== Order schemas =====
class OrderItem(BaseModel):
    product_id: int
    quantity: int = 1
    price_at_time: int

class OrderCreate(BaseModel):
    items: List[OrderItem]
    payment_method: str

class Order(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: str
    total_amount: int
    payment_method: Optional[str]
    transaction_id: Optional[str]
    products: List[Product]
    
    class Config:
        from_attributes = True

# ===== Download schemas =====
class DownloadCreate(BaseModel):
    product_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class Download(BaseModel):
    id: int
    user_id: Optional[int]
    product_id: int
    downloaded_at: datetime
    product: Optional[Product]
    
    class Config:
        from_attributes = True

# ===== Category schemas =====
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    product_count: int
    
    class Config:
        from_attributes = True

# ===== Statistics schemas =====
class DashboardStats(BaseModel):
    total_users: int
    total_products: int
    total_orders: int
    total_downloads: int
    total_revenue: int
    recent_orders: List[Order] = []
    popular_products: List[Product] = []
    
    class Config:
        from_attributes = True

class RevenueStats(BaseModel):
    daily: List[dict] = []
    monthly: List[dict] = []
    yearly: List[dict] = []