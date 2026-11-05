from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.destination import Destination
from app.models.review import Review
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.review import (
    ReviewCreateRequest,
    ReviewResponse,
    ReviewUpdateRequest,
)
from app.utils.pagination import paginate_query

router = APIRouter(prefix="/reviews", tags=["Reviews & Ratings"])


def _recalculate_destination_rating(db: Session, destination_id: str):
    dest = db.query(Destination).filter(Destination.id == destination_id).first()
    if not dest:
        return
    stats = (
        db.query(func.avg(Review.rating), func.count(Review.id))
        .filter(Review.destination_id == destination_id)
        .first()
    )
    avg_rating, count = stats
    if count and count > 0:
        dest.rating = round(float(avg_rating), 2)
        dest.reviews_count = count
    db.commit()


@router.post(
    "",
    response_model=ApiResponse[ReviewResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Submit a review for a destination",
)
def create_review(
    request: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    dest = db.query(Destination).filter(Destination.id == request.destination_id).first()
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Destination '{request.destination_id}' not found",
        )

    review = Review(
        user_id=current_user.id,
        destination_id=request.destination_id,
        rating=request.rating,
        comment=request.comment.strip(),
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    _recalculate_destination_rating(db, request.destination_id)

    resp = ReviewResponse.model_validate(review)
    resp.user_name = current_user.full_name
    return ApiResponse(
        success=True,
        message="Review submitted successfully",
        data=resp,
    )


@router.get(
    "/destination/{destination_id}",
    response_model=ApiResponse[List[ReviewResponse]],
    summary="Get all reviews for a specific destination",
)
def get_destination_reviews(
    destination_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Review)
        .filter(Review.destination_id == destination_id)
        .order_by(Review.created_at.desc())
    )
    items, meta = paginate_query(query, page=page, limit=limit)

    responses = []
    for r in items:
        resp = ReviewResponse.model_validate(r)
        if r.user:
            resp.user_name = r.user.full_name
        responses.append(resp)

    return ApiResponse(
        success=True,
        message="Reviews retrieved successfully",
        data=responses,
        meta=meta,
    )


@router.get(
    "/my-reviews",
    response_model=ApiResponse[List[ReviewResponse]],
    summary="Get all reviews submitted by the current user",
)
def get_my_reviews(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Review)
        .filter(Review.user_id == current_user.id)
        .order_by(Review.created_at.desc())
    )
    items, meta = paginate_query(query, page=page, limit=limit)
    responses = [ReviewResponse.model_validate(r) for r in items]
    for resp in responses:
        resp.user_name = current_user.full_name

    return ApiResponse(
        success=True,
        message="User reviews retrieved",
        data=responses,
        meta=meta,
    )


@router.put(
    "/{review_id}",
    response_model=ApiResponse[ReviewResponse],
    summary="Update an existing review by owner",
)
def update_review(
    review_id: str,
    request: ReviewUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to edit this review",
        )

    if request.rating is not None:
        review.rating = request.rating
    if request.comment is not None:
        review.comment = request.comment.strip()

    db.commit()
    db.refresh(review)

    _recalculate_destination_rating(db, review.destination_id)

    resp = ReviewResponse.model_validate(review)
    resp.user_name = current_user.full_name
    return ApiResponse(
        success=True,
        message="Review updated successfully",
        data=resp,
    )


@router.delete(
    "/{review_id}",
    response_model=ApiResponse[dict],
    summary="Delete an existing review by owner",
)
def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    if review.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this review",
        )

    destination_id = review.destination_id
    db.delete(review)
    db.commit()

    _recalculate_destination_rating(db, destination_id)

    return ApiResponse(
        success=True,
        message="Review deleted successfully",
        data={"review_id": review_id},
    )
