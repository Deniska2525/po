import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Используем переменную окружения или путь по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://marketplace_ix5t_user:4uROQjHkzUjXyfjtaj5IhVLuSBUfZ4xb@dpg-d7933r0gjchc73fcijug-a/marketplace_ix5t")

# Для PostgreSQL нужно добавить sslmode
if "postgresql" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    DATABASE_URL += "?sslmode=require"

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
