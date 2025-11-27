import os
import json
import httpx
from pathlib import Path
from typing import List, Optional
from src.config import WHATSAPP_TOKEN


WHAPI_BASE_URL = "https://gate.whapi.cloud/stories/send/media"


async def whatsapp_post_story(
    media_path: str,
    caption: str,
    exclude_contacts: Optional[List[str]] = None
):
    """
    Publica un estado (story) en WhatsApp con imagen o video y texto.
    
    Args:
        media_path (str): Ruta del archivo de imagen o video a publicar.
                         Puede ser una ruta absoluta o relativa.
        caption (str): Texto/caption del estado
        exclude_contacts (Optional[List[str]]): Lista de contactos a excluir del estado
        
    Returns:
        dict: Respuesta de la API de WhatsApp con el resultado de la publicación
        
    Raises:
        FileNotFoundError: Si el archivo no existe
        httpx.HTTPStatusError: Si la API retorna un error
        Exception: Para cualquier otro error
    """
    if exclude_contacts is None:
        exclude_contacts = []
    
    # 1. Preparar ruta del archivo
    file_path = Path(media_path)
    
    # Si es una ruta relativa, buscar en temp_images
    if not file_path.is_absolute():
        base_path = Path(__file__).parent.parent.parent
        file_path = base_path / "temp_images" / media_path
    
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    # 2. Detectar tipo de archivo
    file_extension = file_path.suffix.lower()
    if file_extension in ['.jpg', '.jpeg', '.png', '.gif']:
        mime_type = f"image/{file_extension[1:]}" if file_extension != '.jpg' else "image/jpeg"
    elif file_extension in ['.mp4', '.avi', '.mov', '.mkv']:
        mime_type = f"video/{file_extension[1:]}"
    else:
        mime_type = "application/octet-stream"
    
    # 3. Preparar payload
    payload = {
        "caption": caption,
        "exclude_contacts": json.dumps(exclude_contacts),
    }
    
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Accept": "application/json",
    }
    
    # 4. Enviar petición
    async with httpx.AsyncClient() as client:
        try:
            with open(file_path, "rb") as f:
                files = {"media": (file_path.name, f, mime_type)}
                
                response = await client.post(
                    WHAPI_BASE_URL,
                    headers=headers,
                    data=payload,
                    files=files,
                    timeout=60.0,
                )
                
                # Si falla, retornar información del error
                if response.status_code != 200:
                    error_detail = response.text
                    return {
                        "status": "error",
                        "status_code": response.status_code,
                        "detail": error_detail
                    }
                
                response.raise_for_status()
                return {
                    "status": "success",
                    "data": response.json()
                }
                
        except httpx.HTTPStatusError as e:
            return {
                "status": "error",
                "status_code": e.response.status_code,
                "detail": e.response.text
            }
        except Exception as e:
            return {
                "status": "error",
                "detail": str(e)
            }


async def whatsapp_post_story_from_url(
    media_url: str,
    caption: str,
    exclude_contacts: Optional[List[str]] = None
):
    """
    Publica un estado en WhatsApp descargando primero la imagen/video de una URL.
    
    Args:
        media_url (str): URL de la imagen o video a publicar
        caption (str): Texto/caption del estado
        exclude_contacts (Optional[List[str]]): Lista de contactos a excluir
        
    Returns:
        dict: Respuesta de la API de WhatsApp
    """
    if exclude_contacts is None:
        exclude_contacts = []
    
    # Descargar el archivo temporalmente
    base_path = Path(__file__).parent.parent.parent
    temp_dir = base_path / "temp_images"
    temp_dir.mkdir(exist_ok=True)
    
    # Extraer nombre del archivo de la URL
    file_name = media_url.split("/")[-1].split("?")[0]
    if not any(file_name.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov']):
        file_name = f"temp_media_{hash(media_url)}.jpg"
    
    temp_file = temp_dir / file_name
    
    # Descargar archivo
    async with httpx.AsyncClient() as client:
        response = await client.get(media_url, timeout=30.0)
        response.raise_for_status()
        
        with open(temp_file, "wb") as f:
            f.write(response.content)
    
    # Publicar usando la función principal
    result = await whatsapp_post_story(
        media_path=str(temp_file),
        caption=caption,
        exclude_contacts=exclude_contacts
    )
    
    # Limpiar archivo temporal
    try:
        temp_file.unlink()
    except Exception:
        pass
    
    return result
