from typing import List, Optional, Tuple
from sqlalchemy import or_, desc, asc
from sqlalchemy.orm import Session

from app.models.destination import Destination
from app.models.favorite import Favorite
from app.models.user import User
from app.schemas.common import PaginationMeta
from app.schemas.destination import DestinationResponse
from app.utils.pagination import paginate_query


class DestinationService:
    @staticmethod
    def _map_destination_response(dest: Destination, saved_ids: set) -> DestinationResponse:
        resp = DestinationResponse.model_validate(dest)
        resp.is_saved = dest.id in saved_ids
        return resp

    @staticmethod
    def _get_user_saved_ids(db: Session, user: Optional[User]) -> set:
        if not user:
            return set()
        favs = db.query(Favorite.destination_id).filter(Favorite.user_id == user.id).all()
        return {f[0] for f in favs}

    @classmethod
    def get_destinations(
        cls,
        db: Session,
        category: Optional[str] = None,
        min_rating: Optional[float] = None,
        search: Optional[str] = None,
        is_featured: Optional[bool] = None,
        sort_by: Optional[str] = None,
        current_user: Optional[User] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Tuple[List[DestinationResponse], PaginationMeta]:
        query = db.query(Destination)

        if category and category.lower() != "all":
            query = query.filter(Destination.category.ilike(category))

        if min_rating is not None and min_rating > 0.0:
            query = query.filter(Destination.rating >= min_rating)

        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Destination.name.ilike(term),
                    Destination.country.ilike(term),
                    Destination.category.ilike(term),
                    Destination.description.ilike(term),
                )
            )

        if is_featured is not None:
            query = query.filter(Destination.is_featured == is_featured)

        if sort_by == "rating":
            query = query.order_by(desc(Destination.rating))
        elif sort_by == "name":
            query = query.order_by(asc(Destination.name))
        else:
            query = query.order_by(desc(Destination.is_featured), desc(Destination.rating))

        items, meta = paginate_query(query, page=page, limit=limit)
        saved_ids = cls._get_user_saved_ids(db, current_user)
        responses = [cls._map_destination_response(item, saved_ids) for item in items]
        return responses, meta

    @classmethod
    def get_featured_destination(cls, db: Session, current_user: Optional[User] = None) -> Optional[DestinationResponse]:
        dest = db.query(Destination).filter(Destination.is_featured == True).first()
        if not dest:
            dest = db.query(Destination).order_by(desc(Destination.rating)).first()
        if not dest:
            return None
        saved_ids = cls._get_user_saved_ids(db, current_user)
        return cls._map_destination_response(dest, saved_ids)

    @classmethod
    def get_destination_by_id(
        cls, db: Session, destination_id: str, current_user: Optional[User] = None
    ) -> Optional[DestinationResponse]:
        dest = db.query(Destination).filter(Destination.id == destination_id).first()
        if not dest:
            return None
        saved_ids = cls._get_user_saved_ids(db, current_user)
        return cls._map_destination_response(dest, saved_ids)

    @classmethod
    def get_categories(cls, db: Session) -> List[str]:
        results = db.query(Destination.category).distinct().all()
        categories = sorted([r[0] for r in results if r[0]])
        return ["All"] + categories
