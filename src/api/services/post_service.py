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
    def create_post(db: Session, title: str, content: str, user_id: Optional[UUID] = None) -> Post:
        """
        Crear un nuevo post
        
        Args:
            db: Sesión de base de datos
            title: Título del post
            content: Contenido del post
            user_id: ID del usuario propietario (opcional)
            
        Returns:
            Post creado
        """
        post = Post(
            title=title,
            content=content,
            status=PostStatus.DRAFT,
            user_id=user_id
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        return post

    @staticmethod
    def get_post(db: Session, post_id: UUID, user_id: Optional[UUID] = None) -> Optional[Post]:
        """
        Obtener un post por ID, opcionalmente verificando que pertenezca al usuario
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            user_id: ID del usuario (opcional, si se proporciona verifica propiedad)
            
        Returns:
            Post o None si no existe o no pertenece al usuario
        """
        query = db.query(Post).filter(Post.id == post_id)
        if user_id:
            query = query.filter(Post.user_id == user_id)
        return query.first()

    @staticmethod
    def get_post_by_user(db: Session, post_id: UUID, user_id: UUID) -> Optional[Post]:
        """
        Obtener un post por ID verificando que pertenezca al usuario
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            user_id: ID del usuario
            
        Returns:
            Post o None si no existe o no pertenece al usuario
        """
        return db.query(Post).filter(Post.id == post_id, Post.user_id == user_id).first()

    @staticmethod
    def get_posts(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: Optional[PostStatus] = None,
        user_id: Optional[UUID] = None
    ) -> List[Post]:
        """
        Listar posts con paginación
        
        Args:
            db: Sesión de base de datos
            skip: Número de posts a omitir
            limit: Máximo número de posts a retornar
            status: Filtrar por estado (opcional)
            user_id: Filtrar por usuario (opcional)
            
        Returns:
            Lista de posts
        """
        query = db.query(Post)
        
        if user_id:
            query = query.filter(Post.user_id == user_id)
        
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
