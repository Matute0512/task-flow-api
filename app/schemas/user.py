from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario único")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128, description="Contraseña en texto plano")


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None

