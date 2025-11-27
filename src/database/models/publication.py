"""
Modelo de Publication - Publicación en una red social específica
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.database.database import Base
import enum


class SocialNetwork(str, enum.Enum):
    """Redes sociales soportadas"""
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    WHATSAPP = "whatsapp"


class PublicationStatus(str, enum.Enum):
    """Estados posibles de una publicación"""
    PENDING = "pending"
    PROCESSING = "processing"
    PUBLISHED = "published"
    FAILED = "failed"


class Publication(Base):
    """
    Modelo de Publication - Representa una publicación en una red social específica
    """
    __tablename__ = "publications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey("posts.id"), nullable=False)
    network = Column(SQLEnum(SocialNetwork), nullable=False)
    adapted_content = Column(Text)
    status = Column(
        SQLEnum(PublicationStatus),
        default=PublicationStatus.PENDING,
        nullable=False
    )
    published_at = Column(DateTime)
    error_message = Column(Text)
    extra_data = Column(JSONB, default=dict)  # IDs de publicación, URLs, etc.
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación con post
    post = relationship("Post", back_populates="publications")

    def __repr__(self):
        return f"<Publication(id={self.id}, network={self.network}, status={self.status})>"

    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            "id": str(self.id),
            "post_id": str(self.post_id),
            "network": self.network.value,
            "adapted_content": self.adapted_content,
            "status": self.status.value,
            "published_at": self.published_at.isoformat() if self.published_at else None,
            "error_message": self.error_message,
            "metadata": self.extra_data,  # Usar extra_data internamente pero exponer como metadata
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
