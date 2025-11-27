"""
Rutas de API para Posts
"""
import os
import uuid
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.database import get_db
from src.api.controllers.posts_controller import PostsController
from src.api.services.auth_service import get_current_user, get_current_user_optional
from src.database.models import User


router = APIRouter(prefix="/api/posts", tags=["Posts"])
controller = PostsController()


# -------------------------
# MODELOS PYDANTIC
# -------------------------

class CreatePostRequest(BaseModel):
    """Modelo para crear un post"""
    title: str
    content: str


class AdaptContentRequest(BaseModel):
    """Modelo para adaptar contenido"""
    networks: Optional[List[str]] = ["facebook", "instagram", "linkedin", "whatsapp"]
    preview_only: Optional[bool] = False


class PublishRequest(BaseModel):
    """Modelo para publicar en redes"""
    image_url: Optional[str] = None


# -------------------------
# ENDPOINTS
# -------------------------

@router.post("")
def create_post(
    request: CreatePostRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    POST /api/posts - Crear nuevo post
    
    Crea un post en estado 'draft' que puede ser adaptado y publicado posteriormente.
    Requiere autenticación.
    
    Args:
        request: Datos del post (title, content)
        
    Returns:
        Post creado con su ID
    """
    try:
        post = controller.create_post(db, request.title, request.content, current_user.id)
        return {
            "success": True,
            "message": "Post creado exitosamente",
            "data": post
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("")
def list_posts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/posts - Listar posts del usuario actual
    
    Lista todos los posts del usuario con paginación y filtro opcional por estado.
    Requiere autenticación.
    
    Query params:
        - skip: Número de posts a omitir (default: 0)
        - limit: Máximo de posts a retornar (default: 100)
        - status: Filtrar por estado (draft, processing, published, failed)
        
    Returns:
        Lista de posts del usuario
    """
    try:
        posts = controller.get_posts(db, skip, limit, status, current_user.id)
        return {
            "success": True,
            "count": len(posts),
            "data": posts
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{post_id}")
def get_post_details(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/posts/:id - Ver detalles de un post
    
    Obtiene los detalles completos de un post incluyendo todas sus publicaciones.
    Requiere autenticación y que el post pertenezca al usuario.
    
    Args:
        post_id: UUID del post
        
    Returns:
        Detalles del post con sus publicaciones
    """
    try:
        post = controller.get_post_details(db, post_id, current_user.id)
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        
        return {
            "success": True,
            "data": post
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{post_id}/adapt")
def adapt_content(
    post_id: UUID,
    request: AdaptContentRequest = AdaptContentRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    POST /api/posts/:id/adapt - Adaptar contenido con LLM
    
    Adapta el contenido del post para diferentes redes sociales usando IA.
    Crea registros de Publication en estado 'pending' para cada red.
    Requiere autenticación y que el post pertenezca al usuario.
    
    Args:
        post_id: UUID del post
        request: Configuración de adaptación
            - networks: Lista de redes (default: todas las soportadas)
              Opciones: ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
            - preview_only: Si es true, solo muestra preview sin guardar (default: false)
        
    Examples:
        # Adaptar para todas las redes (default)
        POST /api/posts/{id}/adapt
        {}
        
        # Adaptar solo para Facebook e Instagram
        POST /api/posts/{id}/adapt
        {"networks": ["facebook", "instagram"]}
        
        # Vista previa para LinkedIn
        POST /api/posts/{id}/adapt
        {"networks": ["linkedin"], "preview_only": true}
        
    Returns:
        Contenido adaptado para cada red social
    """
    try:
        # Validar redes soportadas
        valid_networks = ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
        invalid_networks = [n for n in request.networks if n not in valid_networks]
        
        if invalid_networks:
            raise HTTPException(
                status_code=400,
                detail=f"Redes no soportadas: {invalid_networks}. Válidas: {valid_networks}"
            )
        
        result = controller.adapt_content(
            db,
            post_id,
            request.networks,
            request.preview_only,
            current_user.id
        )
        
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        
        return {
            "success": True,
            "message": "Contenido adaptado exitosamente" if not request.preview_only else "Vista previa generada",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{post_id}/publish")
def publish_to_networks(
    post_id: UUID,
    request: PublishRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    POST /api/posts/:id/publish - Publicar en redes sociales
    
    Publica el contenido adaptado en todas las redes sociales configuradas.
    Las publicaciones se procesan de forma asíncrona usando Celery.
    Requiere autenticación y que el post pertenezca al usuario.
    
    Args:
        post_id: UUID del post
        request: Configuración de publicación
            - image_url: URL de imagen a usar (opcional)
        
    Returns:
        Estado de las tareas de publicación encoladas
    """
    try:
        result = controller.publish_to_networks(db, post_id, request.image_url, current_user.id)
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "message": "Publicaciones encoladas para procesamiento",
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{post_id}/status")
def get_publication_status(
    post_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    GET /api/posts/:id/status - Ver estado de publicaciones
    
    Obtiene el estado actual de todas las publicaciones de un post.
    Útil para verificar el progreso después de publicar.
    Requiere autenticación y que el post pertenezca al usuario.
    
    Args:
        post_id: UUID del post
        
    Returns:
        Estado detallado de todas las publicaciones
    """
    try:
        status = controller.get_publication_status(db, post_id, current_user.id)
        
        if "error" in status:
            raise HTTPException(status_code=404, detail=status["error"])
        
        return {
            "success": True,
            "data": status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    POST /api/posts/upload-image - Subir imagen local
    
    Recibe un archivo de imagen y lo guarda en el servidor,
    devolviendo la URL pública para usar en publicaciones.
    
    Args:
        file: Archivo de imagen a subir
        
    Returns:
        URL pública de la imagen subida
    """
    try:
        # Validar tipo de archivo
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser una imagen"
            )
        
        # Crear directorio si no existe
        upload_dir = "temp_images"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        file_extension = os.path.splitext(file.filename)[1] if file.filename else '.jpg'
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Guardar archivo
        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)
        
        # Construir URL pública (ajustar según tu configuración)
        # Para desarrollo local, usar ruta del servidor
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        public_url = f"{base_url}/{file_path}"
        
        return {
            "success": True,
            "data": {
                "url": public_url,
                "filename": unique_filename,
                "path": file_path
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al subir imagen: {str(e)}")


# Router para publicaciones individuales
publications_router = APIRouter(prefix="/api/publications", tags=["Publications"])


@publications_router.post("/{publication_id}/retry")
def retry_publication(
    publication_id: UUID,
    db: Session = Depends(get_db)
):
    """
    POST /api/publications/:id/retry - Reintentar publicación fallida
    
    Reintenta una publicación que falló anteriormente.
    
    Args:
        publication_id: UUID de la publicación a reintentar
        
    Returns:
        Estado actualizado de la publicación
    """
    try:
        from src.api.services.publication_service import PublicationService
        from src.database.models import PublicationStatus
        from src.queue.tasks import publish_to_network_task
        
        pub_service = PublicationService()
        
        # Obtener la publicación
        pub = pub_service.get_publication(db, publication_id)
        if not pub:
            raise HTTPException(status_code=404, detail="Publicación no encontrada")
        
        # Solo reintentar si está fallida o pendiente
        if pub.status not in [PublicationStatus.FAILED, PublicationStatus.PENDING]:
            raise HTTPException(
                status_code=400,
                detail=f"No se puede reintentar una publicación en estado '{pub.status.value}'"
            )
        
        # Encolar nuevamente la tarea
        task = publish_to_network_task.delay(
            str(pub.id),
            pub.network.value,
            pub.adapted_content,
            pub.extra_data.get('image_url') if pub.extra_data else None
        )
        
        # Actualizar estado a processing
        pub_service.update_publication_status(
            db,
            pub.id,
            PublicationStatus.PROCESSING,
            metadata={"task_id": task.id, "retry": True}
        )
        
        return {
            "success": True,
            "message": "Publicación reencolada para procesamiento",
            "data": {
                "publication_id": str(pub.id),
                "network": pub.network.value,
                "status": "processing",
                "task_id": task.id
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class GenerateImageFromTextRequest(BaseModel):
    """Modelo para generar imagen desde texto adaptado"""
    post_id: str
    network: str
    adapted_text: str  # El texto adaptado visible en el preview


@router.post("/generate-image")
async def generate_image_with_ai(request: GenerateImageFromTextRequest, db: Session = Depends(get_db)):
    """
    POST /api/posts/generate-image - Generar imagen con DALL-E
    
    Genera una imagen usando DALL-E basada en el texto adaptado del preview.
    
    Args:
        request: Post ID, red social y texto adaptado
        db: Sesión de base de datos
        
    Returns:
        URL de la imagen generada
    """
    try:
        from src.services.intelligent_publisher import IntelligentPublisher
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key no configurada"
            )
        
        # Obtener el post
        post = controller.get_post_details(db, UUID(request.post_id))
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        
        # Usar el texto adaptado para generar el prompt de la imagen
        adapted_text = request.adapted_text.strip()
        
        if not adapted_text:
            raise HTTPException(
                status_code=400,
                detail="El texto adaptado está vacío"
            )
        
        # Crear un prompt descriptivo basado en el texto adaptado
        # Limitamos el texto para el prompt de DALL-E
        text_for_prompt = adapted_text[:500] if len(adapted_text) > 500 else adapted_text
        
        image_prompt = f"""Crea una imagen profesional y atractiva para redes sociales que represente visualmente el siguiente contenido:

"{text_for_prompt}"

La imagen debe ser:
- Visualmente impactante y profesional
- Adecuada para {request.network}
- Sin texto superpuesto
- Colores vibrantes y composición clara
- Estilo moderno y limpio"""
        
        publisher = IntelligentPublisher(openai_api_key)
        
        # Generar imagen usando el texto adaptado como base
        # Esto devuelve la ruta local del archivo
        local_path = publisher._generate_and_save_image(image_prompt)
        
        if not local_path:
            raise HTTPException(
                status_code=500,
                detail="No se pudo generar la imagen"
            )
        
        # Construir URL para preview (localhost) y ruta local para publicación
        # La ruta local es relativa: temp_images/dalle_image_xxx.png
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        preview_url = f"{base_url}/{local_path}"
        
        return {
            "success": True,
            "data": {
                "url": preview_url,  # URL para mostrar en el frontend
                "local_path": local_path,  # Ruta local para publicación
                "prompt": image_prompt,
                "based_on": adapted_text[:100] + "..." if len(adapted_text) > 100 else adapted_text
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando imagen: {str(e)}")


class GenerateVideoFromTextRequest(BaseModel):
    """Modelo para generar video desde texto adaptado"""
    post_id: str
    network: str
    adapted_text: str  # El texto adaptado visible en el preview
    duration: Optional[int] = 4  # Duración en segundos (máximo 4)


@router.post("/generate-video")
async def generate_video_with_ai(request: GenerateVideoFromTextRequest, db: Session = Depends(get_db)):
    """
    POST /api/posts/generate-video - Generar video con Sora
    
    Genera un video usando Sora de OpenAI basado en el texto adaptado del preview.
    Máximo 4 segundos de duración.
    
    Args:
        request: Post ID, red social, texto adaptado y duración
        db: Sesión de base de datos
        
    Returns:
        URL del video generado y ruta local
    """
    try:
        from src.services.intelligent_publisher import IntelligentPublisher
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key no configurada"
            )
        
        # Obtener el post
        post = controller.get_post_details(db, UUID(request.post_id))
        if not post:
            raise HTTPException(status_code=404, detail="Post no encontrado")
        
        # Usar el texto adaptado para generar el prompt del video
        adapted_text = request.adapted_text.strip()
        
        if not adapted_text:
            raise HTTPException(
                status_code=400,
                detail="El texto adaptado está vacío"
            )
        
        # Crear un prompt descriptivo basado en el texto adaptado
        text_for_prompt = adapted_text[:500] if len(adapted_text) > 500 else adapted_text
        
        video_prompt = f"""Crea un video corto profesional y atractivo para redes sociales que represente visualmente el siguiente contenido:

"{text_for_prompt}"

El video debe ser:
- Visualmente impactante y profesional
- Adecuado para {request.network}
- Con movimiento suave y cinematográfico
- Colores vibrantes y composición clara
- Estilo moderno y limpio
- Sin texto superpuesto"""
        
        publisher = IntelligentPublisher(openai_api_key)
        
        # Limitar duración a máximo 4 segundos
        duration = min(request.duration or 4, 4)
        
        # Generar video usando el texto adaptado como base
        local_path = publisher._generate_and_save_video(video_prompt, duration)
        
        if not local_path:
            raise HTTPException(
                status_code=500,
                detail="No se pudo generar el video"
            )
        
        # Construir URL para preview
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        preview_url = f"{base_url}/{local_path}"
        
        return {
            "success": True,
            "data": {
                "url": preview_url,  # URL para mostrar en el frontend
                "local_path": local_path,  # Ruta local para publicación
                "prompt": video_prompt,
                "duration": duration,
                "based_on": adapted_text[:100] + "..." if len(adapted_text) > 100 else adapted_text
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando video: {str(e)}")


class PublishToTikTokRequest(BaseModel):
    """Modelo para publicar video en TikTok"""
    video_path: str  # Ruta local del video (temp_images/sora_video_xxx.mp4)
    title: str
    privacy_level: Optional[str] = "PUBLIC_TO_EVERYONE"
    disable_comment: Optional[bool] = False
    post_id: Optional[str] = None  # ID del post para actualizar estado


@router.post("/publish-to-tiktok")
async def publish_video_to_tiktok(request: PublishToTikTokRequest, db: Session = Depends(get_db)):
    """
    POST /api/posts/publish-to-tiktok - Publicar video en TikTok
    
    Envía un video local al backend de TikTok para publicación.
    
    Args:
        request: Datos del video y configuración de TikTok
        
    Returns:
        Resultado de la publicación en TikTok
    """
    import requests
    from src.api.services.publication_service import PublicationService
    from src.database.models import PublicationStatus
    
    pub_service = PublicationService()
    publication_id = None
    
    try:
        # Si tenemos post_id, buscar la publicación de TikTok asociada
        if request.post_id:
            try:
                from uuid import UUID as PyUUID
                post_uuid = PyUUID(request.post_id)
                publications = PublicationService.get_publications_by_post(db, post_uuid)
                tiktok_pub = next((p for p in publications if p.network.value == 'tiktok'), None)
                if tiktok_pub:
                    publication_id = tiktok_pub.id
                    # Marcar como procesando
                    PublicationService.update_publication_status(db, publication_id, PublicationStatus.PROCESSING)
            except Exception as e:
                import logging
                logging.warning(f"No se pudo obtener publicación de TikTok: {e}")
        
        # Verificar que el archivo existe
        if not os.path.exists(request.video_path):
            if publication_id:
                pub_service.update_publication_status(
                    db, publication_id, PublicationStatus.FAILED,
                    error_message=f"Video no encontrado: {request.video_path}"
                )
            raise HTTPException(
                status_code=404,
                detail=f"Video no encontrado: {request.video_path}"
            )
        
        # URL del backend de TikTok (host.docker.internal para acceder desde Docker al host)
        tiktok_api_url = os.getenv("TIKTOK_API_URL", "http://host.docker.internal:8001")
        
        # Abrir el archivo y enviarlo al backend de TikTok
        with open(request.video_path, 'rb') as video_file:
            files = {
                'video': (os.path.basename(request.video_path), video_file, 'video/mp4')
            }
            data = {
                'title': request.title,
                'privacy_level': request.privacy_level,
                'disable_comment': str(request.disable_comment).lower()
            }
            
            response = requests.post(
                f"{tiktok_api_url}/api/tiktok/upload",
                files=files,
                data=data,
                timeout=120  # 2 minutos de timeout para subida de video
            )
        
        if response.status_code != 200:
            error_detail = response.json() if response.text else "Error desconocido"
            if publication_id:
                pub_service.update_publication_status(
                    db, publication_id, PublicationStatus.FAILED,
                    error_message=f"Error del backend TikTok: {error_detail}"
                )
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error del backend TikTok: {error_detail}"
            )
        
        result = response.json()
        
        # Marcar como publicado si tenemos publication_id
        if publication_id:
            PublicationService.update_publication_status(
                db, publication_id, PublicationStatus.PUBLISHED,
                metadata=result
            )
            # Actualizar estado del post
            from src.queue.tasks import _update_post_status_after_publication
            _update_post_status_after_publication(db, publication_id)
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        if publication_id:
            PublicationService.update_publication_status(
                db, publication_id, PublicationStatus.FAILED,
                error_message=f"Error de conexión: {str(e)}"
            )
        raise HTTPException(
            status_code=503,
            detail=f"Error conectando con el backend de TikTok: {str(e)}"
        )
    except Exception as e:
        if publication_id:
            pub_service.update_publication_status(
                db, publication_id, PublicationStatus.FAILED,
                error_message=f"Error: {str(e)}"
            )
        raise HTTPException(status_code=500, detail=f"Error publicando en TikTok: {str(e)}")


@router.post("/upload-video-to-tiktok")
async def upload_and_publish_video_to_tiktok(
    video: UploadFile = File(...),
    title: str = Form("Video"),
    privacy_level: str = Form("PUBLIC_TO_EVERYONE"),
    disable_comment: str = Form("false"),
    post_id: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    POST /api/posts/upload-video-to-tiktok - Subir y publicar video en TikTok
    
    Recibe un archivo de video, lo guarda temporalmente y lo envía al backend de TikTok.
    
    Args:
        video: Archivo de video
        title: Título para TikTok
        privacy_level: Nivel de privacidad
        disable_comment: Deshabilitar comentarios
        post_id: ID del post para actualizar estado (opcional)
        
    Returns:
        Resultado de la publicación en TikTok
    """
    import requests
    from src.api.services.publication_service import PublicationService
    from src.database.models import PublicationStatus
    import logging
    
    logging.info(f"🎬 upload-video-to-tiktok llamado con post_id={post_id}")
    
    pub_service = PublicationService()
    publication_id = None
    
    try:
        # Si tenemos post_id, buscar la publicación de TikTok asociada
        if post_id:
            try:
                from uuid import UUID as PyUUID
                post_uuid = PyUUID(post_id)
                logging.info(f"🔍 Buscando publicaciones para post {post_uuid}")
                publications = PublicationService.get_publications_by_post(db, post_uuid)
                logging.info(f"📋 Publicaciones encontradas: {len(publications)}")
                for p in publications:
                    logging.info(f"  - {p.network.value}: {p.id} (status: {p.status.value})")
                tiktok_pub = next((p for p in publications if p.network.value == 'tiktok'), None)
                if tiktok_pub:
                    publication_id = tiktok_pub.id
                    logging.info(f"✅ Publicación TikTok encontrada: {publication_id}")
                    # Marcar como procesando
                    PublicationService.update_publication_status(db, publication_id, PublicationStatus.PROCESSING)
                    logging.info(f"🔄 Marcado como PROCESSING")
                else:
                    logging.warning(f"⚠️ No se encontró publicación de TikTok para post {post_id}")
            except Exception as e:
                logging.warning(f"❌ No se pudo obtener publicación de TikTok: {e}")
        else:
            logging.warning(f"⚠️ No se recibió post_id")
        # Validar tipo de archivo
        if not video.content_type or not video.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser un video"
            )
        
        # Crear directorio temporal si no existe
        temp_dir = "temp_images"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Guardar archivo temporalmente
        filename = f"upload_video_{uuid.uuid4().hex[:8]}.mp4"
        filepath = os.path.join(temp_dir, filename)
        
        with open(filepath, 'wb') as f:
            content = await video.read()
            f.write(content)
        
        # URL del backend de TikTok (host.docker.internal para acceder desde Docker al host)
        tiktok_api_url = os.getenv("TIKTOK_API_URL", "http://host.docker.internal:8001")
        
        # Enviar al backend de TikTok
        with open(filepath, 'rb') as video_file:
            files = {
                'video': (filename, video_file, 'video/mp4')
            }
            data = {
                'title': title,
                'privacy_level': privacy_level,
                'disable_comment': str(disable_comment).lower()
            }
            
            response = requests.post(
                f"{tiktok_api_url}/api/tiktok/upload",
                files=files,
                data=data,
                timeout=120
            )
        
        # Limpiar archivo temporal
        try:
            os.remove(filepath)
        except:
            pass
        
        if response.status_code != 200:
            error_detail = response.json() if response.text else "Error desconocido"
            # Marcar como fallido si tenemos publication_id
            if publication_id:
                pub_service.update_publication_status(
                    db, publication_id, PublicationStatus.FAILED,
                    error_message=f"Error del backend TikTok: {error_detail}"
                )
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Error del backend TikTok: {error_detail}"
            )
        
        result = response.json()
        logging.info(f"✅ TikTok respondió exitosamente: {result}")
        
        # Marcar como publicado si tenemos publication_id
        if publication_id:
            logging.info(f"📝 Actualizando publicación {publication_id} a PUBLISHED")
            PublicationService.update_publication_status(
                db, publication_id, PublicationStatus.PUBLISHED,
                metadata=result
            )
            logging.info(f"✅ Publicación actualizada a PUBLISHED")
            
            # Actualizar estado del post
            from src.queue.tasks import _update_post_status_after_publication
            _update_post_status_after_publication(db, publication_id)
        else:
            logging.warning(f"⚠️ No hay publication_id para actualizar estado")
        
        return {
            "success": True,
            "data": result
        }
        
    except HTTPException:
        raise
    except requests.exceptions.RequestException as e:
        import logging
        logging.error(f"❌ Error de conexión con TikTok backend: {e}")
        # Marcar como fallido si tenemos publication_id
        if publication_id:
            pub_service.update_publication_status(
                db, publication_id, PublicationStatus.FAILED,
                error_message=f"Error de conexión: {str(e)}"
            )
        raise HTTPException(
            status_code=503,
            detail=f"Error conectando con el backend de TikTok: {str(e)}"
        )
    except Exception as e:
        import logging
        logging.error(f"❌ Error general subiendo video a TikTok: {e}")
        # Marcar como fallido si tenemos publication_id
        if publication_id:
            pub_service.update_publication_status(
                db, publication_id, PublicationStatus.FAILED,
                error_message=f"Error: {str(e)}"
            )
        raise HTTPException(status_code=500, detail=f"Error subiendo video a TikTok: {str(e)}")

