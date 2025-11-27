"""
Test de flujo completo - Publicación en las 5 redes sociales
Facebook, Instagram, LinkedIn, WhatsApp y TikTok

Este test:
1. Registra/Login un usuario
2. Crea un post
3. Adapta el contenido para las 5 redes
4. Publica en todas las redes (Facebook, Instagram, LinkedIn, WhatsApp con imagen, TikTok con video)
5. Verifica el estado de las publicaciones
"""
import os
import sys
import time
import requests
from datetime import datetime

# Configuración
API_BASE_URL = os.getenv("API_URL", "http://localhost:8000")
TIKTOK_API_URL = os.getenv("TIKTOK_API_URL", "http://localhost:8001")

# Archivos disponibles en temp_images
IMAGE_PATH = "temp_images/371001ed-8529-420a-9fe0-e4f7acb49a39.png"  # Imagen PNG
VIDEO_PATH = "temp_images/sora_video_41e491cd.mp4"  # Video MP4 para TikTok

# Usuario de prueba
TEST_USER = {
    "name": "Usuario Test",
    "email": f"test_{datetime.now().strftime('%Y%m%d%H%M%S')}@test.com",
    "password": "password123"
}


class Colors:
    """Colores para output en terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_step(step_num, text):
    print(f"{Colors.CYAN}[Paso {step_num}]{Colors.END} {text}")


def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.END}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.END}")


def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")


class SocialMediaTestClient:
    """Cliente para probar el flujo completo de publicación"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.token = None
        self.user = None
        self.session = requests.Session()
    
    def _headers(self):
        """Headers con autenticación"""
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers
    
    def register(self, name: str, email: str, password: str) -> dict:
        """Registrar un nuevo usuario"""
        response = self.session.post(
            f"{self.base_url}/api/auth/register",
            json={"name": name, "email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.user = data["user"]
            return data
        elif response.status_code == 400:
            # Usuario ya existe, intentar login
            return self.login(email, password)
        else:
            raise Exception(f"Error registrando: {response.status_code} - {response.text}")
    
    def login(self, email: str, password: str) -> dict:
        """Login de usuario existente"""
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.user = data["user"]
            return data
        else:
            raise Exception(f"Error en login: {response.status_code} - {response.text}")
    
    def create_post(self, title: str, content: str) -> dict:
        """Crear un nuevo post"""
        response = self.session.post(
            f"{self.base_url}/api/posts",
            headers=self._headers(),
            json={"title": title, "content": content}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error creando post: {response.status_code} - {response.text}")
    
    def adapt_content(self, post_id: str, networks: list) -> dict:
        """Adaptar contenido para redes sociales"""
        response = self.session.post(
            f"{self.base_url}/api/posts/{post_id}/adapt",
            headers=self._headers(),
            json={"networks": networks, "preview_only": False}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error adaptando contenido: {response.status_code} - {response.text}")
    
    def publish(self, post_id: str, image_url: str = None) -> dict:
        """Publicar en redes sociales (excepto TikTok que necesita video)"""
        response = self.session.post(
            f"{self.base_url}/api/posts/{post_id}/publish",
            headers=self._headers(),
            json={"image_url": image_url}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error publicando: {response.status_code} - {response.text}")
    
    def publish_to_tiktok(self, video_path: str, title: str, post_id: str = None) -> dict:
        """Publicar video en TikTok"""
        response = self.session.post(
            f"{self.base_url}/api/posts/publish-to-tiktok",
            headers=self._headers(),
            json={
                "video_path": video_path,
                "title": title,
                "privacy_level": "PUBLIC_TO_EVERYONE",
                "post_id": post_id
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error publicando en TikTok: {response.status_code} - {response.text}")
    
    def get_post_status(self, post_id: str) -> dict:
        """Obtener estado de publicaciones"""
        response = self.session.get(
            f"{self.base_url}/api/posts/{post_id}/status",
            headers=self._headers()
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error obteniendo estado: {response.status_code} - {response.text}")
    
    def get_post_details(self, post_id: str) -> dict:
        """Obtener detalles del post"""
        response = self.session.get(
            f"{self.base_url}/api/posts/{post_id}",
            headers=self._headers()
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error obteniendo detalles: {response.status_code} - {response.text}")


def run_full_test():
    """Ejecutar test completo de flujo en las 5 redes sociales"""
    
    print_header("TEST DE FLUJO COMPLETO - 5 REDES SOCIALES")
    print_info(f"API URL: {API_BASE_URL}")
    print_info(f"TikTok API URL: {TIKTOK_API_URL}")
    print_info(f"Imagen: {IMAGE_PATH}")
    print_info(f"Video: {VIDEO_PATH}")
    print()
    
    client = SocialMediaTestClient(API_BASE_URL)
    
    # ========================================
    # PASO 1: Registro/Login de usuario
    # ========================================
    print_step(1, "Registro/Login de usuario")
    try:
        result = client.register(TEST_USER["name"], TEST_USER["email"], TEST_USER["password"])
        print_success(f"Usuario autenticado: {client.user['email']}")
        print_info(f"Token obtenido: {client.token[:20]}...")
    except Exception as e:
        print_error(f"Error en autenticación: {e}")
        return False
    
    # ========================================
    # PASO 2: Crear post
    # ========================================
    print_step(2, "Crear post de prueba")
    try:
        post_title = f"Test Automatizado - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        post_content = """
        🚀 Este es un test automatizado del sistema de publicación en redes sociales.
        
        Estamos probando la publicación simultánea en:
        - Facebook 📘
        - Instagram 📷
        - LinkedIn 💼
        - WhatsApp 💬
        - TikTok 🎵
        
        El contenido se adapta automáticamente con IA para cada plataforma.
        
        #TestAutomatizado #SocialMedia #IA #Automatización
        """
        
        result = client.create_post(post_title, post_content)
        post_id = result["data"]["id"]
        print_success(f"Post creado con ID: {post_id}")
    except Exception as e:
        print_error(f"Error creando post: {e}")
        return False
    
    # ========================================
    # PASO 3: Adaptar contenido para las 5 redes
    # ========================================
    print_step(3, "Adaptar contenido para las 5 redes sociales")
    try:
        networks = ["facebook", "instagram", "linkedin", "whatsapp", "tiktok"]
        result = client.adapt_content(post_id, networks)
        
        print_success("Contenido adaptado para todas las redes:")
        for network, content in result["data"]["adaptations"].items():
            preview = content[:80] + "..." if len(content) > 80 else content
            print_info(f"  {network.upper()}: {preview}")
        
        print_info(f"Publicaciones creadas: {len(result['data']['publications'])}")
    except Exception as e:
        print_error(f"Error adaptando contenido: {e}")
        return False
    
    # ========================================
    # PASO 4: Publicar en Facebook, Instagram, LinkedIn, WhatsApp
    # ========================================
    print_step(4, "Publicar en Facebook, Instagram, LinkedIn, WhatsApp")
    try:
        # Usar la imagen para las redes que la soportan
        image_url = f"{API_BASE_URL}/{IMAGE_PATH}"
        print_info(f"Usando imagen: {image_url}")
        
        result = client.publish(post_id, image_url)
        
        print_success("Publicaciones encoladas:")
        for pub in result["data"]["results"]:
            status_icon = "🔄" if pub["status"] == "enqueued" else "❌"
            print_info(f"  {status_icon} {pub['network'].upper()}: {pub['status']}")
    except Exception as e:
        print_error(f"Error publicando: {e}")
        # Continuar con TikTok aunque falle esto
    
    # ========================================
    # PASO 5: Publicar video en TikTok
    # ========================================
    print_step(5, "Publicar video en TikTok")
    try:
        tiktok_title = f"Test Automatizado 🚀 #test #automatizacion"
        result = client.publish_to_tiktok(VIDEO_PATH, tiktok_title, post_id)
        print_success(f"Video enviado a TikTok: {result}")
    except Exception as e:
        print_warning(f"Error publicando en TikTok: {e}")
        print_info("TikTok requiere el backend de TikTok corriendo en puerto 8001")
    
    # ========================================
    # PASO 6: Esperar y verificar estado
    # ========================================
    print_step(6, "Esperar procesamiento y verificar estado")
    print_info("Esperando 10 segundos para que se procesen las publicaciones...")
    time.sleep(10)
    
    try:
        status = client.get_post_status(post_id)
        data = status["data"]
        
        print_success(f"Estado del post: {data['post_status']}")
        print_info(f"Total publicaciones: {data['total_publications']}")
        print()
        
        print(f"{Colors.BOLD}Resumen por estado:{Colors.END}")
        for state, count in data["by_status"].items():
            icon = "✓" if state == "published" else ("🔄" if state == "processing" else ("⏳" if state == "pending" else "✗"))
            color = Colors.GREEN if state == "published" else (Colors.CYAN if state == "processing" else (Colors.WARNING if state == "pending" else Colors.FAIL))
            print(f"  {color}{icon} {state}: {count}{Colors.END}")
        
        print()
        print(f"{Colors.BOLD}Detalle por red:{Colors.END}")
        for pub in data["publications"]:
            network = pub["network"].upper()
            status = pub["status"]
            
            if status == "published":
                icon = "✓"
                color = Colors.GREEN
            elif status == "processing":
                icon = "🔄"
                color = Colors.CYAN
            elif status == "pending":
                icon = "⏳"
                color = Colors.WARNING
            else:
                icon = "✗"
                color = Colors.FAIL
            
            error = f" - Error: {pub['error_message']}" if pub.get("error_message") else ""
            published = f" - Publicado: {pub['published_at']}" if pub.get("published_at") else ""
            
            print(f"  {color}{icon} {network}: {status}{error}{published}{Colors.END}")
    
    except Exception as e:
        print_error(f"Error obteniendo estado: {e}")
    
    # ========================================
    # RESUMEN FINAL
    # ========================================
    print_header("TEST COMPLETADO")
    print_info(f"Post ID: {post_id}")
    print_info(f"Usuario: {TEST_USER['email']}")
    print_info("Revisa el dashboard en http://localhost:5173/dashboard para ver los resultados")
    
    return True


def test_individual_networks():
    """Test individual de cada red social"""
    
    print_header("TEST INDIVIDUAL DE CADA RED SOCIAL")
    
    client = SocialMediaTestClient(API_BASE_URL)
    
    # Login
    try:
        client.register(TEST_USER["name"], TEST_USER["email"], TEST_USER["password"])
        print_success(f"Usuario autenticado: {client.user['email']}")
    except Exception as e:
        print_error(f"Error en autenticación: {e}")
        return
    
    networks = ["facebook", "instagram", "linkedin", "whatsapp", "tiktok"]
    
    for network in networks:
        print(f"\n{Colors.HEADER}--- Testing {network.upper()} ---{Colors.END}")
        
        try:
            # Crear post
            post = client.create_post(
                f"Test {network.title()} - {datetime.now().strftime('%H:%M:%S')}",
                f"Test de publicación individual en {network}. #test #{network}"
            )
            post_id = post["data"]["id"]
            print_success(f"Post creado: {post_id}")
            
            # Adaptar
            client.adapt_content(post_id, [network])
            print_success("Contenido adaptado")
            
            # Publicar
            if network == "tiktok":
                client.publish_to_tiktok(VIDEO_PATH, f"Test TikTok 🎵", post_id)
            else:
                image_url = f"{API_BASE_URL}/{IMAGE_PATH}"
                client.publish(post_id, image_url)
            print_success("Publicación enviada")
            
        except Exception as e:
            print_error(f"Error en {network}: {e}")
        
        time.sleep(2)  # Pequeña pausa entre redes


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test de flujo completo en redes sociales")
    parser.add_argument("--individual", "-i", action="store_true", 
                       help="Ejecutar test individual de cada red")
    parser.add_argument("--api-url", default="http://localhost:8000",
                       help="URL del API (default: http://localhost:8000)")
    
    args = parser.parse_args()
    
    if args.api_url:
        API_BASE_URL = args.api_url
    
    if args.individual:
        test_individual_networks()
    else:
        run_full_test()
