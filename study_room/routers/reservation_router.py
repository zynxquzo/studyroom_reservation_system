# study_room/routers/reservation_router.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from async_database import get_async_db
from study_room.services.reservation_service import reservation_service
from study_room.schemas.reservation import ReservationCreate, ReservationResponse, MyReservationsResponse
from study_room.dependencies import get_current_user
from study_room.models.user import User

router = APIRouter(prefix="/reservations", tags=["Reservation"])


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def create_reservation(
    data: ReservationCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await reservation_service.create_reservation(db, data, current_user)


@router.get("/my", response_model=MyReservationsResponse)
async def read_my_reservations(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    return await reservation_service.read_my_reservations(db, current_user)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_reservation(
    reservation_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
):
    await reservation_service.cancel_reservation(db, reservation_id, current_user)