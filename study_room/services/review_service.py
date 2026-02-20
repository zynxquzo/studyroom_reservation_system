# study_room/services/review_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from study_room.repositories.review_repository import review_repository
from study_room.repositories.reservation_repository import reservation_repository
from study_room.repositories.study_room_repository import study_room_repository
from study_room.models.review import Review
from study_room.models.user import User
from study_room.schemas.review import ReviewCreate, ReviewResponse, ReviewListItem, RoomReviewsResponse


class ReviewService:
    async def create_review(self, db: AsyncSession, data: ReviewCreate, current_user: User) -> ReviewResponse:
        reservation = await reservation_repository.find_by_id(db, data.reservation_id)

        if not reservation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 예약입니다.")
        if reservation.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="본인 예약에만 리뷰를 작성할 수 있습니다.")
        if reservation.status != "이용완료":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="이용 완료된 예약에만 리뷰를 작성할 수 있습니다.")

        if await review_repository.find_by_reservation_id(db, data.reservation_id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="이미 리뷰를 작성하셨습니다.")

        async with db.begin():
            new_review = Review(
                reservation=reservation,
                user=current_user,
                room=reservation.room,
                rating=data.rating,
                content=data.content,
            )
            await review_repository.save(db, new_review)

            avg_rating = await review_repository.get_average_rating(db, reservation.room_id)
            await study_room_repository.update_rating(db, reservation.room, avg_rating)

        await db.refresh(new_review)
        return ReviewResponse(
            id=new_review.id,
            room_name=reservation.room.name,
            rating=new_review.rating,
            content=new_review.content,
            created_at=new_review.created_at,
        )

    async def read_room_reviews(self, db: AsyncSession, room_id: int) -> RoomReviewsResponse:
        room = await study_room_repository.find_by_id(db, room_id)
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 스터디룸입니다.")

        reviews = await review_repository.find_by_room_id(db, room_id)
        avg_rating = await review_repository.get_average_rating(db, room_id)

        items = [
            ReviewListItem(
                id=r.id,
                # 학번 마스킹: 앞 4자리만 표시
                student_id=r.user.student_id[:4] + "****",
                rating=r.rating,
                content=r.content,
                created_at=r.created_at,
            )
            for r in reviews
        ]
        return RoomReviewsResponse(room_id=room_id, average_rating=avg_rating, reviews=items)


review_service = ReviewService()