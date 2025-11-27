import requests
import os
import logging
from pathlib import Path
from src.config import PAGE_ID, PAGE_ACCESS_TOKEN

logger = logging.getLogger(__name__)


def facebook_post_text(message: str):
    """
    Publica un mensaje de texto en Facebook.
    
    Args:
        message (str): Mensaje de texto a publicar
        
    Returns:
        dict: Respuesta de la API de Facebook con el resultado de la publicación
    """
    url = (
        f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
        f"?message={message}"
        f"&access_token={PAGE_ACCESS_TOKEN}"
    )

    response = requests.post(url)
    return response.json()


def facebook_post_image(image_url: str, caption: str):
    """
    Publica una imagen con caption en Facebook.
    Soporta tanto URLs públicas como archivos locales.
    
    Args:
        image_url (str): URL de la imagen a publicar o ruta local
        caption (str): Caption/descripción de la imagen
        
    Returns:
        dict: Respuesta de la API de Facebook con el resultado de la publicación
    """
    logger.info(f"🖼️ facebook_post_image - image_url recibida: {image_url}")
    
    # Verificar si es una URL de localhost o una ruta local
    is_local = (
        image_url.startswith('http://localhost') or 
        image_url.startswith('/temp_images') or
        image_url.startswith('temp_images') or
        os.path.exists(image_url)
    )
    
    logger.info(f"🖼️ is_local: {is_local}, os.path.exists: {os.path.exists(image_url)}")
    
    if is_local:
        # Convertir URL localhost a path local
        if 'localhost' in image_url:
            # Extraer el path del archivo desde la URL
            # http://localhost:8000/temp_images/xxx.png -> temp_images/xxx.png
            local_path = image_url.split('/temp_images/')[-1]
            local_path = f"temp_images/{local_path}"
        elif image_url.startswith('/'):
            local_path = image_url[1:]  # Quitar el / inicial
        else:
            local_path = image_url
        
        logger.info(f"🖼️ local_path: {local_path}, exists: {os.path.exists(local_path)}")
        
        # Verificar que el archivo existe
        if os.path.exists(local_path):
            logger.info(f"🖼️ Subiendo imagen local a Facebook...")
            return _upload_local_image_to_facebook(local_path, caption)
        else:
            logger.error(f"🖼️ ERROR: Archivo no encontrado: {local_path}")
            return {"error": f"Archivo local no encontrado: {local_path}"}
    
    logger.info(f"🖼️ Usando URL pública: {image_url}")
    # Para URLs públicas, usar el método tradicional
    url = (
        f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
        f"?url={image_url}"
        f"&caption={caption}"
        f"&access_token={PAGE_ACCESS_TOKEN}"
    )

    response = requests.post(url)
    return response.json()


def _upload_local_image_to_facebook(image_path: str, caption: str):
    """
    Sube una imagen local directamente a Facebook.
    
    Args:
        image_path (str): Ruta local de la imagen
        caption (str): Caption/descripción de la imagen
        
    Returns:
        dict: Respuesta de la API de Facebook
    """
    upload_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    
    # Determinar el tipo MIME
    if image_path.lower().endswith('.png'):
        mime_type = 'image/png'
    elif image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        mime_type = 'image/jpeg'
    else:
        mime_type = 'image/png'  # Default
    
    with open(image_path, 'rb') as f:
        files = {
            'source': (os.path.basename(image_path), f, mime_type)
        }
        data = {
            'caption': caption,
            'access_token': PAGE_ACCESS_TOKEN,
            'published': 'true'  # Publicar directamente
        }
        
        response = requests.post(upload_url, files=files, data=data)
        return response.json()
