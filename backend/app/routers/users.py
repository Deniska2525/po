import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from typing import List
from datetime import timedelta
from .. import models, schemas, auth
from ..database import get_db
from ..rate_limit import limiter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", tags=["users"])

# Cookie с refresh-токеном: httpOnly (недоступна из JS — защита от XSS),
# secure в проде (только по HTTPS), samesite=lax (защита от CSRF).
REFRESH_COOKIE_NAME = "refresh_token"
_COOKIE_SECURE = os.getenv("ENV", "development") == "production"


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        secure=_COOKIE_SECURE,
        samesite="lax",
        max_age=auth.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/users",
    )


@router.post("/register", response_model=schemas.User)
@limiter.limit("10/hour")
def register(request: Request, user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Проверка существования пользователя
    db_user = db.query(models.User).filter(
        (models.User.username == user.username) | (models.User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Создание нового пользователя.
    # role жёстко фиксируем как "user" — клиент не может задать себе роль
    # при регистрации (иначе можно было бы зарегистрироваться сразу админом).
    # Повысить роль может только администратор через /admin/users/{id}/role.
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role="user"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")
def login(request: Request, response: Response, login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = auth.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires
    )
    _set_refresh_cookie(response, auth.create_refresh_token(db, user))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/refresh", response_model=schemas.Token)
@limiter.limit("30/minute")
def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
    """Обменивает refresh-токен из httpOnly cookie на новый access-токен.

    Ротация: старый refresh-токен отзывается, выдаётся новый (украденный
    токен можно использовать максимум один раз).
    """
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw_token:
        raise HTTPException(status_code=401, detail="No refresh token")

    user = auth.get_user_by_refresh_token(db, raw_token)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    auth.revoke_refresh_token(db, raw_token)
    _set_refresh_cookie(response, auth.create_refresh_token(db, user))

    access_token = auth.create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """Отзывает refresh-токен и удаляет cookie."""
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_token:
        auth.revoke_refresh_token(db, raw_token)
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/users")
    return {"message": "Logged out"}


@router.get("/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(auth.get_current_active_user)):
    """Получить данные текущего пользователя"""
    return current_user


@router.put("/me", response_model=schemas.User)
def update_user(
    user_update: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """Обновить данные текущего пользователя"""
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, key, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/developers", response_model=List[schemas.UserPublic])
def get_developers(db: Session = Depends(get_db)):
    """Получить всех разработчиков (публичный профиль, без email)"""
    return db.query(models.User).filter(models.User.role == "developer").all()
