from fastapi import FastAPI
from app.routers import auth, resources, booking, notifications
from app.db.session import engine
from app.models.models import Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="🏨 Система бронирования ресурсов",
    description="API для управления отелями, столиками и спортивными площадками",
    version="1.0",
    contact={
        "name": "Техподдержка",
        "email": "support@booking.ru",
    },
    openapi_tags=[
        {
            "name": "🔐 Аутентификация",
            "description": "Регистрация и вход в систему"
        },
        {
            "name": "🏨 Ресурсы",
            "description": "Управление отелями, столиками и площадками"
        },
        {
            "name": "📅 Бронирования",
            "description": "Создание и управление бронированиями"
        },
        {
            "name": "📢 Уведомления",
            "description": "Email и вебсокет уведомления"
        }
    ]
)

app.include_router(auth.router, prefix="/auth")
app.include_router(resources.router, prefix="/resources", )
app.include_router(booking.router, prefix="/bookings", )
app.include_router(notifications.router, prefix="/notifications",)

@app.get("/")
def read_root():
    return {"message": "Booking System API"}