from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import (
    PasswordChangeRequest,
    UserProfileResponse,
    UserUpdateRequest,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["Users & Profile"])


@router.get(
    "/me",
    response_model=ApiResponse[UserProfileResponse],
    summary="Get detailed profile of current user with statistics",
)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = AuthService.get_user_profile(db, current_user)
    return ApiResponse(
        success=True,
        message="Profile retrieved successfully",
        data=profile,
    )


@router.put(
    "/me",
    response_model=ApiResponse[UserProfileResponse],
    summary="Update full profile details of current user",
)
def update_user_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated = AuthService.update_profile(db, current_user, request)
    profile = AuthService.get_user_profile(db, updated)
    return ApiResponse(
        success=True,
        message="Profile updated successfully",
        data=profile,
    )


@router.patch(
    "/me",
    response_model=ApiResponse[UserProfileResponse],
    summary="Partially update profile details of current user",
)
def patch_user_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    updated = AuthService.update_profile(db, current_user, request)
    profile = AuthService.get_user_profile(db, updated)
    return ApiResponse(
        success=True,
        message="Profile updated successfully",
        data=profile,
    )


@router.post(
    "/me/change-password",
    response_model=ApiResponse[dict],
    summary="Change password of current user",
)
def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    AuthService.change_password(db, current_user, request)
    return ApiResponse(
        success=True,
        message="Password changed successfully",
        data={},
    )
