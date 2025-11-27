"""
Servicio para manejo de Posts
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import Post, PostStatus


class PostService:
    """Servicio para operaciones CRUD de Posts"""

    @staticmethod
    def create_post(db: Session, title: str, content: str) -> Post:
        """
        Crear un nuevo post
        
        Args:
            db: Sesión de base de datos
            title: Título del post
            content: Contenido del post
            
        Returns:
            Post creado
        """
        post = Post(
            title=title,
            content=content,
            status=PostStatus.DRAFT
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def get_post(db: Session, post_id: UUID) -> Optional[Post]:
        """
        Obtener un post por ID
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            
        Returns:
            Post o None si no existe
        """
        return db.query(Post).filter(Post.id == post_id).first()

    @staticmethod
    def get_posts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PostStatus] = None
    ) -> List[Post]:
        """
        Listar posts con paginación
        
        Args:
            db: Sesión de base de datos
            skip: Número de posts a omitir
            limit: Máximo número de posts a retornar
            status: Filtrar por estado (opcional)
            
        Returns:
            Lista de posts
        """
        query = db.query(Post)
        
        if status:
            query = query.filter(Post.status == status)
        
        return query.order_by(Post.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_post_status(db: Session, post_id: UUID, status: PostStatus) -> Optional[Post]:
        """
        Actualizar el estado de un post
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            status: Nuevo estado
            
        Returns:
            Post actualizado o None si no existe
        """
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            post.status = status
            db.commit()
            db.refresh(post)
        return post

    @staticmethod
    def delete_post(db: Session, post_id: UUID) -> bool:
        """
        Eliminar un post
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            
        Returns:
            True si se eliminó, False si no existía
        """
        post = db.query(Post).filter(Post.id == post_id).first()
        if post:
            db.delete(post)
            db.commit()
            return True
        return False
