"""
Tareas de Celery para publicación en redes sociales
"""
import os
import asyncio
from uuid import UUID
from datetime import datetime
from celery import Task
from src.queue.celery_app import celery_app
from src.database import SessionLocal
from src.database.models import PublicationStatus
from src.api.services.publication_service import PublicationService


@celery_app.task(bind=True, max_retries=3)
def publish_to_network_task(
    self,
    publication_id: str,
    network: str,
    content: str,
    image_url: str = None
):
    """
    Tarea para publicar contenido en una red social
    
    Args:
        publication_id: UUID de la publicación
        network: Red social (facebook, instagram, linkedin, tiktok, whatsapp)
        content: Contenido adaptado
        image_url: URL de imagen (opcional)
        
    Returns:
        Resultado de la publicación
    """
    pub_service = PublicationService()
    
    # Crear una nueva sesión para esta tarea
    db = SessionLocal()
    
    try:
        # Actualizar estado a processing
        pub_service.update_publication_status(
            db,
            UUID(publication_id),
            PublicationStatus.PROCESSING
        )
        
        # Publicar según la red
        result = None
        
        if network == "facebook":
            result = _publish_to_facebook(content, image_url)
        elif network == "instagram":
            result = _publish_to_instagram(content, image_url)
        elif network == "linkedin":
            result = _publish_to_linkedin(content, image_url)
        elif network == "tiktok":
            result = _publish_to_tiktok(content, image_url)
        elif network == "whatsapp":
            result = _publish_to_whatsapp(content, image_url)
        else:
            raise ValueError(f"Red social no soportada: {network}")
        
        # Actualizar estado a published
        pub_service.update_publication_status(
            db,
            UUID(publication_id),
            PublicationStatus.PUBLISHED,
            metadata=result
        )
        
        # Actualizar estado del post
        _update_post_status_after_publication(db, UUID(publication_id))
        
        return {
            "status": "success",
            "publication_id": publication_id,
            "network": network,
            "result": result
        }
        
    except Exception as exc:
        # Actualizar estado a failed
        try:
            pub_service.update_publication_status(
                db,
                UUID(publication_id),
                PublicationStatus.FAILED,
                error_message=str(exc)
            )
            # Actualizar estado del post
            _update_post_status_after_publication(db, UUID(publication_id))
        except:
            pass  # Si falla el update, continuar
        
        # Reintentar en caso de error
        raise self.retry(exc=exc, countdown=60)  # Reintentar en 1 minuto
    
    finally:
        # Siempre cerrar la sesión
        db.close()


def _update_post_status_after_publication(db, publication_id: UUID):
    """
    Actualizar el estado del post basándose en el estado de sus publicaciones
    
    Args:
        db: Sesión de base de datos
        publication_id: UUID de la publicación que acaba de actualizarse
    """
    from src.api.services.post_service import PostService
    from src.database.models import PostStatus
    import logging
    
    try:
        logging.info(f"📊 Actualizando estado del post para publicación {publication_id}")
        
        # Obtener la publicación para saber a qué post pertenece
        publication = PublicationService.get_publication(db, publication_id)
        if not publication:
            logging.warning(f"⚠️ No se encontró publicación {publication_id}")
            return
        
        post_id = publication.post_id
        logging.info(f"📋 Post ID: {post_id}")
        
        # Obtener todas las publicaciones del post
        publications = PublicationService.get_publications_by_post(db, post_id)
        
        if not publications:
            logging.warning(f"⚠️ No hay publicaciones para post {post_id}")
            return
        
        # Contar estados
        total = len(publications)
        published = sum(1 for p in publications if p.status == PublicationStatus.PUBLISHED)
        failed = sum(1 for p in publications if p.status == PublicationStatus.FAILED)
        processing = sum(1 for p in publications if p.status == PublicationStatus.PROCESSING)
        pending = sum(1 for p in publications if p.status == PublicationStatus.PENDING)
        
        logging.info(f"📈 Estados: total={total}, published={published}, failed={failed}, processing={processing}, pending={pending}")
        
        # Determinar nuevo estado del post
        new_status = None
        
        if published == total:
            # Todas publicadas exitosamente
            new_status = PostStatus.PUBLISHED
        elif failed == total:
            # Todas fallaron
            new_status = PostStatus.FAILED
        elif processing > 0 or pending > 0:
            # Aún hay publicaciones en proceso o pendientes
            new_status = PostStatus.PROCESSING
        elif published > 0:
            # Algunas publicadas, otras fallidas
            new_status = PostStatus.PUBLISHED
        elif failed > 0:
            # Solo hay fallidas (y ninguna pendiente/procesando)
            new_status = PostStatus.FAILED
        
        # Actualizar estado del post si cambió
        if new_status:
            logging.info(f"✅ Actualizando estado del post a: {new_status}")
            PostService.update_post_status(db, post_id, new_status)
        else:
            logging.warning(f"⚠️ No se determinó nuevo estado para el post")
            
    except Exception as e:
        import logging
        logging.error(f"❌ Error actualizando estado del post: {e}")
        import traceback
        traceback.print_exc()
        # No propagar el error para no afectar la publicación


