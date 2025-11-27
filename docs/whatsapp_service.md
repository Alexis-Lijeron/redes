# Servicio de WhatsApp - Publicación de Estados (Stories)

## Descripción
Servicio para publicar estados (stories) en WhatsApp con imagen o video y texto usando la API de WHAPI.cloud.

## Configuración

### 1. Agregar Token al archivo `.env`
```env
WHATSAPP_TOKEN=tu_token_aqui
```

### 2. Instalar dependencias
```bash
pip install httpx
```

## Uso

### Importar el servicio
```python
from src.services.whatsapp_service import whatsapp_post_story, whatsapp_post_story_from_url
```

### Ejemplo 1: Publicar estado con imagen local
```python
import asyncio
from src.services.whatsapp_service import whatsapp_post_story

async def publicar_estado():
    result = await whatsapp_post_story(
        media_path="temp_images/mi_imagen.jpg",
        caption="¡Hola! Este es mi estado 📱",
        exclude_contacts=[]
    )
    print(result)

asyncio.run(publicar_estado())
```

### Ejemplo 2: Publicar estado con video
```python
result = await whatsapp_post_story(
    media_path="temp_images/video.mp4",
    caption="Mira este video 🎥",
    exclude_contacts=[]
)
```

### Ejemplo 3: Publicar desde URL
```python
from src.services.whatsapp_service import whatsapp_post_story_from_url

result = await whatsapp_post_story_from_url(
    media_url="https://ejemplo.com/imagen.jpg",
    caption="Estado desde URL 🌐",
    exclude_contacts=[]
)
```

### Ejemplo 4: Excluir contactos específicos
```python
result = await whatsapp_post_story(
    media_path="temp_images/imagen_privada.jpg",
    caption="Solo para algunos contactos 🔒",
    exclude_contacts=["1234567890", "0987654321"]
)
```

## Funciones disponibles

### `whatsapp_post_story()`
Publica un estado con archivo local.

**Parámetros:**
- `media_path` (str): Ruta del archivo (absoluta o relativa a `temp_images/`)
- `caption` (str): Texto del estado
- `exclude_contacts` (Optional[List[str]]): Lista de números a excluir

**Retorna:**
```python
{
    "status": "success",
    "data": {...}  # Respuesta de la API
}
```

### `whatsapp_post_story_from_url()`
Publica un estado descargando el archivo de una URL.

**Parámetros:**
- `media_url` (str): URL del archivo multimedia
- `caption` (str): Texto del estado
- `exclude_contacts` (Optional[List[str]]): Lista de números a excluir

**Retorna:** Mismo formato que `whatsapp_post_story()`

## Formatos soportados

### Imágenes
- `.jpg`, `.jpeg`
- `.png`
- `.gif`

### Videos
- `.mp4`
- `.avi`
- `.mov`
- `.mkv`

## Manejo de errores

El servicio retorna un diccionario con el estado:

**Éxito:**
```python
{
    "status": "success",
    "data": {...}
}
```

**Error:**
```python
{
    "status": "error",
    "status_code": 400,
    "detail": "Mensaje de error"
}
```

## Integración con FastAPI

Ver el archivo `examples/whatsapp_api_integration.py` para ejemplos de endpoints REST.

## Notas importantes

1. El token debe estar configurado en el archivo `.env`
2. Las imágenes/videos se buscan por defecto en `temp_images/`
3. El servicio es asíncrono, debe usarse con `await`
4. Los archivos temporales descargados desde URL se eliminan automáticamente

## Ejemplos completos

Los ejemplos completos están en:
- `examples/whatsapp_example.py` - Uso básico del servicio
- `examples/whatsapp_api_integration.py` - Integración con FastAPI
