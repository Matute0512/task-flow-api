from collections.abc import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

from app.core.config import settings

# Crear el engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={
        "check_same_thread": False
    } if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,  # Muestra queries SQL en desarrollo
    pool_pre_ping=True,
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Clase base para todos los modelos
class Base(DeclarativeBase):
    pass


# Dependencia para obtener la sesión de BD
def get_db() -> Generator[Session, None, None]:
    """
    Generador que proporciona una sesión de base de datos con rollback automático.
    Se usa como dependencia en FastAPI para inyectar la BD en los endpoints.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
