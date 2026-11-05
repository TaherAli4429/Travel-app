from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.common import ApiResponse
from app.schemas.user import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    TokenRefreshRequest,
    TokenResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=ApiResponse[UserResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(request: UserRegisterRequest, db: Session = Depends(get_db)):
    user = AuthService.register_user(db, request)
    return ApiResponse(
        success=True,
        message="Account created successfully",
        data=UserResponse.model_validate(user),
    )


@router.post(
    "/login",
    response_model=ApiResponse[TokenResponse],
    summary="Authenticate user and return JWT tokens",
)
def login(request: UserLoginRequest, db: Session = Depends(get_db)):
    token_response = AuthService.login_user(db, request)
    return ApiResponse(
        success=True,
        message="Login successful",
        data=token_response,
    )


@router.get(
    "/me",
    response_model=ApiResponse[UserResponse],
    summary="Get current authenticated user profile",
)
def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(
        success=True,
        message="User details retrieved",
        data=UserResponse.model_validate(current_user),
    )


@router.post(
    "/refresh",
    response_model=ApiResponse[TokenResponse],
    summary="Refresh access token using refresh token",
)
def refresh_token(request: TokenRefreshRequest, db: Session = Depends(get_db)):
    token_response = AuthService.refresh_access_token(db, request.refresh_token)
    return ApiResponse(
        success=True,
        message="Token refreshed successfully",
        data=token_response,
    )


@router.post(
    "/logout",
    response_model=ApiResponse[dict],
    summary="Log out current authenticated user",
)
def logout(current_user: User = Depends(get_current_user)):
    # Standard JWT client-side discard + server confirmation
    return ApiResponse(
        success=True,
        message="Logged out successfully",
        data={"user_id": current_user.id},
    )


@router.post(
    "/forgot-password",
    response_model=ApiResponse[dict],
    summary="Request a password reset link/token",
)
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    token_or_msg = AuthService.request_password_reset(db, request.email)
    return ApiResponse(
        success=True,
        message="If this email is registered, password reset instructions have been generated.",
        data={"dev_reset_token": token_or_msg},
    )


@router.post(
    "/reset-password",
    response_model=ApiResponse[dict],
    summary="Reset password using valid reset token",
)
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    AuthService.reset_password(db, request.token, request.new_password)
    return ApiResponse(
        success=True,
        message="Password has been reset successfully. You can now login with your new password.",
        data={},
    )
