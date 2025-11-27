"""
Rutas de API para Autenticación
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from src.database import get_db
from src.api.services.auth_service import (
    AuthService, 
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from src.database.models import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


# -------------------------
# MODELOS PYDANTIC
# -------------------------

class UserRegister(BaseModel):
    """Modelo para registro de usuario"""
    email: EmailStr
    password: str
    name: str
    
    @field_validator('password')
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('La contraseña debe tener al menos 6 caracteres')
        return v
    
    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()


class UserLogin(BaseModel):
    """Modelo para login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Modelo de respuesta de token"""
    access_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """Modelo de respuesta de usuario"""
    id: str
    email: str
    name: str
    is_active: bool
    created_at: Optional[str]


# -------------------------
# ENDPOINTS
# -------------------------

@router.post("/register", response_model=Token)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db)
):
    """
    POST /api/auth/register - Registrar nuevo usuario
    
    Args:
        user_data: Datos del nuevo usuario (email, password, name)
        
    Returns:
        Token de acceso y datos del usuario
    """
    # Verificar si el email ya existe
    existing_user = AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    # Crear usuario
    user = AuthService.create_user(
        db,
        email=user_data.email,
        password=user_data.password,
        name=user_data.name
    )
    
    # Generar token
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    POST /api/auth/login - Iniciar sesión
    
    Args:
        credentials: Email y password
        
    Returns:
        Token de acceso y datos del usuario
    """
    user = AuthService.authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    # Generar token
    access_token = AuthService.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user.to_dict()
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/auth/me - Obtener información del usuario actual
    
    Requiere autenticación (Bearer token)
    
    Returns:
        Datos del usuario autenticado
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None
    }


@router.post("/logout")
def logout():
    """
    POST /api/auth/logout - Cerrar sesión
    
    Nota: Con JWT stateless, el logout se maneja en el cliente
    eliminando el token. Este endpoint es solo para consistencia.
    
    Returns:
        Mensaje de éxito
    """
    return {"message": "Sesión cerrada exitosamente"}
