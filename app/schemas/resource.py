from pydantic import BaseModel
from app.models.models import ResourceType
from datetime import datetime
from app import schemas
from app.schemas.user import UserInDB 
from .booking import Booking as BookingSchema  
from typing import List
class ResourceBase(BaseModel):
    name: str
    type: ResourceType
    description: str | None = None

class ResourceCreate(ResourceBase):
    pass

class Resource(BaseModel):
    id: int
    name: str
    type: str
    description: str | None
    owner_id: int
    bookings: List[BookingSchema] = []

    class Config:
        from_attributes = True