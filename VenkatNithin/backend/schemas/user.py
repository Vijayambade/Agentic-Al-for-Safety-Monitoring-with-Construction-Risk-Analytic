"""
backend/schemas/user.py
-----------------------
Pydantic models for request validation and response serialization.
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserRole(str, Enum):
    ADMIN = "Admin"
    ENGINEER = "Engineer"
    CONTRACTOR = "Contractor"
    WORKER = "Worker"
    HR = "HR"
    CLIENT = "Client"
    SUPPLIER = "Supplier"
    PROJECT_MANAGER = "Project Manager"
    SAFETY_OFFICER = "Safety Officer"
    SITE_SUPERVISOR = "Site Supervisor"
    VOLUNTEER = "Volunteer"


class UserBase(BaseModel):
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    role: UserRole


class UserRegister(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    email: str


class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


class OTPVerify(BaseModel):
    email: EmailStr
    otp_code: str


class ForgotPassword(BaseModel):
    email: EmailStr


class ResetPassword(BaseModel):
    email: EmailStr
    otp_code: str
    new_password: str = Field(..., min_length=6, max_length=128)


class ResendOTP(BaseModel):
    email: EmailStr
