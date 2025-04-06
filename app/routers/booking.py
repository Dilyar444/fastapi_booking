from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.db.session import get_db
from app.schemas.booking import Booking, BookingCreate
from app.models.models import Booking as DBBooking, Resource, User
from app.core.security import get_current_user

router = APIRouter(tags=["📅 Бронирования"],
responses={400: {"description": "❌ Ошибка бронирования"}}
)

@router.post("/", response_model=Booking)
def create_booking(
    booking: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if resource exists
    resource = db.query(Resource).filter(Resource.id == booking.resource_id).first()
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Check availability
    conflicting_booking = db.query(DBBooking).filter(
        DBBooking.resource_id == booking.resource_id,
        DBBooking.start_time < booking.end_time,
        DBBooking.end_time > booking.start_time
    ).first()
    
    if conflicting_booking:
        raise HTTPException(
            status_code=400,
            detail="Resource already booked for this time period"
        )
    
    # Create booking
    db_booking = DBBooking(
        user_id=current_user.id,
        resource_id=booking.resource_id,
        start_time=booking.start_time,
        end_time=booking.end_time
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    
    # Here you would add notification logic (email/websocket)
    print(f"Booking created for {current_user.email}")  # Replace with actual notification
    
    return db_booking

@router.get("/", response_model=List[Booking])
def read_bookings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    bookings = db.query(DBBooking).offset(skip).limit(limit).all()
    return bookings

@router.get("/{booking_id}", response_model=Booking)
def read_booking(
    booking_id: int,
    db: Session = Depends(get_db)
):
    booking = db.query(DBBooking).filter(DBBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking

@router.delete("/{booking_id}")
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(DBBooking).filter(DBBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Only allow owner of booking or resource owner to delete
    if booking.user_id != current_user.id and booking.resource.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Not authorized to delete this booking"
        )
    
    db.delete(booking)
    db.commit()
    return {"message": "Booking deleted successfully"}