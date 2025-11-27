"""
Modelo de Post - Contenido original a publicar
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.database.database import Base
import enum


class PostStatus(str, enum.Enum):
    """Estados posibles de un post"""
    DRAFT = "draft"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"


class Post(Base):
    """
    Modelo de Post - Representa el contenido original a adaptar y publicar
    """
    __tablename__ = "posts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # nullable=True para migración
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(
        SQLEnum(PostStatus),
        default=PostStatus.DRAFT,
        nullable=False
    )

    # Relación con usuario
    user = relationship("User", back_populates="posts")
    
    # Relación con publicaciones
    publications = relationship(
        "Publication",
        back_populates="post",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Post(id={self.id}, title='{self.title[:30]}...', status={self.status})>"

    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "status": self.status.value,
            "publications_count": len(self.publications) if self.publications else 0
        }
