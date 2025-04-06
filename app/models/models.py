from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import Enum as SQLEnum
from pydantic import ConfigDict
from sqlalchemy.orm import joinedload



class ResourceType(str, PyEnum):
    HOTEL = "hotel"
    OFFICE = "office"
    SPORTS_GROUND = "sports_ground"
    RESTAURANT_TABLE = "restaurant_table"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    
    # Обратные связи
    resources = relationship("Resource", back_populates="owner")
    bookings = relationship("Booking", back_populates="user")

class UserBase:
    email: str
    hashed_password: str

class UserInDB(UserBase):
    id: int
    is_active: bool
    
    model_config = ConfigDict(from_attributes=True)

class Resource(Base):
    __tablename__ = "resources"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(Enum(ResourceType))
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # Добавляем связь с бронированиями
    bookings = relationship("Booking", back_populates="resource")
    
    # Связь с владельцем
    owner = relationship("User", back_populates="resources")

class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    resource_id = Column(Integer, ForeignKey("resources.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(String, default="confirmed")
    
    # Двусторонние связи
    user = relationship("User", back_populates="bookings")
    resource = relationship("Resource", back_populates="bookings")
