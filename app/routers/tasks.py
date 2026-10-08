from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload

from app.dependencies import get_current_user, get_db
from app.models import Category, Task, User
from app.schemas.common import PaginatedResponse, PaginationParams
from app.schemas.task import TaskCreate, TaskPriority, TaskResponse, TaskUpdate

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva tarea",
    description="Crea una nueva tarea asociada al usuario autenticado. Opcionalmente puede asociarse a una categoría del mismo usuario.",
    responses={
        201: {"description": "Tarea creada exitosamente"},
        404: {"description": "Categoría no encontrada"},
        422: {"description": "Error de validación"},
    },
)
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
def create_task(
    task_in: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Crea una nueva tarea asignando owner_id al usuario autenticado."""
    # Validar que la categoría exista y pertenezca al usuario si se proporciona
    if task_in.category_id is not None:
        cat_stmt = select(Category).where(
            Category.id == task_in.category_id,
            Category.owner_id == current_user.id,
        )
        category = db.scalar(cat_stmt)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {task_in.category_id} not found",
            )

    task = Task(
        **task_in.model_dump(),
        owner_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    # Cargar relación category para la respuesta
    stmt = (
        select(Task)
        .options(joinedload(Task.category))
        .where(Task.id == task.id)
    )
    return db.scalar(stmt)


@router.get(
    "",
    response_model=PaginatedResponse[TaskResponse],
    summary="Listar tareas con filtros y paginación",
    description="""
    Lista las tareas del usuario autenticado con posibilidad de filtrar y paginar.

    **Filtros disponibles:**
    - `is_completed`: filtrar por estado (true/false)
    - `priority`: filtrar por prioridad (low/medium/high)
    - `category_id`: filtrar por categoría
    """,
)
@router.get("/", response_model=PaginatedResponse[TaskResponse], include_in_schema=False)
def list_tasks(
    pagination: PaginationParams = Depends(),
    is_completed: bool | None = Query(
        None, description="Filtrar por estado de completado"
    ),
    priority: TaskPriority | None = Query(
        None, description="Filtrar por prioridad"
    ),
    category_id: int | None = Query(None, description="Filtrar por categoría"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lista tareas del usuario con filtros y paginación usando sintaxis SQLAlchemy 2.0."""
    stmt = (
        select(Task)
        .options(joinedload(Task.category))
        .where(Task.owner_id == current_user.id)
    )
    count_stmt = (
        select(func.count())
        .select_from(Task)
        .where(Task.owner_id == current_user.id)
    )

    # Aplicar filtros
    if is_completed is not None:
        stmt = stmt.where(Task.is_completed == is_completed)
        count_stmt = count_stmt.where(Task.is_completed == is_completed)
    if priority is not None:
        stmt = stmt.where(Task.priority == priority)
        count_stmt = count_stmt.where(Task.priority == priority)
    if category_id is not None:
        stmt = stmt.where(Task.category_id == category_id)
        count_stmt = count_stmt.where(Task.category_id == category_id)

    total = db.scalar(count_stmt) or 0

    stmt = (
        stmt.order_by(Task.created_at.desc())
        .offset(pagination.skip)
        .limit(pagination.limit)
    )
    tasks = db.scalars(stmt).unique().all()

    return PaginatedResponse(
        items=list(tasks),
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Obtener una tarea por ID",
    description="Retorna los detalles completos de una tarea del usuario, incluyendo su categoría.",
    responses={
        404: {"description": "Tarea no encontrada"},
    },
)
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Obtiene una tarea por su ID verificando propiedad del usuario."""
    stmt = (
        select(Task)
        .options(joinedload(Task.category))
        .where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = db.scalar(stmt)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Actualizar una tarea",
    description="Actualiza los datos de una tarea existente del usuario autenticado.",
    responses={
        404: {"description": "Tarea no encontrada"},
    },
)
def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Actualiza una tarea existente."""
    stmt = (
        select(Task)
        .options(joinedload(Task.category))
        .where(Task.id == task_id, Task.owner_id == current_user.id)
    )
    task = db.scalar(stmt)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )

    # Validar categoría si se está actualizando
    if task_in.category_id is not None:
        cat_stmt = select(Category).where(
            Category.id == task_in.category_id,
            Category.owner_id == current_user.id,
        )
        category = db.scalar(cat_stmt)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with id {task_in.category_id} not found",
            )

    update_data = task_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)

    # Recargar con categoría
    stmt_reload = (
        select(Task)
        .options(joinedload(Task.category))
        .where(Task.id == task.id)
    )
    return db.scalar(stmt_reload)


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una tarea",
    description="Elimina permanentemente una tarea del usuario.",
    responses={
        204: {"description": "Tarea eliminada exitosamente"},
        404: {"description": "Tarea no encontrada"},
    },
)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Elimina una tarea."""
    stmt = select(Task).where(Task.id == task_id, Task.owner_id == current_user.id)
    task = db.scalar(stmt)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id {task_id} not found",
        )
    db.delete(task)
    db.commit()
    return None
