# study_room/routers/reservation_router.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import get_db
from study_room.services.reservation_service import reservation_service
from study_room.schemas.reservation import ReservationCreate, ReservationResponse, MyReservationsResponse
from study_room.dependencies import get_current_user
from study_room.models.user import User

router = APIRouter(prefix="/reservations", tags=["Reservation"])


@router.post("", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """예약 생성"""
    return reservation_service.create_reservation(db, data, current_user)


@router.get("/my", response_model=MyReservationsResponse)
def read_my_reservations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """내 예약 목록 조회"""
    return reservation_service.read_my_reservations(db, current_user)


@router.delete("/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """예약 취소"""
    reservation_service.cancel_reservation(db, reservation_id, current_user)