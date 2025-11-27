import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
from src.services.instagram_service import (
    instagram_create_media,
    instagram_publish_media
)
from src.services.facebook_service import (
    facebook_post_text,
    facebook_post_image
)
from src.services.linkedin_service import (
    linkedin_post_text,
    linkedin_post_image
)
from src.services.whatsapp_service import (
    whatsapp_post_story,
    whatsapp_post_story_from_url
)
from src.services.content_publisher import ContentPublisher
from src.services.intelligent_publisher import IntelligentPublisher
from src.api.routes.posts_routes import router as posts_router, publications_router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Social Media Publisher API",
    description="API completa para gestión y publicación automatizada en redes sociales con IA",
    version="2.0.0"
)

# Montar directorio de imágenes estáticas
if not os.path.exists("temp_images"):
    os.makedirs("temp_images")
app.mount("/temp_images", StaticFiles(directory="temp_images"), name="temp_images")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React dev server alternativo
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# Incluir routers
app.include_router(posts_router)
app.include_router(publications_router)

# -------------------------
# MODELOS DE REQUEST
# -------------------------
class InstagramPost(BaseModel):
    image_url: str
    caption: str


class FacebookText(BaseModel):
    message: str


class FacebookImage(BaseModel):
    image_url: str
    caption: str


class LinkedInText(BaseModel):
    message: str


class LinkedInImage(BaseModel):
    image_url: str
    message: str


class WhatsAppStory(BaseModel):
    media_path: str
    caption: str
    exclude_contacts: Optional[List[str]] = []


class WhatsAppStoryFromUrl(BaseModel):
    media_url: str
    caption: str
    exclude_contacts: Optional[List[str]] = []


class ContentGenerationRequest(BaseModel):
    """Modelo para generar contenido con LLM"""
    heading: str
    material: str
    platforms: List[str] = ["facebook", "instagram"]
    auto_publish: bool = False
    image_url: Optional[str] = None


class ContentPreviewRequest(BaseModel):
    """Modelo para vista previa de contenido"""
    heading: str
    material: str
    platforms: List[str] = ["facebook", "instagram"]


class NaturalCommandRequest(BaseModel):
    """Modelo para comando en lenguaje natural"""
    command: str
    test_mode: bool = False  # Si es True, solo genera contenido sin publicar


# -------------------------
#  ENDPOINT: PUBLICAR EN INSTAGRAM
# -------------------------
@app.post("/publish/instagram")
def publish_instagram(data: InstagramPost):
    """
    Publica una imagen en Instagram.
    
    Args:
        data (InstagramPost): Datos de la publicación (image_url, caption)
        
    Returns:
        dict: Resultado de la publicación en Instagram
    """
    # 1) Crear contenedor
    creation = instagram_create_media(data.image_url, data.caption)

    if "id" not in creation:
        return {"error": "No se pudo crear el media", "details": creation}

    creation_id = creation["id"]

    # 2) Publicar
    publish = instagram_publish_media(creation_id)

    return {
        "status": "Publicado en Instagram",
        "creation_id": creation_id,
        "publish_response": publish
    }


# -------------------------
#  ENDPOINT: PUBLICAR TEXTO EN FACEBOOK
# -------------------------
@app.post("/publish/facebook/text")
def publish_facebook_text(data: FacebookText):
    """
    Publica un mensaje de texto en Facebook.
    
    Args:
        data (FacebookText): Datos del mensaje (message)
        
    Returns:
        dict: Resultado de la publicación en Facebook
    """
    result = facebook_post_text(data.message)
    return {"status": "Publicado en Facebook", "response": result}


# -------------------------
#  ENDPOINT: PUBLICAR IMAGEN EN FACEBOOK
# -------------------------
@app.post("/publish/facebook/image")
def publish_facebook_image(data: FacebookImage):
    """
    Publica una imagen con caption en Facebook.
    
    Args:
        data (FacebookImage): Datos de la imagen (image_url, caption)
        
    Returns:
        dict: Resultado de la publicación en Facebook
    """
    result = facebook_post_image(data.image_url, data.caption)
    return {"status": "Publicado en Facebook", "response": result}


# -------------------------
#  ENDPOINT: PUBLICAR TEXTO EN LINKEDIN
# -------------------------
@app.post("/publish/linkedin/text")
def publish_linkedin_text(data: LinkedInText):
    """
    Publica un mensaje de texto en LinkedIn.
    
    Args:
        data (LinkedInText): Datos del mensaje (message)
        
    Returns:
        dict: Resultado de la publicación en LinkedIn
    """
    result = linkedin_post_text(data.message)
    return {"status": "Publicado en LinkedIn", "response": result}


