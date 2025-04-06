from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.session import get_db
from app.models.models import User
from app.schemas.user import UserCreate

router = APIRouter(
    prefix="/auth",
    tags=["🔐 Аутентификация"],  # Русский тег со смайликом
    responses={404: {"description": "Не найдено"}}
)

@router.post(
    "/register",
    status_code=201,
    summary="📝 Регистрация нового пользователя",
    description="Создание нового аккаунта с email и паролем",
    response_description="Успешная регистрация"
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="❌ Этот email уже зарегистрирован"
        )
    
    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    
    return {
        "message": "✅ Пользователь успешно зарегистрирован",
        "user_id": new_user.id
    }

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post(
    "/token",
    summary="🔑 Вход в систему",
    description="Аутентификация по email и паролю",
    response_description="JWT токен доступа"
)
async def login(login_data: LoginRequest = Body(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="❌ Неверный email или пароль"
        )
    
    return {
        "access_token": create_access_token(data={"sub": user.email}),
        "token_type": "bearer",
        "message": "✅ Вход выполнен успешно"
    }