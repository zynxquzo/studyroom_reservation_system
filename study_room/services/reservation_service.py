# study_room/services/reservation_service.py

import logging
from datetime import date, datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from study_room.exceptions import (
    AppException,
    BadRequestException,
    NotFoundException,
    ForbiddenException,
    DuplicateException,
)
from study_room.repositories.reservation_repository import reservation_repository
from study_room.services.study_room_service import study_room_service
from study_room.models.reservation import Reservation
from study_room.models.user import User
from study_room.schemas.reservation import ReservationCreate, ReservationResponse, MyReservationsResponse

logger = logging.getLogger(__name__)


class ReservationService:
    async def create_reservation(self, db: AsyncSession, data: ReservationCreate, current_user: User) -> ReservationResponse:
        room = await study_room_service.read_room_by_id(db, data.room_id)

        today = date.today()
        if data.reservation_date < today or data.reservation_date > today + timedelta(days=7):
            raise BadRequestException("예약은 오늘부터 7일 이내의 날짜만 가능합니다.")

        user_daily_count = await reservation_repository.count_by_user_and_date(db, current_user.id, data.reservation_date)
        if user_daily_count >= 2:
            raise BadRequestException("하루에 최대 2시간(2회)까지만 예약 가능합니다.")

        try:
            start_time = datetime.strptime(data.start_time, "%H:%M").time()
        except ValueError:
            raise BadRequestException("시간 형식이 올바르지 않습니다. (예: 14:00)")

        end_dt = datetime.combine(data.reservation_date, start_time) + timedelta(hours=1)
        end_time = end_dt.time()

        if start_time < room.open_time or end_time > room.close_time:
            raise BadRequestException(
                f"운영 시간({room.open_time.strftime('%H:%M')} ~ {room.close_time.strftime('%H:%M')}) 내에서만 예약 가능합니다."
            )

        if await reservation_repository.find_user_conflict(db, current_user.id, data.reservation_date, start_time):
            raise DuplicateException("해당 시간에 이미 다른 방 예약이 있습니다.")

        if await reservation_repository.find_conflict(db, data.room_id, data.reservation_date, start_time):
            raise DuplicateException("이미 예약된 시간입니다.")

        new_reservation = Reservation(
            user_id=current_user.id,
            room_id=room.room_id,
            reservation_date=data.reservation_date,
            start_time=start_time,
            end_time=end_time,
            status="예약확정",
        )

        try:
            await reservation_repository.save(db, new_reservation)
            await db.commit()
            await db.refresh(new_reservation)
        except Exception as e:
            logger.exception("예약 저장 중 오류: user_id=%s, room_id=%s", current_user.id, data.room_id)
            raise AppException("예약 저장 중 오류가 발생했습니다.") from e

        logger.info("예약 생성 완료: reservation_id=%s, user_id=%s, room_id=%s", new_reservation.id, current_user.id, data.room_id)
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

        # async with db.begin(): 를 제거합니다.
        updated = False
        for r in reservations:
            if r.status == "예약확정":
                ended = (
                    r.reservation_date < today or
                    (r.reservation_date == today and r.end_time <= current_time)
                )
                if ended:
                    r.status = "이용완료"
                    updated = True
        
        if updated:
            await db.commit() # 변경된 상태를 DB에 반영

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
            raise NotFoundException("존재하지 않는 예약입니다.")
        if reservation.user_id != current_user.id:
            logger.warning("예약 취소 권한 없음: user_id=%s, reservation_id=%s", current_user.id, reservation_id)
            raise ForbiddenException("본인 예약만 취소할 수 있습니다.")
        if reservation.status != "예약확정":
            raise BadRequestException("취소 가능한 예약이 아닙니다.")

        reservation_datetime = datetime.combine(reservation.reservation_date, reservation.start_time)
        if datetime.now() >= reservation_datetime - timedelta(hours=1):
            raise BadRequestException("예약 취소는 이용 시간 1시간 전까지만 가능합니다.")

        try:
            reservation.status = "취소"
            await db.commit()
        except Exception as e:
            logger.exception("취소 처리 중 오류: reservation_id=%s", reservation_id)
            raise AppException("취소 처리 중 오류가 발생했습니다.") from e

        logger.info("예약 취소 완료: reservation_id=%s, user_id=%s", reservation_id, current_user.id)


reservation_service = ReservationService()