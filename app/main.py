from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, categories, tasks

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## TaskFlow API

API profesional para gestión de tareas con categorías y autenticación JWT.

### Características:

- **Autenticación** con JWT tokens.
- **CRUD Completo** de usuarios, categorías y tareas.
- **Documentación interactiva** en `/docs` (Swagger) y `/redoc` (ReDoc).
""",
    contact={
        "name": "Matías Torres",
        "email": "matiastorres678@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {"name": "Auth", "description": "Operaciones de autenticación y tokens JWT"},
        {"name": "Categories", "description": "Gestión de categorías de tareas"},
        {"name": "Tasks", "description": "Gestión de tareas con filtros y paginación"},
        {"name": "Root", "description": "Endpoints raíz de la API"},
    ],
)

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(tasks.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Endpoint raíz - Verifica que la API está funcionando."""
    return {
        "message": "Bienvenido a TaskFlow API",
        "docs": "/docs",
        "version": settings.APP_VERSION,
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Endpoint de salud - Usado por Docker/Kubernetes."""
    return {"status": "healthy"}
