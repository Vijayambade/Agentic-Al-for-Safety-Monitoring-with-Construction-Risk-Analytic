"""
backend/services/auth_service.py
--------------------------------
Authentication services: signup, login, OTP generation/validation, password reset.
"""
import logging
import random
import smtplib
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.config import settings
from backend.models.user import User
from backend.schemas.user import UserRegister
from backend.utils.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)

logger = logging.getLogger(__name__)


def generate_otp() -> str:
    """Generate a random 6-digit numeric OTP code."""
    return f"{random.randint(100000, 999999)}"


def send_otp_email(email: str, otp: str, purpose: str = "verification") -> bool:
    """
    Send an OTP code to the user's email address via SMTP.

    Falls back gracefully to logging the OTP to the console if SMTP config is missing.
    """
    subject = f"Construction Hub - OTP for account {purpose}"
    body = f"""
    <h2>Construction Intelligent Hub</h2>
    <p>Your 6-digit One-Time Password (OTP) for account <b>{purpose}</b> is:</p>
    <h1 style="color: #FF8C00; font-family: monospace; letter-spacing: 2px;">{otp}</h1>
    <p>This code is valid for 15 minutes. If you did not request this code, please ignore this email.</p>
    """

    # Check if SMTP parameters are configured
    if not settings.smtp_user or not settings.smtp_pass:
        logger.warning(
            "=== [SMTP Fallback] OTP for %s: %s (SMTP credentials not configured) ===",
            email,
            otp,
        )
        print(
            f"\n--- [MAIL SIMULATOR] OTP for {email} ({purpose}): {otp} ---\n",
            flush=True,
        )
        return True

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.smtp_from_name} <{settings.smtp_user}>"
        msg["To"] = email
        msg.attach(MIMEText(body, "html"))

        # Connect to SMTP server
        if settings.smtp_tls:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port)

        server.login(settings.smtp_user, settings.smtp_pass)
        server.sendmail(settings.smtp_user, email, msg.as_string())
        server.quit()
        logger.info("Successfully sent OTP email to %s", email)
        return True
    except Exception as exc:
        logger.error("Failed to send OTP email to %s: %s", email, exc)
        # Still print OTP to terminal console so system remains usable
        print(
            f"\n--- [SMTP ERROR FALLBACK] OTP for {email} ({purpose}): {otp} ---\n",
            flush=True,
        )
        return False


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Retrieve a user from database by email (case-insensitive)."""
    return db.query(User).filter(User.email == email.lower()).first()


def register_user(db: Session, schema: UserRegister) -> User:
    """
    Register a new user account in an unverified state.

    Generates and sends an OTP verification code.
    """
    existing_user = get_user_by_email(db, schema.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email is already registered.",
        )

    otp = generate_otp()
    otp_expires = datetime.utcnow() + timedelta(minutes=15)

    hashed_pw = get_password_hash(schema.password)

    new_user = User(
        email=schema.email.lower(),
        hashed_password=hashed_pw,
        first_name=schema.first_name,
        last_name=schema.last_name,
        role=schema.role.value,
        is_active=True,
        is_verified=False,  # Needs OTP verification
        otp_code=otp,
        otp_expires_at=otp_expires,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Attempt to send registration OTP email
    send_otp_email(new_user.email, otp, "verification")

    return new_user


def verify_user_otp(db: Session, email: str, otp_code: str) -> bool:
    """
    Verify the user's OTP code. If valid, marks the user account as verified.
    """
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.is_verified:
        return True

    if not user.otp_code or not user.otp_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active OTP found for this account.",
        )

    if user.otp_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP code has expired. Please request a new one.",
        )

    if user.otp_code != otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code.",
        )

    # Verification successful
    user.is_verified = True
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    return True


def resend_verification_otp(db: Session, email: str) -> bool:
    """Resend a new email verification OTP to the user."""
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already verified.",
        )

    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=15)
    db.commit()

    send_otp_email(user.email, otp, "verification")
    return True


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate a user.

    Raises HTTPExceptions if auth fails, user is disabled, or email is unverified.
    """
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated.",
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account email is not verified. Please verify your OTP first.",
        )

    return user


def initiate_forgot_password(db: Session, email: str) -> bool:
    """
    Initiate the forgot password workflow.

    Generates a password reset OTP and sends it via email.
    """
    user = get_user_by_email(db, email)
    # Silent success to prevent account enumeration
    if not user:
        logger.info("Forgot password triggered for non-existent email: %s", email)
        return True

    otp = generate_otp()
    user.otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=15)
    db.commit()

    send_otp_email(user.email, otp, "password reset")
    return True


def reset_user_password(
    db: Session, email: str, otp_code: str, new_password: str
) -> bool:
    """
    Validate the password reset OTP and update the user's password.
    """
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if not user.otp_code or not user.otp_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active password reset request found.",
        )

    if user.otp_expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP code has expired.",
        )

    if user.otp_code != otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code.",
        )

    # Perform password reset
    user.hashed_password = get_password_hash(new_password)
    user.otp_code = None
    user.otp_expires_at = None
    db.commit()
    return True
