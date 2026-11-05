import math
from typing import Any, List, Tuple, TypeVar
from sqlalchemy.orm import Query

from app.schemas.common import PaginationMeta

T = TypeVar("T")


def paginate_query(query: Query, page: int = 1, limit: int = 10) -> Tuple[List[Any], PaginationMeta]:
    if page < 1:
        page = 1
    if limit < 1:
        limit = 10
    if limit > 100:
        limit = 100

    total = query.count()
    total_pages = math.ceil(total / limit) if total > 0 else 1
    offset = (page - 1) * limit

    items = query.offset(offset).limit(limit).all()

    meta = PaginationMeta(
        page=page,
        limit=limit,
        total=total,
        total_pages=total_pages,
    )

    return items, meta
