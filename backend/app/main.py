from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base, SessionLocal
from .routers import users, products, search, admin, orders, downloads
from . import models
import os
from .auth import get_password_hash
from datetime import datetime

# Создание таблиц в БД
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Marketplace PO API")

# Настройка CORS
# Получаем URL фронтенда из переменной окружения
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
# Для разработки можно разрешить несколько URL
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Локальная разработка
    "http://localhost:8000",   # Альтернативный dev порт
    FRONTEND_URL,              # URL на Render'е (придет из переменной)
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,  # Теперь массив, а не строка
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(users.router)
app.include_router(products.router)
app.include_router(search.router)
app.include_router(admin.router)      
app.include_router(orders.router)     
app.include_router(downloads.router)

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def root():
    return {"message": "Welcome to Marketplace PO API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
