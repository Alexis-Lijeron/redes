"""
Controlador de Posts - Lógica de negocio
"""
import os
from typing import List, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from src.database.models import Post, Publication, PostStatus, SocialNetwork, PublicationStatus
from src.api.services.post_service import PostService
from src.api.services.adaptation_service import AdaptationService
from src.api.services.publication_service import PublicationService


class PostsController:
    """Controlador para manejo de posts y publicaciones"""

    def __init__(self):
        """Inicializar controlador"""
        self.post_service = PostService()
        self.publication_service = PublicationService()
        
        # Obtener API key de OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if openai_api_key:
            self.adaptation_service = AdaptationService(openai_api_key)
        else:
            self.adaptation_service = None

    def create_post(self, db: Session, title: str, content: str) -> Dict:
        """
        Crear un nuevo post
        
        Args:
            db: Sesión de base de datos
            title: Título del post
            content: Contenido del post
            
        Returns:
            Diccionario con el post creado
        """
        post = self.post_service.create_post(db, title, content)
        return post.to_dict()

    def get_posts(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: str = None
    ) -> List[Dict]:
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
        status_enum = PostStatus(status) if status else None
        posts = self.post_service.get_posts(db, skip, limit, status_enum)
        return [post.to_dict() for post in posts]

    def get_post_details(self, db: Session, post_id: UUID) -> Dict:
        """
        Obtener detalles de un post con sus publicaciones
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            
        Returns:
            Diccionario con post y publicaciones
        """
        post = self.post_service.get_post(db, post_id)
        if not post:
            return None
        
        post_dict = post.to_dict()
        post_dict["publications"] = [
            pub.to_dict() for pub in post.publications
        ]
        
        return post_dict

    def adapt_content(
        self,
        db: Session,
        post_id: UUID,
        networks: List[str],
        preview_only: bool = False
    ) -> Dict:
        """
        Adaptar contenido de un post para diferentes redes sociales
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            networks: Lista de redes sociales
            preview_only: Si es True, solo muestra preview sin guardar
            
        Returns:
            Diccionario con adaptaciones
        """
        # Obtener post
        post = self.post_service.get_post(db, post_id)
        if not post:
            return {"error": "Post no encontrado"}
        
        if not self.adaptation_service:
            return {"error": "Servicio de adaptación no disponible"}
        
        # Generar adaptaciones
        if preview_only:
            adaptations = self.adaptation_service.preview_adaptations(
                post.title,
                post.content,
                networks
            )
            return {
                "post_id": str(post_id),
                "preview": adaptations
            }
        else:
            # Adaptar y crear publicaciones
            adaptations = self.adaptation_service.adapt_content(
                post.title,
                post.content,
                networks
            )
            
            publications = []
            for network, adapted_text in adaptations.items():
                try:
                    network_enum = SocialNetwork(network)
                    pub = self.publication_service.create_publication(
                        db,
                        post_id,
                        network_enum,
                        adapted_text
                    )
                    # Convertir a dict inmediatamente
                    pub_dict = {
                        "id": str(pub.id),
                        "network": pub.network.value,
                        "status": pub.status.value,
                        "adapted_content": pub.adapted_content,
                        "created_at": pub.created_at.isoformat() if pub.created_at else None
                    }
                    publications.append(pub_dict)
                except Exception as e:
                    print(f"Error creando publicación para {network}: {e}")
            
            # Actualizar estado del post
            self.post_service.update_post_status(db, post_id, PostStatus.PROCESSING)
            
            return {
                "post_id": str(post_id),
                "adaptations": adaptations,
                "publications": publications
            }

    def publish_to_networks(
        self,
        db: Session,
        post_id: UUID,
        image_url: str = None
    ) -> Dict:
        """
        Publicar contenido adaptado en las redes sociales
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            image_url: URL de imagen (opcional)
            
        Returns:
            Diccionario con resultados de publicación
        """
        # Obtener publicaciones pendientes
        post = self.post_service.get_post(db, post_id)
        if not post:
            return {"error": "Post no encontrado"}
        
        publications = self.publication_service.get_publications_by_post(db, post_id)
        
        if not publications:
            return {
                "error": "No hay publicaciones para este post",
                "hint": "Primero adapta el contenido usando POST /api/posts/:id/adapt"
            }
        
        results = []
        
        # Importar servicios de publicación
        from src.queue.tasks import publish_to_network_task
        
        for pub in publications:
            if pub.status == PublicationStatus.PENDING:
                try:
                    # Encolar tarea de publicación
                    task = publish_to_network_task.delay(
                        str(pub.id),
                        pub.network.value,
                        pub.adapted_content,
                        image_url
                    )
                    
                    # Actualizar estado a processing
                    self.publication_service.update_publication_status(
                        db,
                        pub.id,
                        PublicationStatus.PROCESSING,
                        metadata={"task_id": task.id}
                    )
                    
                    results.append({
                        "publication_id": str(pub.id),
                        "network": pub.network.value,
                        "status": "enqueued",
                        "task_id": task.id
                    })
                    
                except Exception as e:
                    self.publication_service.update_publication_status(
                        db,
                        pub.id,
                        PublicationStatus.FAILED,
                        error_message=str(e)
                    )
                    
                    results.append({
                        "publication_id": str(pub.id),
                        "network": pub.network.value,
                        "status": "failed",
                        "error": str(e)
                    })
        
        # Retornar solo datos primitivos, NO objetos SQLAlchemy
        return {
            "post_id": str(post_id),
            "total_publications": len(publications),
            "results": results
        }

    def get_publication_status(self, db: Session, post_id: UUID) -> Dict:
        """
        Obtener estado de publicaciones de un post
        
        Args:
            db: Sesión de base de datos
            post_id: ID del post
            
        Returns:
            Diccionario con estado de publicaciones
        """
        post = self.post_service.get_post(db, post_id)
        if not post:
            return {"error": "Post no encontrado"}
        
        publications = self.publication_service.get_publications_by_post(db, post_id)
        
        status_summary = {
            "post_id": str(post_id),
            "post_status": post.status.value,
            "total_publications": len(publications),
            "by_status": {
                "pending": 0,
                "processing": 0,
                "published": 0,
                "failed": 0
            },
            "publications": []
        }
        
        for pub in publications:
            status_summary["by_status"][pub.status.value] += 1
            status_summary["publications"].append({
                "id": str(pub.id),
                "network": pub.network.value,
                "status": pub.status.value,
                "published_at": pub.published_at.isoformat() if pub.published_at else None,
                "error_message": pub.error_message,
                "metadata": pub.extra_data if pub.extra_data else {}
            })
        
        return status_summary
