from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Literal
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
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    # ВАЖНО: здесь намеренно нет поля role.
    # Роль всегда выставляется сервером (см. routers/users.py -> register)
    # и меняется только через админский эндпоинт PUT /admin/users/{id}/role.
    # Максимум 72 символа — ограничение bcrypt.
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isalpha() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать и буквы, и цифры")
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None

class User(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class UserPublic(BaseModel):
    """Публичный профиль — без email и других приватных полей."""
    id: int
    username: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str

    class Config:
        from_attributes = True

# ===== Admin schemas =====
RoleName = Literal["user", "developer", "manager", "admin", "superuser"]

class RoleUpdate(BaseModel):
    new_role: RoleName

class AdminUserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[RoleName] = None
    is_active: Optional[bool] = None

class OrderStatusUpdate(BaseModel):
    status: Literal["pending", "paid", "completed", "cancelled"]

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
    # Публичная схема: товары видны всем, поэтому email разработчика не отдаём
    developer: Optional[UserPublic] = None
    
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
    user: Optional[User] = None
    
    class Config:
        from_attributes = True

# ===== Download schemas =====
class DownloadCreate(BaseModel):
    # ip_address/user_agent намеренно не принимаются от клиента —
    # сервер берёт их из самого запроса (иначе их можно подделать)
    product_id: int

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

# ===== Favorite schemas =====
class Favorite(BaseModel):
    id: int
    created_at: datetime
    product: Product

    class Config:
        from_attributes = True

# ===== AI search schemas =====
class AISearchRequest(BaseModel):
    query: str

class AISearchRecommendation(BaseModel):
    product: Product
    reason: str = ""

class AISearchResponse(BaseModel):
    message: str
    advice: List[str] = []
    recommendations: List[AISearchRecommendation] = []

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