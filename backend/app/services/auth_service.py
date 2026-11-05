from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_password_reset_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
    verify_password_reset_token,
)
from app.models.favorite import Favorite
from app.models.notification import Notification
from app.models.review import Review
from app.models.user import User
from app.schemas.user import (
    PasswordChangeRequest,
    TokenResponse,
    UserLoginRequest,
    UserProfileResponse,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)


class AuthService:
    @staticmethod
    def register_user(db: Session, request: UserRegisterRequest) -> User:
        existing = db.query(User).filter(User.email == request.email.lower().strip()).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists",
            )

        new_user = User(
            full_name=request.full_name.strip(),
            email=request.email.lower().strip(),
            hashed_password=hash_password(request.password),
            is_active=True,
            is_verified=True,
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Welcome notification
        welcome_notice = Notification(
            user_id=new_user.id,
            title="Welcome to Wanderly!",
            message="Discover beautiful destinations and plan your unforgettable journeys.",
            is_read=False,
        )
        db.add(welcome_notice)
        db.commit()

        return new_user

    @staticmethod
    def login_user(db: Session, request: UserLoginRequest) -> TokenResponse:
        user = db.query(User).filter(User.email == request.email.lower().strip()).first()
        if not user or not verify_password(request.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account has been deactivated. Please contact support.",
            )

        access_token = create_access_token(subject=user.id)
        refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token_str: str) -> TokenResponse:
        try:
            payload = decode_token(refresh_token_str)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid refresh token: {str(e)}",
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token is not a valid refresh token",
            )

        user_id = payload.get("sub")
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
            )

        new_access_token = create_access_token(subject=user.id)
        new_refresh_token = create_refresh_token(subject=user.id)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
            user=UserResponse.model_validate(user),
        )

    @staticmethod
    def request_password_reset(db: Session, email: str) -> str:
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if not user:
            # We still return a safe message or token in development mode
            return "If that email is registered, password reset instructions have been generated."
        reset_token = create_password_reset_token(user.email)
        return reset_token

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        email = verify_password_reset_token(token)
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password reset token is invalid or has expired",
            )

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.hashed_password = hash_password(new_password)
        db.commit()
        return True

    @staticmethod
    def get_user_profile(db: Session, user: User) -> UserProfileResponse:
        saved_count = db.query(Favorite).filter(Favorite.user_id == user.id).count()
        reviews_count = db.query(Review).filter(Review.user_id == user.id).count()
        trips_count = 0  # Trips are not currently supported by frontend; kept accurate

        profile_dict = {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "profile_image": user.profile_image,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at,
            "updated_at": user.updated_at,
            "saved_count": saved_count,
            "reviews_count": reviews_count,
            "trips_count": trips_count,
        }
        return UserProfileResponse.model_validate(profile_dict)

    @staticmethod
    def update_profile(db: Session, user: User, update_data: UserUpdateRequest) -> User:
        if update_data.email and update_data.email.lower().strip() != user.email:
            existing = db.query(User).filter(User.email == update_data.email.lower().strip()).first()
            if existing and existing.id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This email address is already in use by another account",
                )
            user.email = update_data.email.lower().strip()

        if update_data.full_name is not None:
            user.full_name = update_data.full_name.strip()

        if update_data.profile_image is not None:
            user.profile_image = update_data.profile_image.strip()

        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(db: Session, user: User, password_data: PasswordChangeRequest) -> bool:
        if not verify_password(password_data.current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect",
            )

        user.hashed_password = hash_password(password_data.new_password)
        db.commit()
        return True