def _publish_to_facebook(content: str, image_url: str = None):
    """Publicar en Facebook"""
    from src.services.facebook_service import facebook_post_image, facebook_post_text
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"📘 Facebook - Publicando con image_url: {image_url}")
        if image_url:
            result = facebook_post_image(image_url, content)
            logger.info(f"📘 Facebook - Resultado: {result}")
        else:
            result = facebook_post_text(content)
        
        return {
            "platform": "facebook",
            "post_id": result.get("id"),
            "response": result
        }
    except Exception as e:
        raise Exception(f"Error publicando en Facebook: {str(e)}")


def _publish_to_instagram(content: str, image_url: str = None):
    """Publicar en Instagram"""
    from src.services.instagram_service import instagram_create_media, instagram_publish_media
    
    try:
        if not image_url:
            raise ValueError("Instagram requiere una imagen")
        
        # Crear media
        creation = instagram_create_media(image_url, content)
        if "id" not in creation:
            raise Exception(f"Error creando media: {creation}")
        
        creation_id = creation["id"]
        
        # Publicar
        publish_result = instagram_publish_media(creation_id)
        
        return {
            "platform": "instagram",
            "creation_id": creation_id,
            "post_id": publish_result.get("id"),
            "response": publish_result
        }
    except Exception as e:
        raise Exception(f"Error publicando en Instagram: {str(e)}")


def _publish_to_linkedin(content: str, image_url: str = None):
    """Publicar en LinkedIn"""
    from src.services.linkedin_service import linkedin_post_image, linkedin_post_text
    
    try:
        if image_url:
            result = linkedin_post_image(content, image_url)
        else:
            result = linkedin_post_text(content)
        
        return {
            "platform": "linkedin",
            "post_id": result.get("id"),
            "response": result
        }
    except Exception as e:
        raise Exception(f"Error publicando en LinkedIn: {str(e)}")


def _publish_to_tiktok(content: str, image_url: str = None):
    """Publicar en TikTok usando el backend externo"""
    import requests
    import os
    
    # TikTok requiere un video, no imagen
    # Si solo tenemos imagen o texto, no podemos publicar en TikTok directamente
    if not image_url:
        raise ValueError("TikTok requiere un video para publicar. Usa la opción de generar video con IA o sube un video.")
    
    # Si la URL es un video local (ruta de archivo)
    if image_url.startswith('temp_images/') or image_url.startswith('./temp_images/'):
        video_path = image_url
    elif os.path.exists(image_url):
        video_path = image_url
    else:
        # Si es una URL remota de video, descargarla primero
        raise ValueError("TikTok requiere un video local. Genera un video con IA o sube uno desde tu computadora.")
    
    try:
        # URL del backend de TikTok (host.docker.internal para acceder desde Docker al host)
        tiktok_api_url = os.getenv("TIKTOK_API_URL", "http://host.docker.internal:8001")
        
        # Abrir el archivo y enviarlo al backend de TikTok
        with open(video_path, 'rb') as video_file:
            files = {
                'video': (os.path.basename(video_path), video_file, 'video/mp4')
            }
            data = {
                'title': content[:150] if len(content) > 150 else content,  # TikTok limita el título
                'privacy_level': 'PUBLIC_TO_EVERYONE',
                'disable_comment': 'false'
            }
            
            response = requests.post(
                f"{tiktok_api_url}/api/tiktok/upload",
                files=files,
                data=data,
                timeout=120
            )
        
        if response.status_code != 200:
            error_detail = response.json() if response.text else "Error desconocido"
            raise Exception(f"Error del backend TikTok: {error_detail}")
        
        result = response.json()
        
        return {
            "platform": "tiktok",
            "response": result
        }
    except Exception as e:
        raise Exception(f"Error publicando en TikTok: {str(e)}")


def _publish_to_whatsapp(content: str, image_url: str = None):
    """Publicar en WhatsApp"""
    from src.services.whatsapp_service import whatsapp_post_story_from_url
    
    try:
        if not image_url:
            raise ValueError("WhatsApp requiere una imagen o video")
        
        # Ejecutar la función asíncrona
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            whatsapp_post_story_from_url(image_url, content)
        )
        loop.close()
        
        if result.get("status") == "error":
            raise Exception(result.get("detail", "Error desconocido"))
        
        return {
            "platform": "whatsapp",
            "response": result.get("data", result)
        }
    except Exception as e:
        raise Exception(f"Error publicando en WhatsApp: {str(e)}")
