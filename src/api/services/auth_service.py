"""
Servicio de Autenticación - Manejo de usuarios, JWT y passwords
"""
import os
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.database.models import User
from src.database import get_db

# Configuración de JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "tu-super-secreto-cambiar-en-produccion-123456")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 días

# Configuración de password hashing - usar sha256_crypt que es más compatible
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# Security scheme
security = HTTPBearer()


class AuthService:
    """Servicio de autenticación"""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verificar password contra hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generar hash de password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crear token JWT"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decodificar y validar token JWT"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: UUID) -> Optional[User]:
        """Obtener usuario por ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create_user(db: Session, email: str, password: str, name: str) -> User:
        """Crear nuevo usuario"""
        hashed_password = AuthService.get_password_hash(password)
        user = User(
            email=email,
            password_hash=hashed_password,
            name=name
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Autenticar usuario con email y password"""
        user = AuthService.get_user_by_email(db, email)
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obtener el usuario actual desde el token JWT.
    Usar como dependencia en endpoints protegidos.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user = AuthService.get_user_by_id(db, UUID(user_id))
    except:
        raise credentials_exception
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo"
        )
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency opcional para obtener el usuario actual.
    Retorna None si no hay token válido.
    """
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    if payload is None:
        return None
    
    user_id: str = payload.get("sub")
    if user_id is None:
        return None
    
    try:
        user = AuthService.get_user_by_id(db, UUID(user_id))
        return user if user and user.is_active else None
    except:
        return None
