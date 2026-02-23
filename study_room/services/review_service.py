# study_room/services/review_service.py

import logging
from sqlalchemy.ext.asyncio import AsyncSession

from study_room.exceptions import NotFoundException, ForbiddenException, BadRequestException, DuplicateException
from study_room.repositories.review_repository import review_repository
from study_room.repositories.reservation_repository import reservation_repository
from study_room.repositories.study_room_repository import study_room_repository
from study_room.models.review import Review
from study_room.models.user import User
from study_room.schemas.review import ReviewCreate, ReviewResponse, ReviewListItem, RoomReviewsResponse

logger = logging.getLogger(__name__)


class ReviewService:
    async def create_review(self, db: AsyncSession, data: ReviewCreate, current_user: User) -> ReviewResponse:
        reservation = await reservation_repository.find_by_id(db, data.reservation_id)

        if not reservation:
            raise NotFoundException("존재하지 않는 예약입니다.")
        if reservation.user_id != current_user.id:
            logger.warning("리뷰 작성 권한 없음: user_id=%s, reservation_id=%s", current_user.id, data.reservation_id)
            raise ForbiddenException("본인 예약에만 리뷰를 작성할 수 있습니다.")
        if reservation.status != "이용완료":
            raise BadRequestException("이용 완료된 예약에만 리뷰를 작성할 수 있습니다.")

        if await review_repository.find_by_reservation_id(db, data.reservation_id):
            raise DuplicateException("이미 리뷰를 작성하셨습니다.")

        logger.info("리뷰 작성: user_id=%s, reservation_id=%s, room_id=%s", current_user.id, data.reservation_id, reservation.room_id)

        # 리뷰 저장과 rating 업데이트를 한 트랜잭션으로 묶음 (update_rating은 커밋 시점에만 DB 반영됨)
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
        logger.info("리뷰 작성 완료: review_id=%s", new_review.id)
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
            raise NotFoundException("존재하지 않는 스터디룸입니다.")

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