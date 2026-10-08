from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

# Crear el engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,  # Muestra queries SQL en desarrollo
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Clase base para todos los modelos
class Base(DeclarativeBase):
    pass


# Dependencia para obtener la sesión de BD
def get_db():
    """
    Generador que proporciona una sesión de base de datos.
    Se usa como dependencia en FastAPI para inyectar la BD en los endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
