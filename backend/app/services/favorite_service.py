from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.destination import Destination
from app.models.favorite import Favorite
from app.models.user import User
from app.schemas.common import PaginationMeta
from app.schemas.destination import DestinationResponse
from app.utils.pagination import paginate_query


class FavoriteService:
    @staticmethod
    def add_favorite(db: Session, user: User, destination_id: str) -> Favorite:
        dest = db.query(Destination).filter(Destination.id == destination_id).first()
        if not dest:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Destination '{destination_id}' not found",
            )

        existing = (
            db.query(Favorite)
            .filter(Favorite.user_id == user.id, Favorite.destination_id == destination_id)
            .first()
        )
        if existing:
            return existing

        favorite = Favorite(user_id=user.id, destination_id=destination_id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite

    @staticmethod
    def remove_favorite(db: Session, user: User, destination_id: str) -> bool:
        fav = (
            db.query(Favorite)
            .filter(Favorite.user_id == user.id, Favorite.destination_id == destination_id)
            .first()
        )
        if not fav:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Favorite record not found for this destination",
            )

        db.delete(fav)
        db.commit()
        return True

    @staticmethod
    def get_user_favorites(
        db: Session, user: User, page: int = 1, limit: int = 50
    ) -> Tuple[List[DestinationResponse], PaginationMeta]:
        query = (
            db.query(Destination)
            .join(Favorite, Favorite.destination_id == Destination.id)
            .filter(Favorite.user_id == user.id)
            .order_by(Favorite.created_at.desc())
        )

        items, meta = paginate_query(query, page=page, limit=limit)
        responses = []
        for dest in items:
            resp = DestinationResponse.model_validate(dest)
            resp.is_saved = True
            responses.append(resp)

        return responses, meta

    @staticmethod
    def check_favorite(db: Session, user: User, destination_id: str) -> bool:
        count = (
            db.query(Favorite)
            .filter(Favorite.user_id == user.id, Favorite.destination_id == destination_id)
            .count()
        )
        return count > 0