# -------------------------
#  ENDPOINT: PUBLICAR IMAGEN EN LINKEDIN
# -------------------------
@app.post("/publish/linkedin/image")
def publish_linkedin_image(data: LinkedInImage):
    """
    Publica una imagen con mensaje en LinkedIn.
    
    Args:
        data (LinkedInImage): Datos de la imagen (image_url, message)
        
    Returns:
        dict: Resultado de la publicación en LinkedIn
    """
    result = linkedin_post_image(data.message, data.image_url)
    return {"status": "Publicado en LinkedIn", "response": result}


# -------------------------
#  ENDPOINT: PUBLICAR ESTADO EN WHATSAPP
# -------------------------
@app.post("/publish/whatsapp/story")
async def publish_whatsapp_story(data: WhatsAppStory):
    """
    Publica un estado (story) en WhatsApp con imagen o video.
    
    Args:
        data (WhatsAppStory): Datos del estado (media_path, caption, exclude_contacts)
        
    Returns:
        dict: Resultado de la publicación en WhatsApp
    """
    try:
        result = await whatsapp_post_story(
            media_path=data.media_path,
            caption=data.caption,
            exclude_contacts=data.exclude_contacts
        )
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=result.get("status_code", 500),
                detail=result.get("detail", "Error al publicar estado")
            )
        
        return {
            "status": "Publicado en WhatsApp",
            "response": result
        }
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
#  ENDPOINT: PUBLICAR ESTADO EN WHATSAPP DESDE URL
# -------------------------
@app.post("/publish/whatsapp/story-from-url")
async def publish_whatsapp_story_url(data: WhatsAppStoryFromUrl):
    """
    Publica un estado en WhatsApp descargando la imagen/video de una URL.
    
    Args:
        data (WhatsAppStoryFromUrl): Datos del estado (media_url, caption, exclude_contacts)
        
    Returns:
        dict: Resultado de la publicación en WhatsApp
    """
    try:
        result = await whatsapp_post_story_from_url(
            media_url=data.media_url,
            caption=data.caption,
            exclude_contacts=data.exclude_contacts
        )
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=result.get("status_code", 500),
                detail=result.get("detail", "Error al publicar estado")
            )
        
        return {
            "status": "Publicado en WhatsApp",
            "response": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------
#  ENDPOINTS CON LLM INTEGRATION
# -------------------------
@app.post("/generate-content")
def generate_content_with_llm(data: ContentGenerationRequest):
    """
    Genera contenido optimizado usando LLM y opcionalmente lo publica.
    
    Args:
        data: Datos de la solicitud incluyendo heading, material, plataformas
        
    Returns:
        dict: Contenido generado y resultados de publicación (si aplica)
    """
    try:
        # Obtener clave API de OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY no configurada en variables de entorno"
            )
        
        # Crear publisher
        publisher = ContentPublisher(openai_api_key)
        
        # Generar y opcionalmente publicar contenido
        result = publisher.generate_and_publish(
            heading=data.heading,
            material=data.material,
            platforms=data.platforms,
            auto_publish=data.auto_publish,
            image_url=data.image_url
        )
        
        return {
            "success": True,
            "message": "Contenido generado exitosamente" + 
                      (" y publicado" if data.auto_publish else ""),
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/preview-content")
def preview_content_with_llm(data: ContentPreviewRequest):
    """
    Genera vista previa del contenido sin publicar.
    
    Args:
        data: Datos de la solicitud para vista previa
        
    Returns:
        dict: Vista previa del contenido generado con sugerencias de imagen
    """
    try:
        # Obtener clave API de OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY no configurada en variables de entorno"
            )
        
        # Crear publisher
        publisher = ContentPublisher(openai_api_key)
        
        # Generar vista previa
        result = publisher.preview_content(
            heading=data.heading,
            material=data.material,
            platforms=data.platforms
        )
        
        return {
            "success": True,
            "message": "Vista previa generada exitosamente",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/smart-publish")
def smart_publish(data: NaturalCommandRequest):
    """
    🤖 ENDPOINT INTELIGENTE - Procesa comandos en lenguaje natural
    
    Simplemente dile qué quieres publicar y dónde:
    - "Quiero publicar en Instagram sobre nuestro nuevo café con una imagen moderna"
    - "Publica en Facebook e Instagram sobre el evento de mañana"
    - "Crea un post para Instagram sobre tecnología con imagen futurista"
    
    El sistema automáticamente:
    1. Analiza tu comando
    2. Genera contenido optimizado para cada plataforma
    3. Crea una imagen con DALL-E si es necesario
    4. Publica automáticamente en las redes sociales especificadas
    
    Args:
        data: Comando en lenguaje natural
        
    Returns:
        dict: Resultado completo de la operación automática
    """
    try:
        # Obtener clave API de OpenAI
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise HTTPException(
                status_code=500, 
                detail="OPENAI_API_KEY no configurada en variables de entorno"
            )
        
        # Crear publisher inteligente
        smart_publisher = IntelligentPublisher(openai_api_key)
        
        # Procesar comando en lenguaje natural
        if data.test_mode:
            # Solo generar contenido sin publicar
            result = smart_publisher.process_natural_command_test_mode(data.command)
        else:
            # Generar y publicar
            result = smart_publisher.process_natural_command(data.command)
        
        return {
            "success": result.get("success", False),
            "message": "Comando procesado por IA exitosamente" if result.get("success") else "Error procesando comando",
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))





