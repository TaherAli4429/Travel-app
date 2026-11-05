from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.destination import DestinationResponse
from app.schemas.favorite import FavoriteCheckResponse, FavoriteResponse
from app.services.favorite_service import FavoriteService

router = APIRouter(prefix="/favorites", tags=["Favorites / Saved Places"])


@router.post(
    "/{destination_id}",
    response_model=ApiResponse[FavoriteResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add destination to user favorites",
)
def add_favorite(
    destination_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    fav = FavoriteService.add_favorite(db, current_user, destination_id)
    return ApiResponse(
        success=True,
        message="Destination saved to favorites",
        data=FavoriteResponse.model_validate(fav),
    )


@router.delete(
    "/{destination_id}",
    response_model=ApiResponse[dict],
    summary="Remove destination from user favorites",
)
def remove_favorite(
    destination_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    FavoriteService.remove_favorite(db, current_user, destination_id)
    return ApiResponse(
        success=True,
        message="Destination removed from favorites",
        data={"destination_id": destination_id},
    )


@router.get(
    "",
    response_model=ApiResponse[List[DestinationResponse]],
    summary="Get all favorites for the currently authenticated user",
)
def get_user_favorites(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    items, meta = FavoriteService.get_user_favorites(db, current_user, page=page, limit=limit)
    return ApiResponse(
        success=True,
        message="User favorites retrieved",
        data=items,
        meta=meta,
    )


@router.get(
    "/check/{destination_id}",
    response_model=ApiResponse[FavoriteCheckResponse],
    summary="Check if destination is saved in user favorites",
)
def check_favorite(
    destination_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    is_saved = FavoriteService.check_favorite(db, current_user, destination_id)
    return ApiResponse(
        success=True,
        message="Favorite check completed",
        data=FavoriteCheckResponse(destination_id=destination_id, is_saved=is_saved),
    )
