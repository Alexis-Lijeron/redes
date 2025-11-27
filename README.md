# Motor de Transformación Digital de Contenidos y Publicación en Redes Sociales

Plataforma avanzada que transforma material original en publicaciones optimizadas para múltiples canales digitales usando OpenAI GPT-3.5 Turbo. Crea versiones personalizadas para Facebook, Instagram, LinkedIn, TikTok y WhatsApp con características únicas por canal, y permite publicar directamente en Facebook e Instagram mediante sus APIs.

##  Funcionalidades

- **Interface Intuitiva**: Entrada sencilla de encabezado, material y selección de plataformas
- **Transformación Inteligente**: Estilo, extensión y tono específicos por canal digital
- **Publicación Directa**: Integración con Facebook e Instagram APIs para publicación automática
- **API REST**: Endpoints para publicar texto e imágenes en Facebook e Instagram
- **Campos Especializados**: 
  - Instagram: `suggested_image_prompt` para contenido visual
  - TikTok: `suggested_video_prompt` para contenido audiovisual
- **Validación Automática**: Control de límites de caracteres y estructura JSON
- **Sistema de Pruebas**: Casos integrados para testing completo

##  Prerrequisitos

- Python 3.8+
- Token API de OpenAI
- Conectividad a internet

##  Configuración Inicial

1. **Clonar repositorio**
```bash
git clone <repository-url>
cd proy2
```

2. **Instalar paquetes requeridos**
```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env y agregar:
# - OPENAI_API_KEY (para transformación de contenido)
# - PAGE_ACCESS_TOKEN (para Facebook/Instagram)
# - PAGE_ID (ID de tu página de Facebook) 
# - IG_USER_ID (ID de tu cuenta de Instagram Business)
```

## Utilización

### Motor Principal

```bash
python src/services/llm_adapter.py

# Proceso:
# 1. Ingresa encabezado
# 2. Ingresa material (Enter doble para terminar)  
# 3. Selecciona plataformas (números, nombres, o 'a' para todas)
# 4. Visualiza transformación
# 5. Opcionalmente guarda en JSON
```

### API de Publicación en Redes Sociales

```bash
# Ejecutar la API
python run_api.py

# La API estará disponible en: http://localhost:8000
# Documentación interactiva en: http://localhost:8000/docs
```

#### Endpoints Principales (Integración LLM):

**1. Generar contenido con LLM (con opción de publicación automática):**
```bash
POST /generate-content
Content-Type: application/json

{
  "heading": "Lanzamiento de Nueva Funcionalidad",
  "material": "Descripción completa del contenido a transformar...",
  "platforms": ["facebook", "instagram"],
  "auto_publish": false,
  "image_url": "https://example.com/image.jpg"
}
```

**2. Vista previa del contenido generado:**
```bash
POST /preview-content
Content-Type: application/json

{
  "heading": "Mi encabezado",
  "material": "Mi material original...",
  "platforms": ["facebook", "instagram"]
}
```

#### Endpoints de Publicación Directa:

**3. Publicar imagen en Instagram:**
```bash
POST /publish/instagram
Content-Type: application/json

{
  "image_url": "https://example.com/image.jpg",
  "caption": "Mi caption para Instagram"
}
```

**4. Publicar texto en Facebook:**
```bash
POST /publish/facebook/text
Content-Type: application/json

{
  "message": "Mi mensaje para Facebook"
}
```

**5. Publicar imagen en Facebook:**
```bash
POST /publish/facebook/image
Content-Type: application/json

{
  "image_url": "https://example.com/image.jpg",
  "caption": "Mi caption para Facebook"
}
```

#### Ejemplos de Uso Integrado:

```bash
# Probar la integración completa
python example_llm_integration.py

# Probar endpoints individuales
python example_usage.py
```

### Sistema de Validación

```bash
# Ver casos disponibles
python tests/test_all_cases.py --list

# Ejecutar caso específico
python tests/test_all_cases.py --caso empresarial

# Ejecutar todos los casos
python tests/test_all_cases.py --all

# Modo interactivo
python tests/test_all_cases.py --interactive
```

### Implementación Programática

```python
from src.services.llm_adapter import process_content

input_data = {
    "encabezado": "Encabezado del material",
    "material": "Material completo...",
    "target_platforms": ["facebook", "instagram", "tiktok"]
}

results = process_content(input_data)
```

### Sistema de Validación Integrado

El sistema incluye 3 casos de validación integrados:

```bash
# Ver casos disponibles
python tests/test_all_cases.py --list

# Ejecutar caso específico
python tests/test_all_cases.py --caso empresarial
python tests/test_all_cases.py --caso lanzamiento
python tests/test_all_cases.py --caso actividad

# Ejecutar todos los casos
python tests/test_all_cases.py --all

# Modo interactivo de validación
python tests/test_all_cases.py --interactive
```

##  Estructura de Entrada

```json
{
  "encabezado": "Encabezado del material",
  "material": "Material original completo...",
  "target_platforms": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
}
```

##  Estructura de Salida

