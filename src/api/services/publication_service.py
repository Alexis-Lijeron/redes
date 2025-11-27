"""
Servicio para manejo de Publications
"""
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from src.database.models import Publication, SocialNetwork, PublicationStatus


class PublicationService:
    """Servicio para operaciones CRUD de Publications"""

    @staticmethod
    def create_publication(
        db: Session,
        post_id: UUID,
        network: SocialNetwork,
        adapted_content: str
    ) -> Publication:
        """
        Crear una nueva publicación
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post original
            network: Red social
            adapted_content: Contenido adaptado para la red
            
        Returns:
            Publication creada
        """
        publication = Publication(
            post_id=post_id,
            network=network,
            adapted_content=adapted_content,
            status=PublicationStatus.PENDING
        )
        db.add(publication)
        db.commit()
        db.refresh(publication)
        return publication

    @staticmethod
    def get_publication(db: Session, publication_id: UUID) -> Optional[Publication]:
        """
        Obtener una publicación por ID
        
        Args:
            db: Sesión de base de datos
            publication_id: ID de la publicación
            
        Returns:
            Publication o None si no existe
        """
        return db.query(Publication).filter(Publication.id == publication_id).first()

    @staticmethod
    def get_publications_by_post(db: Session, post_id: UUID) -> List[Publication]:
        """
        Obtener todas las publicaciones de un post
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            
        Returns:
            Lista de publicaciones
        """
        from sqlalchemy.orm import lazyload
        
        # Usar lazyload para evitar cargar relaciones
        publications = db.query(Publication).options(
            lazyload(Publication.post)
        ).filter(Publication.post_id == post_id).all()
        
        return publications

    @staticmethod
    def update_publication_status(
        db: Session,
        publication_id: UUID,
        status: PublicationStatus,
        error_message: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> Optional[Publication]:
        """
        Actualizar el estado de una publicación
        
        Args:
            db: Sesión de base de datos
            publication_id: ID de la publicación
            status: Nuevo estado
            error_message: Mensaje de error (opcional)
            metadata: Metadata adicional (opcional)
            
        Returns:
            Publication actualizada o None si no existe
        """
        publication = db.query(Publication).filter(
            Publication.id == publication_id
        ).first()
        
        if publication:
            publication.status = status
            
            if status == PublicationStatus.PUBLISHED:
                publication.published_at = datetime.utcnow()
            
            if error_message:
                publication.error_message = error_message
            
            if metadata:
                publication.extra_data = metadata
            
            db.commit()
            db.refresh(publication)
        
        return publication

    @staticmethod
    def get_publications_by_status(
        db: Session,
        status: PublicationStatus
    ) -> List[Publication]:
        """
        Obtener publicaciones por estado
        
        Args:
            db: Sesión de base de datos
            status: Estado a filtrar
            
        Returns:
            Lista de publicaciones
        """
        return db.query(Publication).filter(Publication.status == status).all()
