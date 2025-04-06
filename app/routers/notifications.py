from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict
from sqlalchemy.orm import Session
import json
from app.core.security import get_current_user_ws
from app.db.session import get_db
from app.models.models import User
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.core.config import settings

# Initialize the router ONCE at the top
router = APIRouter(    tags=["📢 Уведомления"],
    responses={500: {"description": "❌ Ошибка отправки"}})

if not all([settings.EMAIL_USERNAME, settings.EMAIL_PASSWORD, settings.EMAIL_SERVER]):
    print("Warning: Email configuration is incomplete. Email notifications will be disabled.")

# Then modify your ConnectionConfig to handle missing values safely
conf = ConnectionConfig(
    MAIL_USERNAME=settings.EMAIL_USERNAME,
    MAIL_PASSWORD=settings.EMAIL_PASSWORD,
    MAIL_FROM=settings.EMAIL_FROM,
    MAIL_PORT=settings.EMAIL_PORT,
    MAIL_SERVER=settings.EMAIL_SERVER,
    MAIL_STARTTLS=True,  # Changed from MAIL_TLS
    MAIL_SSL_TLS=False,  # Changed from MAIL_SSL
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_email_notification(email: str, message: str):
    message = MessageSchema(
        subject="Booking Notification",
        recipients=[email],
        body=message,
        subtype="html"
    )
    fm = FastMail(conf)
    await fm.send_message(message)

@router.post("/email/{user_id}")
async def trigger_email_notification(
    user_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    message = "Your booking has been confirmed!"
    background_tasks.add_task(send_email_notification, user.email, message)
    return {"message": "Email notification queued"}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

manager = ConnectionManager()

@router.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: str,
    token: str
):
    user = await get_current_user_ws(token)
    if not user or str(user.id) != user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # You can handle incoming messages here if needed
    except WebSocketDisconnect:
        manager.disconnect(user_id)

@router.get("/test-notification/{user_id}")
async def test_notification(user_id: str):
    await manager.send_personal_message(
        json.dumps({"message": "Test notification", "type": "test"}),
        user_id
    )
    return {"message": "Notification sent"}