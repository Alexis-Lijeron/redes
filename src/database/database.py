"""
Configuración de base de datos con SQLAlchemy
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# URL de conexión a PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/social_media_publisher"
)

# Crear engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verificar conexión antes de usar
    echo=True  # Mostrar SQL queries en desarrollo
)

# Crear SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()


def get_db():
    """
    Dependency para obtener sesión de base de datos.
    Se usa en FastAPI como dependencia.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
