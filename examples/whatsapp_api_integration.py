"""
Ejemplo de integración del servicio de WhatsApp en la API FastAPI
Agrega estos endpoints a tu archivo src/api/main.py
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from src.services.whatsapp_service import whatsapp_post_story, whatsapp_post_story_from_url

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])


class WhatsAppStoryRequest(BaseModel):
    """Modelo para publicar un estado de WhatsApp con archivo local"""
    media_path: str
    caption: str
    exclude_contacts: Optional[List[str]] = []


class WhatsAppStoryFromUrlRequest(BaseModel):
    """Modelo para publicar un estado de WhatsApp desde URL"""
    media_url: str
    caption: str
    exclude_contacts: Optional[List[str]] = []


@router.post("/story")
async def publish_whatsapp_story(request: WhatsAppStoryRequest):
    """
    Publica un estado (story) en WhatsApp con imagen o video local.
    
    Body:
        - media_path: Ruta del archivo (ej: "temp_images/imagen.jpg")
        - caption: Texto del estado
        - exclude_contacts: Lista opcional de números a excluir
    
    Returns:
        Resultado de la publicación
    """
    try:
        result = await whatsapp_post_story(
            media_path=request.media_path,
            caption=request.caption,
            exclude_contacts=request.exclude_contacts
        )
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=result.get("status_code", 500),
                detail=result.get("detail", "Error al publicar estado")
            )
        
        return result
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/story/from-url")
async def publish_whatsapp_story_from_url(request: WhatsAppStoryFromUrlRequest):
    """
    Publica un estado en WhatsApp descargando la imagen/video de una URL.
    
    Body:
        - media_url: URL de la imagen o video
        - caption: Texto del estado
        - exclude_contacts: Lista opcional de números a excluir
    
    Returns:
        Resultado de la publicación
    """
    try:
        result = await whatsapp_post_story_from_url(
            media_url=request.media_url,
            caption=request.caption,
            exclude_contacts=request.exclude_contacts
        )
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=result.get("status_code", 500),
                detail=result.get("detail", "Error al publicar estado")
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Para agregar este router a tu aplicación FastAPI principal:
# 
# En src/api/main.py:
# from src.api.whatsapp_routes import router as whatsapp_router
# app.include_router(whatsapp_router)
