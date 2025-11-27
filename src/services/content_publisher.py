"""
Servicio integrado que combina generación de contenido con LLM y publicación en redes sociales
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

from src.services.llm_adapter import LLMAdapter, validate_input_data
from src.services.instagram_service import instagram_create_media, instagram_publish_media
from src.services.facebook_service import facebook_post_text, facebook_post_image
from src.config import PAGE_ACCESS_TOKEN

logger = logging.getLogger(__name__)


class ContentPublisher:
    """Servicio que genera contenido con LLM y publica en redes sociales"""
    
    def __init__(self, openai_api_key: str):
        """
        Inicializa el publicador de contenido.
        
        Args:
            openai_api_key (str): Clave API de OpenAI
        """
        self.llm_adapter = LLMAdapter(openai_api_key)
        self.supported_platforms = ["facebook", "instagram"]
        logger.info("ContentPublisher inicializado correctamente")
    
    def generate_and_publish(
        self, 
        heading: str, 
        material: str, 
        platforms: List[str],
        auto_publish: bool = False,
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Genera contenido optimizado para cada plataforma y opcionalmente lo publica.
        
        Args:
            heading (str): Encabezado del contenido
            material (str): Material original
            platforms (List[str]): Plataformas objetivo ["facebook", "instagram"]
            auto_publish (bool): Si debe publicar automáticamente
            image_url (Optional[str]): URL de imagen para usar en las publicaciones
            
        Returns:
            Dict: Contenido generado y resultados de publicación
        """
        try:
            logger.info(f"Generando contenido para: {', '.join(platforms)}")
            
            # Filtrar solo plataformas soportadas para publicación
            supported_platforms = [p for p in platforms if p in self.supported_platforms]
            
            if not supported_platforms:
                raise ValueError(f"Ninguna plataforma soportada para publicación. Soportadas: {self.supported_platforms}")
            
            # Generar contenido con el LLM
            generated_content = self.llm_adapter.transform_for_multiple_platforms(
                heading=heading,
                material=material,
                target_platforms=supported_platforms
            )
            
            results = {
                "generated_content": generated_content,
                "publication_results": {},
                "timestamp": datetime.now().isoformat(),
                "auto_published": auto_publish
            }
            
            # Si auto_publish está activado, publicar en cada plataforma
            if auto_publish:
                logger.info("Iniciando publicación automática...")
                
                for platform in supported_platforms:
                    if platform in generated_content:
                        try:
                            platform_content = generated_content[platform]
                            publication_result = self._publish_to_platform(
                                platform, 
                                platform_content, 
                                image_url
                            )
                            results["publication_results"][platform] = publication_result
                        except Exception as e:
                            logger.error(f"Error publicando en {platform}: {e}")
                            results["publication_results"][platform] = {
                                "error": str(e),
                                "status": "failed"
                            }
            
            return results
            
        except Exception as e:
            logger.error(f"Error en generate_and_publish: {e}")
            raise Exception(f"Error generando/publicando contenido: {str(e)}")
    
    def _publish_to_platform(
        self, 
        platform: str, 
        content: Dict, 
        image_url: Optional[str] = None
    ) -> Dict:
        """
        Publica contenido en una plataforma específica.
        
        Args:
            platform (str): Plataforma objetivo
            content (Dict): Contenido generado por el LLM
            image_url (Optional[str]): URL de imagen
            
        Returns:
            Dict: Resultado de la publicación
        """
        try:
            text = content.get("text", "")
            logger.info(f"Publicando en {platform} con texto: {text[:50]}...")
            
            if platform == "facebook":
                if image_url:
                    # Publicar imagen con caption en Facebook
                    logger.info(f"Publicando imagen en Facebook: {image_url}")
                    result = facebook_post_image(image_url, text)
                else:
                    # Publicar solo texto en Facebook
                    logger.info("Publicando texto en Facebook")
                    result = facebook_post_text(text)
                
                return {
                    "status": "published",
                    "platform": "facebook",
                    "type": "image" if image_url else "text",
                    "response": result
                }
            
            elif platform == "instagram":
                if not image_url:
                    raise ValueError("Instagram requiere una imagen para publicar")
                
                logger.info(f"Publicando en Instagram - imagen: {image_url}, texto: {text[:50]}...")
                
                # Crear contenedor de media en Instagram
                creation_result = instagram_create_media(image_url, text)
                logger.info(f"Resultado creación Instagram: {creation_result}")
                
                if "id" not in creation_result:
                    logger.error(f"Error en creación Instagram: {creation_result}")
                    raise Exception(f"Error creando media en Instagram: {creation_result}")
                
                creation_id = creation_result["id"]
                logger.info(f"Media creado en Instagram con ID: {creation_id}")
                
                # Publicar el contenedor
                publish_result = instagram_publish_media(creation_id)
                logger.info(f"Resultado publicación Instagram: {publish_result}")
                
                return {
                    "status": "published",
                    "platform": "instagram",
                    "type": "image",
                    "creation_id": creation_id,
                    "creation_response": creation_result,
                    "publish_response": publish_result
                }
            
            else:
                raise ValueError(f"Plataforma no soportada para publicación: {platform}")
                
        except Exception as e:
            logger.error(f"Error publicando en {platform}: {e}")
            raise Exception(f"Error en publicación {platform}: {str(e)}")
    
    def generate_image_suggestions(self, content: Dict) -> Dict:
        """
        Extrae y mejora las sugerencias de imagen generadas por el LLM.
        
        Args:
            content (Dict): Contenido generado que puede incluir image prompts
            
        Returns:
            Dict: Sugerencias de imagen organizadas por plataforma
        """
        image_suggestions = {}
        
        for platform, platform_content in content.items():
            if isinstance(platform_content, dict):
                # Instagram tiene suggested_image_prompt
                if "suggested_image_prompt" in platform_content:
                    image_suggestions[platform] = {
                        "type": "image",
                        "prompt": platform_content["suggested_image_prompt"],
                        "recommended_size": "1080x1080" if platform == "instagram" else "1200x630"
                    }
                
                # TikTok tiene suggested_video_prompt (para futura implementación)
                elif "suggested_video_prompt" in platform_content:
                    image_suggestions[platform] = {
                        "type": "video",
                        "prompt": platform_content["suggested_video_prompt"],
                        "recommended_size": "1080x1920"
                    }
        
        return image_suggestions
    
    def preview_content(self, heading: str, material: str, platforms: List[str]) -> Dict:
        """
        Genera vista previa del contenido sin publicar.
        
        Args:
            heading (str): Encabezado del contenido
            material (str): Material original
            platforms (List[str]): Plataformas objetivo
            
        Returns:
            Dict: Vista previa del contenido generado
        """
        try:
            # Filtrar plataformas soportadas
            supported_platforms = [p for p in platforms if p in self.supported_platforms]
            
            # Generar contenido
            generated_content = self.llm_adapter.transform_for_multiple_platforms(
                heading=heading,
                material=material,
                target_platforms=supported_platforms
            )
            
            # Generar sugerencias de imagen
            image_suggestions = self.generate_image_suggestions(generated_content)
            
            return {
                "preview": True,
                "generated_content": generated_content,
                "image_suggestions": image_suggestions,
                "supported_platforms": supported_platforms,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en preview_content: {e}")
            raise Exception(f"Error generando vista previa: {str(e)}")


def create_content_publisher(openai_api_key: str) -> ContentPublisher:
    """Factory function para crear un ContentPublisher"""
    return ContentPublisher(openai_api_key)