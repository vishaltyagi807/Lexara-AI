from __future__ import annotations
import uuid
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr = Field(..., description="User's email address.")
    password: str = Field(..., min_length=8, description="Plaintext password (min 8 chars).")
    full_name: str = Field(..., min_length=1, max_length=255, description="Display name.")

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:

        has_letter = any(c.isalpha() for c in v)
        has_digit = any(c.isdigit() for c in v)
        if not (has_letter and has_digit):
            raise ValueError("Password must contain at least one letter and one digit.")
        return v


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    email: EmailStr = Field(..., description="Registered email address.")
    password: str = Field(..., description="Plaintext password.")


class RefreshResponse(BaseModel):
    status: str = "success"
    expires_in: int = Field(..., description="Access token lifetime in seconds.")


class UpdateMeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    full_name: str | None = Field(
        None, min_length=1, max_length=255, description="New display name."
    )




class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int = Field(..., description="Access token lifetime in seconds.")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    email: EmailStr
    full_name: str
    tier: str
    is_verified: bool