```json
{
  "facebook": {
    "text": "🎉 Excelente noticia para nuestra comunidad...",
    "hashtags": ["#Desarrollo", "#Digital"],
    "character_count": 245,
    "tone": "conversacional"
  },
  "instagram": {
    "text": "✨ Nueva funcionalidad impresionante...",
    "hashtags": ["#Digital", "#Transformacion"],
    "character_count": 180,
    "tone": "inspirador",
    "suggested_image_prompt": "Interfaz moderna con colores vibrantes..."
  },
  "tiktok": {
    "text": "🔥 Esto revolucionará todo...",
    "hashtags": ["#DigitalTok", "#Transformacion"],
    "character_count": 120,
    "tone": "energético",
    "suggested_video_prompt": "Video dinámico mostrando características con música trending..."
  }
}
```

##  Configuración por Plataforma Digital

| Plataforma | Estilo | Límite | Etiquetas | Creatividad | Campo Especial |
|------------|--------|--------|-----------|-------------|----------------|
| **Facebook** | Conversacional-profesional | 63,206 | 3-5 | 0.7 | - |
| **Instagram** | Visual-inspirador | 2,200 | 5-10 | 0.8 | `suggested_image_prompt` |
| **LinkedIn** | Profesional | 3,000 | 3-5 | 0.5 | - |
| **TikTok** | Dinámico-viral | 4,000 | 3-8 | 0.9 | `suggested_video_prompt` |
| **WhatsApp** | Personal-directo | 4,000 | 1-2 | 0.6 | - |

##  Arquitectura del Proyecto

```
top/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py               # API FastAPI principal
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_adapter.py        # Motor principal de transformación
│   │   ├── instagram_service.py  # Servicio de Instagram
│   │   └── facebook_service.py   # Servicio de Facebook
│   └── config.py                 # Configuración y variables de entorno
├── tests/
│   ├── test_all_cases.py         # Sistema de validación unificado
│   ├── test_social_media_services.py  # Tests para servicios de redes sociales
│   └── test_api.py               # Tests para la API
├── docs/
│   ├── prompts.md
│   └── clase-02-desarrollo.md
├── run_api.py                    # Script para ejecutar la API
├── requirements.txt
├── .env.example
└── README.md
```

##  Casos de Validación

El sistema incluye 3 casos predefinidos en `test_all_cases.py`:

- **empresarial**: Logro organizacional (15K usuarios)
- **lanzamiento**: Debut de InnovatePro 3.0 con ML  
- **actividad**: Congreso DigitalNext 2025

**Características del sistema de validación**:
- Verificación automática de campos específicos por plataforma
- Análisis de elementos clave por tipo de material
- Resumen detallado por canal digital
- Almacenamiento automático de resultados con timestamp

##  Configuración Avanzada

### Variables de Entorno

```bash
# Variables para OpenAI (transformación de contenido)
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-3.5-turbo  # Opcional, por defecto gpt-3.5-turbo
LOG_LEVEL=INFO              # Opcional, por defecto INFO

# Variables para Facebook e Instagram APIs
PAGE_ID=826165060588207                    # ID de tu página de Facebook
IG_USER_ID=17841453993603227              # ID de tu cuenta de Instagram Business  
PAGE_ACCESS_TOKEN=EAALxxxx...xxxx         # Token de acceso de tu página de Facebook
```

### Configuración de Facebook/Instagram API

Para obtener los tokens y IDs necesarios:

1. **Facebook Developer Console**: https://developers.facebook.com/
2. **Crear una aplicación** y agregar productos Facebook Login e Instagram Basic Display
3. **Obtener PAGE_ACCESS_TOKEN**: 
   - Graph API Explorer → Seleccionar tu página → Generar token
4. **Obtener PAGE_ID**: ID de tu página de Facebook Business
5. **Obtener IG_USER_ID**: ID de tu cuenta de Instagram Business conectada a Facebook

### Personalización de Prompts

Los prompts se pueden personalizar editando el método `get_system_prompt()` en `src/services/llm_adapter.py`.

##  Desarrollo

### Agregar Nueva Plataforma Digital

1. Actualizar `PLATFORM_LIMITS` y `CREATIVITY_CONFIG`
2. Crear instrucciones en `get_platform_instructions()`
3. Si requiere campo especial, agregarlo en `build_transformation_request()`

### Ejecutar Validaciones

```bash
# Casos disponibles
python tests/test_all_cases.py --list

# Caso específico
python tests/test_all_cases.py --caso empresarial

# Todos los casos
python tests/test_all_cases.py --all

# Modo interactivo
python tests/test_all_cases.py --interactive
```

## Métricas y Registro

El sistema incluye registro detallado:

- Procesamiento por plataforma digital
- Tiempo de respuesta del AI
- Errores y advertencias
- Validaciones de límites

##  Resolución de Problemas

### Error: "OPENAI_API_KEY not found"
```bash
export OPENAI_API_KEY=sk-your-key-here
# o agregar a .env
```

### Error: "Rate limit exceeded"
- Verificar límites de tu plan OpenAI
- Implementar retry con backoff exponencial

### Error: "JSON parsing failed"
- El AI devolvió formato incorrecto
- Revisar instrucciones o aumentar max_tokens
