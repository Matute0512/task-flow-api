from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

# Creamos la app con metadatos profesionales para OpenAPI
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
## TaskFlow API

API profesional para gestion de tareas con categorías y  autenticación JWT.

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
        {"name": "Auth", "description": "Operaciones de autenticación"},
        {"name": "Users", "description": "Gestión de Usuarios"},
        {"name": "Categories", "description": "Gestión de categorías de tareas"},
        {"name": "Tasks", "description": "Gestión de tareas"},
    ],
)

# Configuración CORS (permite que un frontend se conecte)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],    # En producción, especifica dominios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
