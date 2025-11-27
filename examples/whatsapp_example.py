"""
Ejemplo de uso del servicio de WhatsApp para publicar estados (stories)
"""
import asyncio
from src.services.whatsapp_service import whatsapp_post_story, whatsapp_post_story_from_url


async def ejemplo_publicar_estado_con_imagen_local():
    """Ejemplo: Publicar un estado con una imagen local"""
    result = await whatsapp_post_story(
        media_path="temp_images/mi_imagen.jpg",  # Ruta relativa o absoluta
        caption="¡Hola! Este es mi estado de WhatsApp 📱✨",
        exclude_contacts=[]  # Opcional: lista de contactos a excluir
    )
    print("Resultado:", result)


async def ejemplo_publicar_estado_con_video():
    """Ejemplo: Publicar un estado con un video"""
    result = await whatsapp_post_story(
        media_path="temp_images/mi_video.mp4",
        caption="Mira este increíble video 🎥",
        exclude_contacts=[]
    )
    print("Resultado:", result)


async def ejemplo_publicar_estado_desde_url():
    """Ejemplo: Publicar un estado descargando la imagen de una URL"""
    result = await whatsapp_post_story_from_url(
        media_url="https://ejemplo.com/imagen.jpg",
        caption="Estado publicado desde URL 🌐",
        exclude_contacts=[]
    )
    print("Resultado:", result)


async def ejemplo_excluir_contactos():
    """Ejemplo: Publicar un estado excluyendo algunos contactos"""
    result = await whatsapp_post_story(
        media_path="temp_images/imagen_privada.jpg",
        caption="Solo para algunos contactos 🔒",
        exclude_contacts=["1234567890", "0987654321"]  # Números a excluir
    )
    print("Resultado:", result)


if __name__ == "__main__":
    # Ejecutar uno de los ejemplos
    asyncio.run(ejemplo_publicar_estado_con_imagen_local())
    
    # Para ejecutar otro ejemplo, descomenta:
    # asyncio.run(ejemplo_publicar_estado_con_video())
    # asyncio.run(ejemplo_publicar_estado_desde_url())
    # asyncio.run(ejemplo_excluir_contactos())
