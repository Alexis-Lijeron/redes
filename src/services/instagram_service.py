import requests
from src.config import IG_USER_ID, PAGE_ACCESS_TOKEN


def instagram_create_media(image_url: str, caption: str):
    """
    Crea un contenedor de media en Instagram para posteriormente publicarlo.
    
    Args:
        image_url (str): URL de la imagen a publicar
        caption (str): Caption/descripción de la imagen
        
    Returns:
        dict: Respuesta de la API de Instagram con el ID del contenedor creado
    """
    url = (
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
        f"?image_url={image_url}"
        f"&caption={caption}"
        f"&access_token={PAGE_ACCESS_TOKEN}"
    )

    response = requests.post(url)
    return response.json()


def instagram_publish_media(creation_id: str):
    """
    Publica un contenedor de media previamente creado en Instagram.
    
    Args:
        creation_id (str): ID del contenedor de media creado anteriormente
        
    Returns:
        dict: Respuesta de la API de Instagram con el resultado de la publicación
    """
    url = (
        f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
        f"?creation_id={creation_id}"
        f"&access_token={PAGE_ACCESS_TOKEN}"
    )

    response = requests.post(url)
    return response.json()
