from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict

from app.schemas.category import CategoryResponse


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskBase(BaseModel):
    """Schema base con los campos comunes."""
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        examples=["Terminar reporte mensual"],
        description="Título claro y conciso de la tarea",
    )
    description: str | None = Field(
        None,
        examples=["Incluir gráficos de ventas del Q3"],
        description="Detalles adicionales sobre la tarea",
    )
    is_completed: bool = Field(
        False,
        description="Estado de completado de la tarea",
    )
    priority: TaskPriority = Field(
        TaskPriority.MEDIUM,
        description="Prioridad de la tarea",
    )
    due_date: datetime | None = Field(
        None,
        examples=["2026-10-15T18:00:00Z"],
        description="Fecha límite de la tarea (ISO 8601)",
    )
    category_id: int | None = Field(
        None,
        examples=[1],
        description="ID de la categoría asociada",
    )


class TaskCreate(TaskBase):
    """Schema para crear una nueva tarea."""
    pass


class TaskUpdate(BaseModel):
    """Schema para actualizar una tarea (todos los campos opcionales)."""
    title: str | None = Field(None, min_length=3, max_length=100)
    description: str | None = None
    is_completed: bool | None = None
    priority: TaskPriority | None = None
    due_date: datetime | None = None
    category_id: int | None = None


class TaskResponse(TaskBase):
    """Schema de respuesta con los datos completos."""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., examples=[1])
    owner_id: int | None = Field(None, examples=[1], description="ID del usuario propietario")
    created_at: datetime
    updated_at: datetime
    category: CategoryResponse | None = None
