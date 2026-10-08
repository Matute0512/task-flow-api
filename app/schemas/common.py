from typing import Generic, TypeVar
from fastapi import Query
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams:
    """Dependencia reutilizable para paginación compatible con endpoints GET."""

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Número de registros a saltar"),
        limit: int = Query(10, ge=1, le=100, description="Máximo de registros a retornar"),
    ):
        self.skip = skip
        self.limit = limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Schema genérico para respuestas paginadas."""
    items: list[T] = Field(..., description="Lista de elementos de la página actual")
    total: int = Field(..., description="Total de registros disponibles")
    skip: int = Field(..., description="Registros saltados")
    limit: int = Field(..., description="Límite por página")

    @property
    def has_next(self) -> bool:
        return self.skip + self.limit < self.total

    @property
    def has_prev(self) -> bool:
        return self.skip > 0
