"""
backend/routers/auth.py
-----------------------
FastAPI router containing all authentication endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models.user import User
from backend.schemas.user import (
    ForgotPassword,
    OTPVerify,
    ResendOTP,
    ResetPassword,
    Token,
    UserLogin,
    UserRegister,
    UserResponse,
)
from backend.services.auth_service import (
    authenticate_user,
    get_user_by_email,
    initiate_forgot_password,
    register_user,
    resend_verification_otp,
    reset_user_password,
    verify_user_otp,
)
from backend.utils.security import create_access_token, decode_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])
security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> User:
    """
    Dependency that decodes the JWT bearer token and retrieves the current user.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or session expired.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    email = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token payload is invalid.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authenticated user no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(schema: UserRegister, db: Session = Depends(get_db)):
    """Register a new construction platform user."""
    return register_user(db, schema)


@router.post("/verify-otp")
def verify_otp(schema: OTPVerify, db: Session = Depends(get_db)):
    """Verify registration OTP code."""
    verify_user_otp(db, schema.email, schema.otp_code)
    return {"detail": "Account verified successfully. You can now log in."}


@router.post("/resend-otp")
def resend_otp(schema: ResendOTP, db: Session = Depends(get_db)):
    """Resend email verification OTP."""
    resend_verification_otp(db, schema.email)
    return {"detail": "Verification OTP resent successfully."}


@router.post("/login", response_model=Token)
def login(schema: UserLogin, db: Session = Depends(get_db)):
    """Authenticate credentials and generate a JWT access token."""
    user = authenticate_user(db, schema.email, schema.password)

    # Determine token lifespan based on Remember Me option
    if schema.remember_me:
        # Load from config, fallback to 30 days
        from backend.config import settings

        expires = timedelta(days=settings.jwt_remember_me_expire_days)
    else:
        expires = None

    token = create_access_token(
        data={"sub": user.email, "role": user.role}, expires_delta=expires
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "role": user.role,
        "email": user.email,
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """
    Log out endpoint.

    For stateless JWT, the frontend clears the token.
    This serves as an optional server audit log trigger.
    """
    return {"detail": f"Successfully logged out user {current_user.email}"}


@router.post("/forgot-password")
def forgot_password(schema: ForgotPassword, db: Session = Depends(get_db)):
    """Initiate password recovery by sending an OTP reset code."""
    initiate_forgot_password(db, schema.email)
    return {
        "detail": "If the account exists, a password reset OTP has been sent."
    }


@router.post("/reset-password")
def reset_password(schema: ResetPassword, db: Session = Depends(get_db)):
    """Reset password using email, reset OTP, and new password details."""
    reset_user_password(db, schema.email, schema.otp_code, schema.new_password)
    return {"detail": "Password has been reset successfully. You can now log in."}


@router.get("/developer/get-otp")
def get_developer_otp(email: str, db: Session = Depends(get_db)):
    """Developer helper to fetch the latest OTP code for an email without checking terminal logs."""
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"otp_code": user.otp_code}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get profile of the currently logged-in user."""
    return current_user
