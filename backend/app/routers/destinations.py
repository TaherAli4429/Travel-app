from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user_optional
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.destination import DestinationResponse
from app.services.destination_service import DestinationService

router = APIRouter(prefix="/destinations", tags=["Destinations"])


@router.get(
    "",
    response_model=ApiResponse[List[DestinationResponse]],
    summary="List all destinations with optional filters and pagination",
)
def list_destinations(
    category: Optional[str] = Query(None, description="Filter by category (e.g. Beaches, Mountains)"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Minimum star rating filter"),
    search: Optional[str] = Query(None, description="Search query in name, country, category, description"),
    is_featured: Optional[bool] = Query(None, description="Filter for featured destination"),
    sort_by: Optional[str] = Query(None, description="Sort order: rating, name"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    items, meta = DestinationService.get_destinations(
        db=db,
        category=category,
        min_rating=min_rating,
        search=search,
        is_featured=is_featured,
        sort_by=sort_by,
        current_user=current_user,
        page=page,
        limit=limit,
    )
    return ApiResponse(
        success=True,
        message="Destinations fetched successfully",
        data=items,
        meta=meta,
    )


@router.get(
    "/featured",
    response_model=ApiResponse[Optional[DestinationResponse]],
    summary="Get top featured destination",
)
def get_featured_destination(
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    dest = DestinationService.get_featured_destination(db, current_user=current_user)
    return ApiResponse(
        success=True,
        message="Featured destination retrieved",
        data=dest,
    )


@router.get(
    "/categories",
    response_model=ApiResponse[List[str]],
    summary="Get all available destination categories",
)
def get_categories(db: Session = Depends(get_db)):
    categories = DestinationService.get_categories(db)
    return ApiResponse(
        success=True,
        message="Categories fetched successfully",
        data=categories,
    )


@router.get(
    "/search",
    response_model=ApiResponse[List[DestinationResponse]],
    summary="Search destinations by keyword across name, country, category",
)
def search_destinations(
    q: Optional[str] = Query(None, description="Search query"),
    search: Optional[str] = Query(None, description="Alternate search query parameter"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    term = q or search or ""
    items, meta = DestinationService.get_destinations(
        db=db,
        search=term,
        current_user=current_user,
        page=page,
        limit=limit,
    )
    return ApiResponse(
        success=True,
        message=f"Search completed for '{term}'",
        data=items,
        meta=meta,
    )


@router.get(
    "/{destination_id}",
    response_model=ApiResponse[DestinationResponse],
    summary="Get single destination details by ID",
)
def get_destination_by_id(
    destination_id: str,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    dest = DestinationService.get_destination_by_id(db, destination_id, current_user=current_user)
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination '{destination_id}' not found",
        )
    return ApiResponse(
        success=True,
        message="Destination details retrieved",
        data=dest,
    )
