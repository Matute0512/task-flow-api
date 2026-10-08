from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class CategoryBase(BaseModel):
    """Schema base con los campos comunes."""
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        examples=["Trabajo", "Personal", "Estudio"],
        description="Nombre de la categoría",
    )
    description: str | None = Field(
        None,
        max_length=500,
        examples=["Tareas relacionadas con el trabajo"],
        description="Descripción opcional de la categoría",
    )
    color: str = Field(
        "#3B82F6",
        pattern=r"^#[0-9A-Fa-f]{6}$",
        examples=["#3B82F6", "#EF4444", "#10B981"],
        description="Color en formato hexadecimal",
    )


class CategoryCreate(CategoryBase):
    """Schema para crear una nueva categoría."""
    pass


class CategoryUpdate(BaseModel):
    """Schema para actualizar una categoría (todos los campos opcionales)."""
    name: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        examples=["Trabajo Remoto"],
    )
    description: str | None = Field(None, max_length=500)
    color: str | None = Field(None, pattern=r"^#[0-9A-Fa-f]{6}$")


class CategoryResponse(CategoryBase):
    """Schema de respuesta con los datos completos."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    owner_id: int | None = Field(None, examples=[1], description="ID del usuario propietario")
    created_at: datetime = Field(..., examples=["2026-10-09T10:00:00Z"])
