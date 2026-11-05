from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.notification import NotificationResponse, UnreadCountResponse
from app.utils.pagination import paginate_query

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=ApiResponse[List[NotificationResponse]],
    summary="Get user-specific notifications",
)
def get_notifications(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
    )
    items, meta = paginate_query(query, page=page, limit=limit)
    responses = [NotificationResponse.model_validate(n) for n in items]
    return ApiResponse(
        success=True,
        message="Notifications retrieved",
        data=responses,
        meta=meta,
    )


@router.get(
    "/unread-count",
    response_model=ApiResponse[UnreadCountResponse],
    summary="Get unread notifications count for current user",
)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    count = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .count()
    )
    return ApiResponse(
        success=True,
        message="Unread count retrieved",
        data=UnreadCountResponse(unread_count=count),
    )


@router.patch(
    "/{notification_id}/read",
    response_model=ApiResponse[NotificationResponse],
    summary="Mark single notification as read",
)
def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notice = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    notice.is_read = True
    db.commit()
    db.refresh(notice)
    return ApiResponse(
        success=True,
        message="Notification marked as read",
        data=NotificationResponse.model_validate(notice),
    )


@router.patch(
    "/read-all",
    response_model=ApiResponse[dict],
    summary="Mark all user notifications as read",
)
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.is_read == False)
        .update({"is_read": True})
    )
    db.commit()
    return ApiResponse(
        success=True,
        message=f"Marked {updated} notifications as read",
        data={"updated_count": updated},
    )


@router.delete(
    "/{notification_id}",
    response_model=ApiResponse[dict],
    summary="Delete a notification",
)
def delete_notification(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notice = (
        db.query(Notification)
        .filter(Notification.id == notification_id, Notification.user_id == current_user.id)
        .first()
    )
    if not notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    db.delete(notice)
    db.commit()
    return ApiResponse(
        success=True,
        message="Notification deleted successfully",
        data={"notification_id": notification_id},
    )
