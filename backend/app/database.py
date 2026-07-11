import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URL обязательно берём из окружения — никаких секретов в коде.
# Локально задайте её в .env (см. .env.example) или в переменных окружения shell.
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL не задана. Установите переменную окружения DATABASE_URL "
        "(например: postgresql://user:password@host/dbname)"
    )

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
