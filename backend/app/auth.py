import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, schemas
from .database import get_db

# Конфигурация JWT
# SECRET_KEY обязательно берём из окружения. В проде переменная ДОЛЖНА быть задана,
# иначе токены можно подделать, зная секрет из публичного репозитория.
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if os.getenv("ENV", "development") == "production":
        raise RuntimeError("SECRET_KEY не задана в production-окружении!")
    # Только для локальной разработки — каждый рестарт будет новый ключ
    # (все выданные ранее токены станут невалидны, это нормально для дев-режима)
    SECRET_KEY = secrets.token_hex(32)
    print("⚠️  SECRET_KEY не задана, используется временный ключ для разработки")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Защита от перебора: после MAX_FAILED_LOGINS неудачных попыток аккаунт
# блокируется на LOCKOUT_MINUTES минут.
MAX_FAILED_LOGINS = 5
LOCKOUT_MINUTES = 15

# bcrypt — медленный адаптивный алгоритм, устойчивый к перебору при утечке БД.
# sha256_crypt оставлен в списке, чтобы старые хеши продолжали проверяться;
# deprecated="auto" помечает их устаревшими, и при входе пароль перехешируется
# в bcrypt (см. authenticate_user).
pwd_context = CryptContext(schemes=["bcrypt", "sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    """Проверяет пароль"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Хеширует пароль"""
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    """Аутентифицирует пользователя с учётом блокировки после неудачных попыток.

    Возвращает models.User при успехе, None при неверных кредах,
    и бросает HTTPException(423), если аккаунт временно заблокирован.
    """
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        # Выполняем фиктивную проверку, чтобы время ответа не выдавало,
        # существует ли пользователь (timing attack).
        pwd_context.dummy_verify()
        return None

    if user.locked_until and user.locked_until > datetime.utcnow():
        minutes_left = int((user.locked_until - datetime.utcnow()).total_seconds() // 60) + 1
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=f"Аккаунт временно заблокирован. Попробуйте через {minutes_left} мин.",
        )

    if not verify_password(password, user.hashed_password):
        user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
        if user.failed_login_attempts >= MAX_FAILED_LOGINS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            user.failed_login_attempts = 0
        db.commit()
        return None

    # Успешный вход: сброс счётчика, обновление last_login,
    # перехеширование пароля, если он в устаревшем формате (sha256_crypt -> bcrypt)
    user.failed_login_attempts = 0
    user.locked_until = None
    user.last_login = datetime.utcnow()
    if pwd_context.needs_update(user.hashed_password):
        user.hashed_password = pwd_context.hash(password)
    db.commit()
    return user


# ===== Refresh-токены =====
# Сырой токен уходит клиенту в httpOnly-cookie, в БД хранится только его
# SHA-256 (утечка БД не даёт использовать токены). Отзыв — при logout.

def _hash_refresh_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()

def create_refresh_token(db: Session, user: models.User) -> str:
    raw_token = secrets.token_urlsafe(48)
    db.add(models.RefreshToken(
        user_id=user.id,
        token_hash=_hash_refresh_token(raw_token),
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
    ))
    db.commit()
    return raw_token

def get_user_by_refresh_token(db: Session, raw_token: str) -> Optional[models.User]:
    token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token_hash == _hash_refresh_token(raw_token)
    ).first()
    if not token or token.revoked or token.expires_at < datetime.utcnow():
        return None
    return db.query(models.User).filter(models.User.id == token.user_id).first()

def revoke_refresh_token(db: Session, raw_token: str) -> None:
    token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token_hash == _hash_refresh_token(raw_token)
    ).first()
    if token:
        token.revoked = True
        db.commit()

def revoke_all_user_tokens(db: Session, user_id: int) -> None:
    """Отзывает все refresh-токены пользователя (смена пароля, блокировка)."""
    db.query(models.RefreshToken).filter(
        models.RefreshToken.user_id == user_id,
        models.RefreshToken.revoked == False,  # noqa: E712
    ).update({"revoked": True})
    db.commit()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создает JWT токен"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Получает текущего пользователя по токену"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    """Проверяет, активен ли пользователь"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def check_superuser(current_user: models.User = Depends(get_current_active_user)):
    """Проверяет, является ли пользователь суперпользователем"""
    if current_user.role != "superuser":
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user