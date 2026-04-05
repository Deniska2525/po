from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import engine, Base
from .routers import users, products, search, admin, orders, downloads
from . import models
import os
import subprocess

app = FastAPI(title="Marketplace PO API")

@app.on_event("startup")
def startup_event():
    """Запускается при старте контейнера, когда DATABASE_URL уже задана"""
    print("=" * 60)
    print("ЗАПУСК ИНИЦИАЛИЗАЦИИ БАЗЫ ДАННЫХ")
    print(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'не задана')[:50]}...")
    print("=" * 60)
    
    # Запускаем скрипт инициализации
    result = subprocess.run(
        ["python", "init_db.py"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(__file__)
    )

FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

Base.metadata.create_all(bind=engine)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        FRONTEND_URL,  # Сюда подставится URL из Render
    ],
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
