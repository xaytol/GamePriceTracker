from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserLogin(BaseModel):
    email: str = Field(
        ..., min_length=5, max_length=100, description="Email пользователя"
    )
    password: str = Field(..., min_length=8, max_length=100, description="Пароль")


class UserCreate(BaseModel):
    email: str = Field(
        ..., min_length=5, max_length=100, description="Email пользователя"
    )
    password: str = Field(
        ..., min_length=8, max_length=100, description="Пароль (от 8 до 100 символов)"
    )


class UserUpdate(BaseModel):
    email: str | None = Field(None, min_length=5, max_length=100)
    password: str | None = Field(None, min_length=8, max_length=100)


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