@app.get("/")
def root():
    """Endpoint raíz de la API."""
    return {
        "message": "Meta Publisher API - Generación con LLM y Publicación Automática",
        "features": [
            "Generación automática de contenido con OpenAI GPT",
            "Optimización por plataforma (Facebook, Instagram, LinkedIn)",
            "Publicación automática en múltiples redes sociales",
            "Vista previa antes de publicar",
            "Sugerencias de imagen generadas por IA",
            "Comandos inteligentes en lenguaje natural"
        ],
        "endpoints": {
            "/smart-publish": "🤖 Comando inteligente en lenguaje natural con DALL-E",
            "/generate-content": "Generar y publicar contenido",
            "/preview-content": "Vista previa del contenido",
            "/publish/instagram": "Publicar directamente en Instagram",
            "/publish/facebook/text": "Publicar texto en Facebook",
            "/publish/facebook/image": "Publicar imagen en Facebook",
            "/publish/linkedin/text": "Publicar texto en LinkedIn",
            "/publish/linkedin/image": "Publicar imagen en LinkedIn",
            "/publish/whatsapp/story": "Publicar estado en WhatsApp con archivo local",
            "/publish/whatsapp/story-from-url": "Publicar estado en WhatsApp desde URL",
            "/diagnostics": "Diagnóstico de configuración"
        },
        "smart_examples": [
            "Quiero publicar en Instagram sobre nuestro nuevo producto con imagen moderna",
            "Publica en Facebook e Instagram sobre el evento de tecnología", 
            "Crea un post para LinkedIn sobre nuestra empresa con imagen profesional",
            "Comparte en todas las redes sociales sobre nuestro lanzamiento",
            "Publica en LinkedIn sobre innovación tecnológica"
        ]
    }


@app.get("/diagnostics")
def diagnostics():
    """Endpoint de diagnóstico para verificar configuración."""
    from src.config import (
        PAGE_ID, IG_USER_ID, PAGE_ACCESS_TOKEN,
        LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSONAL_ID, LINKEDIN_CLIENT_ID
    )
    
    # Verificar que el IG_USER_ID sea correcto
    ig_user_id_valid = IG_USER_ID.startswith('17') and len(IG_USER_ID) == 17
    
    return {
        "status": "ok",
        "config_check": {
            "facebook_instagram": {
                "PAGE_ID": PAGE_ID,
                "IG_USER_ID": IG_USER_ID,
                "IG_USER_ID_valid": ig_user_id_valid,
                "IG_USER_ID_note": "Debe empezar con '17' y tener 17 dígitos" if not ig_user_id_valid else "Válido",
                "PAGE_ACCESS_TOKEN_length": len(PAGE_ACCESS_TOKEN) if PAGE_ACCESS_TOKEN else 0,
                "PAGE_ACCESS_TOKEN_preview": PAGE_ACCESS_TOKEN[:10] + "..." if PAGE_ACCESS_TOKEN else "Not set"
            },
            "linkedin": {
                "LINKEDIN_CLIENT_ID": LINKEDIN_CLIENT_ID[:10] + "..." if LINKEDIN_CLIENT_ID else "Not set",
                "LINKEDIN_ACCESS_TOKEN_length": len(LINKEDIN_ACCESS_TOKEN) if LINKEDIN_ACCESS_TOKEN else 0,
                "LINKEDIN_ACCESS_TOKEN_preview": LINKEDIN_ACCESS_TOKEN[:10] + "..." if LINKEDIN_ACCESS_TOKEN else "Not set",
                "LINKEDIN_PERSONAL_ID": LINKEDIN_PERSONAL_ID
            },
            "openai": {
                "OPENAI_API_KEY_configured": bool(os.getenv("OPENAI_API_KEY"))
            },
            "whatsapp": {
                "WHATSAPP_TOKEN_configured": bool(os.getenv("WHATSAPP_TOKEN")),
                "WHATSAPP_TOKEN_length": len(os.getenv("WHATSAPP_TOKEN", ""))
            }
        },
        "test_urls": {
            "instagram_create": f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media",
            "facebook_feed": f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed",
            "linkedin_posts": "https://api.linkedin.com/v2/ugcPosts",
            "whatsapp_stories": "https://gate.whapi.cloud/stories/send/media"
        },
        "supported_platforms": ["facebook", "instagram", "linkedin", "whatsapp"],
        "recommendations": [
            "Usa /publish/instagram directamente para probar Instagram",
            "Usa /publish/linkedin/text para probar LinkedIn",
            "El sistema inteligente /smart-publish ahora soporta LinkedIn",
            "Verifica que todos los tokens tengan los permisos necesarios"
        ]
    }
