from __future__ import annotations
import uuid
from datetime import datetime
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
    avatar_url: str | None = None


class OAuthCallbackParams(BaseModel):
    code: str
    state: str


class OAuthUserInfo(BaseModel):
    provider: str
    provider_id: str
    email: EmailStr
    full_name: str | None = None
    avatar_url: str | None = None


class ConnectedAccount(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    provider: str
    connected_at: datetime


class PKCEAuthorizeRequest(BaseModel):
    provider: str
    code_challenge: str
    code_challenge_method: str = "S256"
    redirect_uri: str | None = None
    client_type: str = "web"


class OAuthCallbackRequest(BaseModel):
    code: str
    state: str
    code_verifier: str


class OAuthLoginResponse(BaseModel):
    user: UserResponse
    is_new_user: bool
    expires_in: int = Field(..., description="Access token lifetime in seconds.")


class OAuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse
    is_new_user: bool


class ConnectedProvider(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    provider: str
    connected_at: datetime
    avatar_url: str | None = None
