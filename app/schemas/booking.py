from datetime import datetime
from pydantic import BaseModel

class BookingBase(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    user_id: int
    status: str

    class Config:
        from_attributes = True