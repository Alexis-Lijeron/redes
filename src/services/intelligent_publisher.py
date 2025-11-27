"""
Servicio inteligente que procesa comandos en lenguaje natural para generar contenido,
crear imágenes con DALL-E y publicar automáticamente en redes sociales.
"""

import json
import logging
import re
import requests
import tempfile
import os
import base64
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import openai
from openai import OpenAI
from urllib.parse import urlparse

from src.services.llm_adapter import LLMAdapter
from src.services.instagram_service import instagram_create_media, instagram_publish_media
from src.services.facebook_service import facebook_post_text, facebook_post_image
from src.services.linkedin_service import linkedin_post_text, linkedin_post_image

logger = logging.getLogger(__name__)


class IntelligentPublisher:
    """Servicio que procesa comandos en lenguaje natural y ejecuta automáticamente"""
    
    def __init__(self, openai_api_key: str):
        """
        Inicializa el publicador inteligente.
        
        Args:
            openai_api_key (str): Clave API de OpenAI
        """
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.llm_adapter = LLMAdapter(openai_api_key)
        logger.info("IntelligentPublisher inicializado correctamente")
    
    def process_natural_command(self, command: str) -> Dict:
        """
        Procesa un comando en lenguaje natural y ejecuta todas las acciones necesarias.
        
        Args:
            command (str): Comando en lenguaje natural como:
                         "Quiero publicar en Instagram sobre nuestro nuevo producto X con una imagen moderna"
                         "Publica en Facebook e Instagram sobre el evento de mañana"
                         "Crea un post para Instagram sobre tecnología con imagen futurista"
        
        Returns:
            Dict: Resultado completo de la operación
        """
        try:
            logger.info(f"Procesando comando: {command[:100]}...")
            
            # 1. Analizar el comando con GPT para extraer información
            analysis = self._analyze_command(command)
            
            # 2. Generar contenido optimizado para cada plataforma
            content = self._generate_content(analysis)
            
            # 3. Generar imagen si es necesaria
            image_url = None
            if analysis.get("needs_image", False):
                image_url = self._generate_image(analysis.get("image_prompt", ""))
            
            # 4. Publicar en las plataformas especificadas
            publication_results = {}
            for platform in analysis.get("platforms", []):
                try:
                    result = self._publish_to_platform(
                        platform, 
                        content.get(platform, {}), 
                        image_url
                    )
                    publication_results[platform] = result
                except Exception as e:
                    publication_results[platform] = {
                        "error": str(e),
                        "status": "failed"
                    }
            
            return {
                "success": True,
                "message": "Comando procesado exitosamente",
                "analysis": analysis,
                "generated_content": content,
                "generated_image": image_url,
                "publication_results": publication_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en process_natural_command: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def process_natural_command_test_mode(self, command: str) -> Dict:
        """
        Procesa un comando en lenguaje natural SOLO generando contenido e imagen, sin publicar.
        
        Args:
            command (str): Comando en lenguaje natural
            
        Returns:
            Dict: Contenido generado sin intentar publicar
        """
        try:
            logger.info(f"Procesando comando en modo prueba: {command[:100]}...")
            
            # 1. Analizar el comando con GPT para extraer información
            analysis = self._analyze_command(command)
            
            # 2. Generar contenido optimizado para cada plataforma
            content = self._generate_content(analysis)
            
            # 3. Generar imagen si es necesaria
            image_url = None
            if analysis.get("needs_image", False):
                image_url = self._generate_image(analysis.get("image_prompt", ""))
            
            return {
                "success": True,
                "message": "Contenido generado exitosamente (modo prueba - sin publicar)",
                "analysis": analysis,
                "generated_content": content,
                "generated_image": image_url,
                "publication_results": {"note": "Modo prueba - no se publicó automáticamente"},
                "timestamp": datetime.now().isoformat(),
                "instructions": {
                    "next_steps": "Usa los endpoints directos para publicar manualmente:",
                    "instagram": "POST /publish/instagram con image_url y caption",
                    "facebook_text": "POST /publish/facebook/text con message",
                    "facebook_image": "POST /publish/facebook/image con image_url y caption",
                    "linkedin_text": "POST /publish/linkedin/text con message",
                    "linkedin_image": "POST /publish/linkedin/image con image_url y message"
                }
            }
            
        except Exception as e:
            logger.error(f"Error en process_natural_command_test_mode: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    

    
    def _analyze_command(self, command: str) -> Dict:
        """
        Analiza el comando en lenguaje natural para extraer información estructurada.
        """
        system_prompt = """Eres un asistente que analiza comandos para publicación en redes sociales.
        
Tu tarea es analizar el comando del usuario y extraer:
1. Plataformas donde publicar (facebook, instagram, linkedin, o combinaciones)
2. Título/encabezado del contenido
3. Tema/contenido principal
4. Si necesita imagen (true/false)
5. Descripción para generar la imagen

Responde SOLO con un JSON válido con esta estructura:
{
    "platforms": ["facebook", "instagram", "linkedin"],
    "title": "título extraído",
    "content": "contenido principal",
    "needs_image": true,
    "image_prompt": "descripción detallada para generar imagen"
}

Ejemplos de análisis:
- "Publica en Instagram sobre nuestro café" → platforms: ["instagram"], needs_image: true
- "Post en Facebook e Instagram sobre el evento" → platforms: ["facebook", "instagram"]
- "Publica en LinkedIn sobre nuestra empresa" → platforms: ["linkedin"], needs_image: false
- "Quiero publicar en todas las redes sobre tecnología" → platforms: ["facebook", "instagram", "linkedin"]
- "Quiero publicar en redes sobre tecnología" → platforms: ["facebook", "instagram"] (sin LinkedIn por defecto a menos que se especifique)
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": command}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"Análisis completado: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Error analizando comando: {e}")
            # Fallback: análisis básico por palabras clave
            return self._basic_analysis(command)
    
    def _basic_analysis(self, command: str) -> Dict:
        """Análisis básico por palabras clave como fallback."""
        platforms = []
        
        if "instagram" in command.lower() or "insta" in command.lower():
            platforms.append("instagram")
        if "facebook" in command.lower() or "fb" in command.lower():
            platforms.append("facebook")
        if "linkedin" in command.lower():
            platforms.append("linkedin")
        
        # Detectar "todas las redes" o "redes sociales"
        if "todas las redes" in command.lower() or "all platforms" in command.lower():
            platforms = ["facebook", "instagram", "linkedin"]
        elif not platforms:
            platforms = ["facebook", "instagram"]  # Por defecto Facebook e Instagram
        
        return {
            "platforms": platforms,
            "title": "Publicación en redes sociales",
            "content": command,
            "needs_image": "instagram" in platforms or "linkedin" in platforms,
            "image_prompt": "imagen moderna y atractiva para redes sociales"
        }
    
    def _generate_content(self, analysis: Dict) -> Dict:
        """
        Genera contenido optimizado usando el LLMAdapter existente.
        """
        return self.llm_adapter.transform_for_multiple_platforms(
            heading=analysis.get("title", ""),
            material=analysis.get("content", ""),
            target_platforms=analysis.get("platforms", [])
        )
    
    def _generate_image(self, image_prompt: str) -> Optional[str]:
        """
        Genera una imagen usando DALL-E 3, la descarga y la hace públicamente accesible.
        
        Args:
            image_prompt (str): Prompt para generar la imagen
            
        Returns:
            Optional[str]: URL de la imagen accesible públicamente
        """
        logger.info(f"🎨 Generando imagen con DALL-E para: {image_prompt}")
        
        # Mejorar el prompt para DALL-E
        enhanced_prompt = f"""{image_prompt}. 
        Estilo: moderno, profesional, colores vibrantes, alta calidad, 
        formato cuadrado 1:1 ideal para redes sociales, 
        sin texto superpuesto, imagen limpia y atractiva"""
        
        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        dalle_url = response.data[0].url
        logger.info(f"✅ Imagen DALL-E generada exitosamente")
        
        # Descargar y convertir a URL pública accesible
        logger.info("🔄 Procesando imagen para redes sociales...")
        public_url = self._make_image_publicly_accessible(dalle_url)
        
        logger.info(f"🎉 Imagen lista para publicación: {public_url}")
        return public_url
    
    def _generate_and_save_image(self, image_prompt: str) -> Optional[str]:
        """
        Genera una imagen usando DALL-E, la guarda localmente y la sube a Facebook para obtener URL pública.
        
        Args:
            image_prompt (str): Prompt para generar la imagen
            
        Returns:
            Optional[str]: URL pública accesible de la imagen
        """
        logger.info(f"🎨 Generando imagen con DALL-E para: {image_prompt}")
        
        # Mejorar el prompt para DALL-E
        enhanced_prompt = f"""{image_prompt}. 
        Estilo: moderno, profesional, colores vibrantes, alta calidad, 
        formato cuadrado 1:1 ideal para redes sociales, 
        sin texto superpuesto, imagen limpia y atractiva"""
        
        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        
        dalle_url = response.data[0].url
        logger.info(f"✅ Imagen DALL-E generada exitosamente")
        
        # Descargar y guardar localmente
        logger.info("📥 Descargando imagen...")
        local_path = self._download_and_save_dalle_image(dalle_url)
        
        # Devolver la ruta local - facebook_service se encargará de subirla
        # cuando se publique
        logger.info(f"✅ Imagen guardada localmente: {local_path}")
        return local_path
    
    def _generate_and_save_video(self, video_prompt: str, duration: int = 4) -> Optional[str]:
        """
        Genera un video usando Sora 2 de OpenAI, lo guarda localmente.
        Formato: Portrait 720x1280 para TikTok.
        
        Args:
            video_prompt (str): Prompt para generar el video
            duration (int): Duración del video en segundos (máximo 4)
            
        Returns:
            Optional[str]: Ruta local del video generado
        """
        import time
        import uuid
        
        # Limitar duración a máximo 4 segundos
        duration = min(duration, 4)
        
        logger.info(f"🎬 Generando video con Sora 2 para: {video_prompt}")
        
        try:
            # Crear el trabajo de generación de video con Sora 2
            logger.info("⏳ Iniciando generación de video...")
            
            video = self.openai_client.videos.create(
                model="sora-2",
                prompt=video_prompt,
                seconds=str(duration),  # Duración como string
            )
            
            logger.info(f"📤 Trabajo de video creado, ID: {video.id}")
            
            # Polling del progreso
            progress = getattr(video, 'progress', 0) or 0
            
            while video.status in ['in_progress', 'queued']:
                # Verificar estado del video cada 3 segundos
                video = self.openai_client.videos.retrieve(video.id)
                progress = getattr(video, 'progress', 0) or 0
                
                status_msg = 'En cola' if video.status == 'queued' else 'Procesando'
                logger.info(f"⏳ {status_msg}: {progress:.1f}%")
                
                time.sleep(3)  # Esperar 3 segundos
            
            # Si falló
            if video.status == 'failed':
                error_msg = video.error.message if hasattr(video, 'error') and video.error else 'Error desconocido'
                logger.error(f"❌ Falló la generación del video: {error_msg}")
                raise Exception(f"Error generando video: {error_msg}")
            
            # Video completado, descargar
            logger.info("✅ Video completado, descargando...")
            
            content = self.openai_client.videos.download_content(video.id)
            
            # Convertir a bytes
            video_bytes = content.read() if hasattr(content, 'read') else bytes(content)
            
            # Crear directorio para videos si no existe
            temp_dir = Path("temp_images")
            temp_dir.mkdir(exist_ok=True)
            
            # Generar nombre único para el archivo
            filename = f"sora_video_{uuid.uuid4().hex[:8]}.mp4"
            filepath = temp_dir / filename
            
            # Guardar el archivo
            with open(filepath, 'wb') as f:
                f.write(video_bytes)
            
            logger.info(f"✅ Video guardado: {filepath}")
            
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Error generando video con Sora 2: {e}")
            raise
    
    def _download_and_save_dalle_image(self, dalle_url: str) -> str:
        """
        Descarga la imagen de DALL-E y la guarda localmente.
        
        Args:
            dalle_url (str): URL temporal de DALL-E
            
        Returns:
            str: Ruta local del archivo descargado
        """
        logger.info(f"📥 Descargando imagen DALL-E...")
        
        # Descargar la imagen de DALL-E
        response = requests.get(dalle_url, timeout=30)
        response.raise_for_status()
        
        # Crear directorio temporal si no existe
        temp_dir = Path("temp_images")
        temp_dir.mkdir(exist_ok=True)
        
        # Generar nombre único para el archivo
        import uuid
        filename = f"dalle_image_{uuid.uuid4().hex[:8]}.png"
        filepath = temp_dir / filename
        
        # Guardar la imagen localmente
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"✅ Imagen descargada: {filepath}")
        # Retornar path relativo para que funcione tanto en Docker como local
        return str(filepath)
    
    def _upload_image_to_facebook_api(self, image_path: str) -> str:
        """
        Sube una imagen local a Facebook API y retorna la URL pública.
        
        Args:
            image_path (str): Ruta local de la imagen
            
        Returns:
            str: URL pública de la imagen subida
        """
        from src.config import PAGE_ID, PAGE_ACCESS_TOKEN
        
        logger.info(f"📤 Subiendo imagen a Facebook API...")
        
        try:
            # Leer la imagen como bytes
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            # Subir imagen a Facebook
            upload_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
            
            files = {
                'file': ('image.png', image_data, 'image/png')
            }
            
            data = {
                'access_token': PAGE_ACCESS_TOKEN,
                'published': 'false'  # No publicar, solo subir
            }
            
            response = requests.post(upload_url, files=files, data=data)
            result = response.json()
            
            if 'id' in result:
                photo_id = result['id']
                
                # Obtener información completa de la foto para conseguir la URL real
                photo_info_url = f"https://graph.facebook.com/v19.0/{photo_id}?fields=images&access_token={PAGE_ACCESS_TOKEN}"
                photo_info_response = requests.get(photo_info_url)
                photo_info = photo_info_response.json()
                
                # Obtener la URL de la imagen de mayor resolución
                if 'images' in photo_info and len(photo_info['images']) > 0:
                    # Las imágenes vienen ordenadas por tamaño, la primera es la más grande
                    photo_url = photo_info['images'][0]['source']
                    logger.info(f"✅ Imagen subida exitosamente a Facebook: {photo_url}")
                    return photo_url
                else:
                    # Fallback a la URL básica
                    photo_url = f"https://graph.facebook.com/v19.0/{photo_id}/picture?type=large"
                    logger.info(f"✅ Imagen subida exitosamente a Facebook (usando URL básica)")
                    return photo_url
            else:
                raise Exception(f"Error en API de Facebook: {result}")
                
        finally:
            # Limpiar archivo temporal
            try:
                if os.path.exists(image_path):
                    os.remove(image_path)
                    logger.info(f"🗑️ Archivo temporal eliminado")
            except Exception as e:
                logger.warning(f"No se pudo eliminar archivo temporal: {e}")
    
    def _make_image_publicly_accessible(self, dalle_url: str) -> str:
        """
        Convierte una imagen de DALL-E en una URL pública descargándola y subiéndola.
        
        Args:
            dalle_url (str): URL temporal de DALL-E
            
        Returns:
            str: URL pública accesible
        """
        # 1. Descargar imagen de DALL-E localmente
        local_path = self._download_and_save_dalle_image(dalle_url)
        
        # 2. Subir imagen a Facebook API para obtener URL pública
        public_url = self._upload_image_to_facebook_api(local_path)
        
        logger.info(f"✅ Imagen DALL-E convertida a URL pública: {public_url}")
        return public_url
    
    def _publish_to_platform(self, platform: str, content: Dict, image_url: Optional[str]) -> Dict:
        """
        Publica en una plataforma específica usando llamadas HTTP directas.
        """
        try:
            text = content.get("text", "")
            logger.info(f"Intentando publicar en {platform} con imagen: {image_url}")
            
            if platform == "facebook":
                if image_url:
                    logger.info(f"Publicando imagen en Facebook: {image_url}")
                    result = facebook_post_image(image_url, text)
                else:
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
                    raise ValueError("Instagram requiere una imagen")
                
                result = self._direct_instagram_publish(image_url, text)
                
                return {
                    "status": "published",
                    "platform": "instagram", 
                    "type": "image",
                    "response": result
                }
            
            elif platform == "linkedin":
                if image_url:
                    logger.info(f"Publicando imagen en LinkedIn: {image_url}")
                    result = linkedin_post_image(text, image_url)
                else:
                    logger.info("Publicando texto en LinkedIn")
                    result = linkedin_post_text(text)
                
                return {
                    "status": "published",
                    "platform": "linkedin",
                    "type": "image" if image_url else "text",
                    "response": result
                }
            
            else:
                raise ValueError(f"Plataforma no soportada: {platform}")
                
        except Exception as e:
            logger.error(f"Error publicando en {platform}: {e}")
            raise
    
    def _direct_instagram_publish(self, image_url: str, caption: str) -> Dict:
        """
        Publica directamente en Instagram usando llamadas HTTP para evitar problemas de contexto.
        """
        try:
            from src.config import IG_USER_ID, PAGE_ACCESS_TOKEN
            
            logger.info(f"Publicación directa Instagram - ID: {IG_USER_ID}, Token: {PAGE_ACCESS_TOKEN[:20]}...")
            
            # 1. Crear contenedor de media
            create_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
            create_params = {
                "image_url": image_url,
                "caption": caption,
                "access_token": PAGE_ACCESS_TOKEN
            }
            
            logger.info(f"Creando media con params: {create_params}")
            create_response = requests.post(create_url, params=create_params)
            create_result = create_response.json()
            
            logger.info(f"Resultado creación: {create_result}")
            
            if "id" not in create_result:
                raise Exception(f"Error creando media: {create_result}")
            
            creation_id = create_result["id"]
            
            # 2. Publicar contenedor
            publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
            publish_params = {
                "creation_id": creation_id,
                "access_token": PAGE_ACCESS_TOKEN
            }
            
            logger.info(f"Publicando media con ID: {creation_id}")
            publish_response = requests.post(publish_url, params=publish_params)
            publish_result = publish_response.json()
            
            logger.info(f"Resultado publicación: {publish_result}")
            
            return {
                "creation_id": creation_id,
                "creation_response": create_result,
                "publish_response": publish_result
            }
            
        except Exception as e:
            logger.error(f"Error en publicación directa Instagram: {e}")
            raise Exception(f"Error en publicación directa Instagram: {str(e)}")


def create_intelligent_publisher(openai_api_key: str) -> IntelligentPublisher:
    """Factory function para crear un IntelligentPublisher"""
    return IntelligentPublisher(openai_api_key)