from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.dependencies import get_current_user, get_db
from app.models import Category, User
from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)
from app.schemas.common import PaginatedResponse, PaginationParams

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría",
    description="Crea una nueva categoría para organizar tus tareas vinculada al usuario autenticado.",
    responses={
        201: {"description": "Categoría creada exitosamente"},
        422: {"description": "Error de validación en los datos"},
    },
)
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_category(
    category_in: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva categoría vinculada al usuario autenticado."""
    category = Category(
        **category_in.model_dump(),
        owner_id=current_user.id,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get(
    "",
    response_model=PaginatedResponse[CategoryResponse],
    summary="Listar todas las categorías",
    description="Retorna las categorías del usuario autenticado con soporte para paginación.",
)
@router.get("/", response_model=PaginatedResponse[CategoryResponse], include_in_schema=False)
def list_categories(
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista las categorías del usuario autenticado con paginación usando SQLAlchemy 2.0."""
    count_stmt = select(func.count()).select_from(Category).where(Category.owner_id == current_user.id)
    total = db.scalar(count_stmt) or 0

    stmt = (
        select(Category)
        .where(Category.owner_id == current_user.id)
        .order_by(Category.name)
        .offset(pagination.skip)
        .limit(pagination.limit)
    )
    categories = db.scalars(stmt).all()

    return PaginatedResponse(
        items=list(categories),
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Obtener una categoría por ID",
    description="Retorna los detalles de una categoría específica del usuario.",
    responses={
        404: {"description": "Categoría no encontrada"},
    },
)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una categoría por su ID verificando propiedad del usuario."""
    stmt = select(Category).where(
        Category.id == category_id,
        Category.owner_id == current_user.id,
    )
    category = db.scalar(stmt)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )
    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    summary="Actualizar una categoría",
    description="Actualiza los datos de una categoría existente.",
    responses={
        404: {"description": "Categoría no encontrada"},
    },
)
def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una categoría existente."""
    stmt = select(Category).where(
        Category.id == category_id,
        Category.owner_id == current_user.id,
    )
    category = db.scalar(stmt)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )

    update_data = category_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(category, field, value)

    db.commit()
    db.refresh(category)
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una categoría",
    description="Elimina una categoría. Las tareas asociadas quedarán sin categoría.",
    responses={
        204: {"description": "Categoría eliminada exitosamente"},
        404: {"description": "Categoría no encontrada"},
    },
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una categoría."""
    stmt = select(Category).where(
        Category.id == category_id,
        Category.owner_id == current_user.id,
    )
    category = db.scalar(stmt)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {category_id} not found",
        )

    db.delete(category)
    db.commit()
    return None
