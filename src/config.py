import os
from dotenv import load_dotenv
from pathlib import Path

# Asegurar que se carga el .env desde la raíz del proyecto
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Debug: imprimir valores cargados (solo para desarrollo)
print(f"[DEBUG] PAGE_ID cargado: {os.getenv('PAGE_ID')}")
print(f"[DEBUG] IG_USER_ID cargado: {os.getenv('IG_USER_ID')}")
print(f"[DEBUG] PAGE_ACCESS_TOKEN cargado: {'***' + os.getenv('PAGE_ACCESS_TOKEN', '')[-10:] if os.getenv('PAGE_ACCESS_TOKEN') else 'None'}")
print(f"[DEBUG] LINKEDIN_ACCESS_TOKEN cargado: {'***' + os.getenv('LINKEDIN_ACCESS_TOKEN', '')[-10:] if os.getenv('LINKEDIN_ACCESS_TOKEN') else 'None'}")
print(f"[DEBUG] WHATSAPP_TOKEN cargado: {'***' + os.getenv('WHATSAPP_TOKEN', '')[-10:] if os.getenv('WHATSAPP_TOKEN') else 'None'}")

# Facebook e Instagram
PAGE_ID = os.getenv("PAGE_ID", "826165060588207")
IG_USER_ID = os.getenv("IG_USER_ID", "17841453993603227")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "EAALxxxx...xxxx")

# LinkedIn
LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
LINKEDIN_ACCESS_TOKEN = os.getenv("LINKEDIN_ACCESS_TOKEN")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8000/auth/linkedin/callback")
LINKEDIN_ORG_ID = os.getenv("LINKEDIN_ORG_ID")
LINKEDIN_PERSONAL_ID = os.getenv("LINKEDIN_PERSONAL_ID", "ynLeqFuErI")

# WhatsApp
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
