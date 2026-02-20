# study_room/services/reservation_service.py

from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from study_room.repositories.reservation_repository import reservation_repository
from study_room.services.study_room_service import study_room_service
from study_room.models.reservation import Reservation
from study_room.models.user import User
from study_room.schemas.reservation import ReservationCreate, ReservationResponse, MyReservationsResponse


class ReservationService:
    async def create_reservation(self, db: AsyncSession, data: ReservationCreate, current_user: User) -> ReservationResponse:
        room = await study_room_service.read_room_by_id(db, data.room_id)

        today = date.today()
        if data.reservation_date < today or data.reservation_date > today + timedelta(days=7):
            raise HTTPException(status_code=400, detail="예약은 오늘부터 7일 이내의 날짜만 가능합니다.")

        user_daily_count = await reservation_repository.count_by_user_and_date(db, current_user.id, data.reservation_date)
        if user_daily_count >= 2:
            raise HTTPException(status_code=400, detail="하루에 최대 2시간(2회)까지만 예약 가능합니다.")

        try:
            start_time = datetime.strptime(data.start_time, "%H:%M").time()
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="시간 형식이 올바르지 않습니다. (예: 14:00)")

        end_dt = datetime.combine(data.reservation_date, start_time) + timedelta(hours=1)
        end_time = end_dt.time()

        if start_time < room.open_time or end_time > room.close_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"운영 시간({room.open_time.strftime('%H:%M')} ~ {room.close_time.strftime('%H:%M')}) 내에서만 예약 가능합니다.",
            )
        
        if await reservation_repository.find_user_conflict(db, current_user.id, data.reservation_date, start_time):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="해당 시간에 이미 다른 방 예약이 있습니다.",
            )
        
        if await reservation_repository.find_conflict(db, data.room_id, data.reservation_date, start_time):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 예약된 시간입니다.")

        new_reservation = Reservation(
            user_id=current_user.id,
            room_id=room.room_id,
            reservation_date=data.reservation_date,
            start_time=start_time,
            end_time=end_time,
            status="예약확정",
        )

        try:
            async with db.begin():
                await reservation_repository.save(db, new_reservation)
            await db.refresh(new_reservation)
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="예약 저장 중 오류가 발생했습니다.")

        return ReservationResponse(
            id=new_reservation.id,
            room_name=room.name,
            reservation_date=new_reservation.reservation_date,
            start_time=new_reservation.start_time.strftime("%H:%M"),
            end_time=new_reservation.end_time.strftime("%H:%M"),
            status=new_reservation.status,
        )

    async def read_my_reservations(self, db: AsyncSession, current_user: User) -> MyReservationsResponse:
        reservations = await reservation_repository.find_by_user_id(db, current_user.id)

        now = datetime.now()
        today = now.date()
        current_time = now.time()

        # 조회 시점에 상태 업데이트
        async with db.begin():
            for r in reservations:
                if r.status == "예약확정":
                    ended = (
                        r.reservation_date < today or
                        (r.reservation_date == today and r.end_time <= current_time)
                    )
                    if ended:
                        r.status = "이용완료"

        items = [
            ReservationResponse(
                id=r.id,
                room_name=r.room.name,
                reservation_date=r.reservation_date,
                start_time=r.start_time.strftime("%H:%M"),
                end_time=r.end_time.strftime("%H:%M"),
                status=r.status,
            )
            for r in reservations
        ]
        return MyReservationsResponse(reservations=items)

    async def cancel_reservation(self, db: AsyncSession, reservation_id: int, current_user: User):
        reservation = await reservation_repository.find_by_id(db, reservation_id)

        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 예약입니다.")
        if reservation.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인 예약만 취소할 수 있습니다.")
        if reservation.status != "예약확정":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="취소 가능한 예약이 아닙니다.")

        reservation_datetime = datetime.combine(reservation.reservation_date, reservation.start_time)
        if datetime.now() >= reservation_datetime - timedelta(hours=1):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="예약 취소는 이용 시간 1시간 전까지만 가능합니다.")

        try:
            async with db.begin():
                reservation.status = "취소"
        except Exception:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="취소 처리 중 오류가 발생했습니다.")


reservation_service = ReservationService()