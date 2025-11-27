"""
Servicio para adaptación de contenido usando LLM
"""
from typing import Dict, List
from src.services.llm_adapter import LLMAdapter


class AdaptationService:
    """Servicio para adaptar contenido a diferentes redes sociales usando LLM"""

    def __init__(self, openai_api_key: str):
        """
        Inicializar servicio de adaptación
        
        Args:
            openai_api_key: API key de OpenAI
        """
        self.llm_adapter = LLMAdapter(openai_api_key)

    def adapt_content(
        self,
        title: str,
        content: str,
        networks: List[str]
    ) -> Dict[str, str]:
        """
        Adaptar contenido para múltiples redes sociales
        
        Args:
            title: Título del contenido
            content: Contenido original
            networks: Lista de redes sociales ["facebook", "instagram", etc.]
            
        Returns:
            Diccionario con contenido adaptado por red
            {
                "facebook": "contenido adaptado...",
                "instagram": "contenido adaptado...",
                ...
            }
        """
        adapted_content = {}
        
        for network in networks:
            try:
                # Usar el método transform_for_platform del LLMAdapter
                result = self.llm_adapter.transform_for_platform(
                    heading=title,
                    material=content,
                    platform=network
                )
                
                # Extraer el texto adaptado del resultado
                adapted_content[network] = result.get("text", f"{title}\n\n{content}")
                
            except Exception as e:
                print(f"Error adaptando para {network}: {e}")
                # En caso de error, usar el contenido original
                adapted_content[network] = f"{title}\n\n{content}"
        
        return adapted_content

    def preview_adaptations(
        self,
        title: str,
        content: str,
        networks: List[str]
    ) -> Dict[str, Dict]:
        """
        Generar vista previa de adaptaciones con metadata
        
        Args:
            title: Título del contenido
            content: Contenido original
            networks: Lista de redes sociales
            
        Returns:
            Diccionario con vista previa por red incluyendo metadata
        """
        previews = {}
        
        for network in networks:
            try:
                # Usar transform_for_platform que retorna JSON completo
                result = self.llm_adapter.transform_for_platform(
                    heading=title,
                    material=content,
                    platform=network
                )
                
                previews[network] = {
                    "adapted_text": result.get("text", ""),
                    "hashtags": result.get("hashtags", []),
                    "image_suggestion": result.get("suggested_image_prompt", result.get("suggested_video_prompt", "")),
                    "character_count": result.get("character_count", 0),
                    "tone": result.get("tone", "")
                }
                
            except Exception as e:
                previews[network] = {
                    "error": str(e),
                    "adapted_text": f"{title}\n\n{content}"
                }
        
        return previews
