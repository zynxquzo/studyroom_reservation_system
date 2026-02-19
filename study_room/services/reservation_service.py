from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from study_room.repositories.reservation_repository import reservation_repository
from study_room.services.study_room_service import study_room_service
from study_room.models.reservation import Reservation
from study_room.models.user import User
from study_room.schemas.reservation import ReservationCreate, ReservationResponse, MyReservationsResponse


class ReservationService:
    def create_reservation(self, db: Session, data: ReservationCreate, current_user: User) -> ReservationResponse:
        room = study_room_service.read_room_by_id(db, data.room_id)

    # 1. [추가] 생성 시점에서도 7일 제한 및 과거 날짜 체크
        today = date.today()
        if data.reservation_date < today or data.reservation_date > today + timedelta(days=7):
            raise HTTPException(
                status_code=400, 
                detail="예약은 오늘부터 7일 이내의 날짜만 가능합니다."
            )

        # 2. [추가] 하루 최대 2회(2시간) 제한 체크
        # repository에 count_by_user_and_date 메서드를 만들어야 함
        user_daily_count = reservation_repository.count_by_user_and_date(
            db, current_user.id, data.reservation_date
        )
        if user_daily_count >= 2:
            raise HTTPException(
                status_code=400, 
                detail="하루에 최대 2시간(2회)까지만 예약 가능합니다."
            )
        # 시간 파싱
        try:
            start_time = datetime.strptime(data.start_time, "%H:%M").time()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="시간 형식이 올바르지 않습니다. (예: 14:00)",
            )

        end_dt = datetime.combine(data.reservation_date, start_time) + timedelta(hours=1)
        end_time = end_dt.time()

        # 운영 시간 체크
        if start_time < room.open_time or end_time > room.close_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"운영 시간({room.open_time.strftime('%H:%M')} ~ {room.close_time.strftime('%H:%M')}) 내에서만 예약 가능합니다.",
            )

        # 중복 예약 체크 (트랜잭션 밖에서 조회)
        if reservation_repository.find_conflict(db, data.room_id, data.reservation_date, start_time):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="이미 예약된 시간입니다.",
            )

        new_reservation = Reservation(
            user_id=current_user.id,  # relationship(user=user) 대신 외래키 직접 지정이 더 명확할 때가 있습니다.
            room_id=room.room_id,
            reservation_date=data.reservation_date,
            start_time=start_time,
            end_time=end_time,
            status="예약확정",
        )

        try:
            reservation_repository.save(db, new_reservation)
            db.commit()      # 데이터베이스에 확정 반영
            db.refresh(new_reservation) # 생성된 ID 등을 다시 읽어옴
        except Exception as e:
            db.rollback()    # 에러 발생 시 되돌리기
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="예약 저장 중 오류가 발생했습니다."
            )

        return ReservationResponse(
            id=new_reservation.id,
            room_name=room.name,
            reservation_date=new_reservation.reservation_date,
            start_time=new_reservation.start_time.strftime("%H:%M"),
            end_time=new_reservation.end_time.strftime("%H:%M"),
            status=new_reservation.status,
        )

    def read_my_reservations(self, db: Session, current_user: User) -> MyReservationsResponse:
        reservations = reservation_repository.find_by_user_id(db, current_user.id)
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

    def cancel_reservation(self, db: Session, reservation_id: int, current_user: User):
        reservation = reservation_repository.find_by_id(db, reservation_id)

        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 예약입니다.")
        if reservation.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인 예약만 취소할 수 있습니다.")
        if reservation.status != "예약확정":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="취소 가능한 예약이 아닙니다.")

        # 이용 1시간 전까지만 취소 가능
        reservation_datetime = datetime.combine(reservation.reservation_date, reservation.start_time)
        if datetime.now() >= reservation_datetime - timedelta(hours=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="예약 취소는 이용 시간 1시간 전까지만 가능합니다.",
            )

        try:
            reservation.status = "취소" # 더티 체킹(Dirty Checking)으로 상태 변경
            db.commit()
        except Exception:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="취소 처리 중 오류가 발생했습니다.")


reservation_service = ReservationService()