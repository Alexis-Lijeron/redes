import requests
import json
import os
import tempfile
from urllib.parse import quote
from typing import Optional, Dict, Any
from src.config import LINKEDIN_ACCESS_TOKEN, LINKEDIN_PERSONAL_ID, LINKEDIN_ORG_ID


class LinkedInService:
    def __init__(self):
        self.access_token = LINKEDIN_ACCESS_TOKEN
        self.personal_id = LINKEDIN_PERSONAL_ID
        self.org_id = LINKEDIN_ORG_ID
        self.base_url = "https://api.linkedin.com/v2"
        
    def get_headers(self) -> Dict[str, str]:
        """Obtiene los headers para las peticiones a LinkedIn API"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
    
    def upload_image(self, image_url: str, person_id: str) -> Optional[str]:
        """
        Sube una imagen a LinkedIn y retorna el asset ID
        """
        try:
            print(f"[LINKEDIN] Iniciando subida de imagen: {image_url}")
            
            # Paso 1: Registrar el upload
            register_url = f"{self.base_url}/assets?action=registerUpload"
            register_data = {
                "registerUploadRequest": {
                    "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                    "owner": f"urn:li:person:{person_id}",
                    "serviceRelationships": [
                        {
                            "relationshipType": "OWNER",
                            "identifier": "urn:li:userGeneratedContent"
                        }
                    ]
                }
            }
            
            response = requests.post(
                register_url,
                headers=self.get_headers(),
                json=register_data
            )
            
            if response.status_code != 200:
                print(f"[LINKEDIN] Error registrando upload: {response.status_code}")
                print(f"[LINKEDIN] Response: {response.text}")
                return None
                
            register_response = response.json()
            print(f"[LINKEDIN] Upload registrado exitosamente")
            
            # Obtener URL de upload y asset ID
            upload_mechanism = register_response["value"]["uploadMechanism"]
            upload_url = upload_mechanism["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
            asset = register_response["value"]["asset"]
            
            # Paso 2: Descargar la imagen
            print(f"[LINKEDIN] Descargando imagen desde: {image_url}")
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                print(f"[LINKEDIN] Error descargando imagen: {image_response.status_code}")
                return None
                
            # Paso 3: Subir la imagen binaria
            print(f"[LINKEDIN] Subiendo imagen a LinkedIn...")
            upload_headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/octet-stream"
            }
            
            upload_response = requests.post(
                upload_url,
                headers=upload_headers,
                data=image_response.content
            )
            
            if upload_response.status_code not in [200, 201]:
                print(f"[LINKEDIN] Error subiendo imagen: {upload_response.status_code}")
                print(f"[LINKEDIN] Response: {upload_response.text}")
                return None
                
            print(f"[LINKEDIN] Imagen subida exitosamente")
            return asset
            
        except Exception as e:
            print(f"[LINKEDIN] Error en upload_image: {str(e)}")
            return None
    
    def post_text(self, text: str, person_id: str) -> Dict[str, Any]:
        """
        Publica solo texto en LinkedIn
        """
        try:
            print(f"[LINKEDIN] Publicando texto en LinkedIn...")
            
            url = f"{self.base_url}/ugcPosts"
            data = {
                "author": f"urn:li:person:{person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = requests.post(
                url,
                headers=self.get_headers(),
                json=data
            )
            
            print(f"[LINKEDIN] Status Code: {response.status_code}")
            print(f"[LINKEDIN] Response: {response.text}")
            
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"[LINKEDIN] Error en post_text: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def post_with_image(self, text: str, image_url: str, person_id: str) -> Dict[str, Any]:
        """
        Publica texto con imagen en LinkedIn
        """
        try:
            print(f"[LINKEDIN] Publicando texto con imagen en LinkedIn...")
            
            # Primero subir la imagen
            asset_id = self.upload_image(image_url, person_id)
            if not asset_id:
                return {"success": False, "error": "No se pudo subir la imagen"}
            
            # Crear el post con la imagen
            url = f"{self.base_url}/ugcPosts"
            data = {
                "author": f"urn:li:person:{person_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": text
                        },
                        "shareMediaCategory": "IMAGE",
                        "media": [
                            {
                                "status": "READY",
                                "description": {
                                    "text": "Imagen generada con IA"
                                },
                                "media": asset_id,
                                "title": {
                                    "text": "Publicación con imagen"
                                }
                            }
                        ]
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            response = requests.post(
                url,
                headers=self.get_headers(),
                json=data
            )
            
            print(f"[LINKEDIN] Status Code: {response.status_code}")
            print(f"[LINKEDIN] Response: {response.text}")
            
            if response.status_code == 201:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": response.text}
                
        except Exception as e:
            print(f"[LINKEDIN] Error en post_with_image: {str(e)}")
            return {"success": False, "error": str(e)}


# Instancia global del servicio
linkedin_service = LinkedInService()

# Funciones de conveniencia
def linkedin_post_text(text: str, person_id: str = None) -> Dict[str, Any]:
    """Función de conveniencia para publicar texto"""
    if not person_id:
        person_id = LINKEDIN_PERSONAL_ID
    return linkedin_service.post_text(text, person_id)

def linkedin_post_image(text: str, image_url: str, person_id: str = None) -> Dict[str, Any]:
    """Función de conveniencia para publicar texto con imagen"""
    if not person_id:
        person_id = LINKEDIN_PERSONAL_ID
    return linkedin_service.post_with_image(text, image_url, person_id)