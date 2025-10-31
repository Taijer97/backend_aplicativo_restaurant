from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List
from db.base import get_db
from models import reservation as models
from schemas import reservation as schemas

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("/", response_model=schemas.ReservationOut)
async def create_reservation(payload: schemas.ReservationIn, db: AsyncSession = Depends(get_db)):
    db_reservation = models.Reservation(**payload.dict())
    db.add(db_reservation)
    await db.commit()
    await db.refresh(db_reservation)
    return db_reservation

@router.get("/", response_model=List[schemas.ReservationOut])
async def get_reservations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Reservation))
    reservations = result.scalars().all()
    return reservations

@router.put("/{reservation_id}", response_model=schemas.ReservationOut)
async def update_reservation(reservation_id: int, payload: schemas.ReservationIn, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Reservation).where(models.Reservation.id == reservation_id))
    db_reservation = result.scalars().first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(db_reservation, key, value)
    await db.commit()
    await db.refresh(db_reservation)
    return db_reservation

@router.delete("/{reservation_id}")
async def delete_reservation(reservation_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Reservation).where(models.Reservation.id == reservation_id))
    db_reservation = result.scalars().first()
    if not db_reservation:
        raise HTTPException(status_code=404, detail="Reservation not found")
    await db.delete(db_reservation)
    await db.commit()
    return {"detail": "Reservation deleted"}
