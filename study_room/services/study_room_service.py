# study_room/services/study_room_service.py

from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from study_room.repositories.study_room_repository import study_room_repository
from study_room.schemas.study_room import (
    StudyRoomListResponse,
    StudyRoomDetailResponse,
    AvailableTimesResponse,
    AvailableTimeSlot,
)


class StudyRoomService:
    def read_rooms(self, db: Session, floor: int | None, capacity: int | None) -> list[StudyRoomListResponse]:
        rooms = study_room_repository.find_all(db, floor=floor, capacity=capacity)
        return [
            StudyRoomListResponse(
                room_id=room.room_id,
                name=room.name,
                floor=room.floor,
                location=room.location,
                max_capacity=room.max_capacity,
                rating=room.rating,
                facilities=[f.name for f in room.facilities],
            )
            for room in rooms
        ]

    def read_room_by_id(self, db: Session, room_id: int):
        room = study_room_repository.find_by_id(db, room_id)
        if not room:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "존재하지 않는 스터디룸입니다.")
        return room

    def read_room_detail(self, db: Session, room_id: int) -> StudyRoomDetailResponse:
        room = self.read_room_by_id(db, room_id)
        return StudyRoomDetailResponse(
            room_id=room.room_id,
            name=room.name,
            floor=room.floor,
            location=room.location,
            max_capacity=room.max_capacity,
            rating=room.rating,
            open_time=room.open_time,
            close_time=room.close_time,
            facilities=[f.name for f in room.facilities],
        )

    def read_available_times(self, db: Session, room_id: int, target_date: date) -> AvailableTimesResponse:
        room = self.read_room_by_id(db, room_id)

        # 7일 이내 예약 가능 여부 체크
        today = date.today()
        if target_date < today or target_date > today + timedelta(days=7):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="최대 7일 이내 날짜만 선택 가능합니다.",
            )

        reserved_times = study_room_repository.get_reserved_times(db, room_id, target_date)
        reserved_set = set(reserved_times)

        # 운영 시간대 슬롯 생성
        slots = []
        current = datetime.combine(target_date, room.open_time)
        end = datetime.combine(target_date, room.close_time)

        while current < end:
            slot_time = current.time()
            slots.append(
                AvailableTimeSlot(
                    time=slot_time.strftime("%H:%M"),
                    available=slot_time not in reserved_set,
                )
            )
            current += timedelta(hours=1)

        return AvailableTimesResponse(
            room_id=room_id,
            date=str(target_date),
            available_times=slots,
        )


study_room_service = StudyRoomService()