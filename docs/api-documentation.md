# API Documentation - Social Media Publisher

## Descripción General

API REST completa para gestión de contenido y publicación automatizada en múltiples redes sociales con adaptación inteligente usando IA.

## Base URL

```
http://localhost:8000
```

## Documentación Interactiva

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Endpoints de Posts

### 1. Crear Nuevo Post

Crea un post en estado 'draft' que puede ser adaptado y publicado posteriormente.

**Endpoint**: `POST /api/posts`

**Request Body**:
```json
{
  "title": "Título del post",
  "content": "Contenido completo del post..."
}
```

**Response Success (200)**:
```json
{
  "success": true,
  "message": "Post creado exitosamente",
  "data": {
    "id": "uuid-del-post",
    "title": "Título del post",
    "content": "Contenido...",
    "status": "draft",
    "created_at": "2025-11-25T10:00:00",
    "publications_count": 0
  }
}
```

---

### 2. Listar Posts

Lista todos los posts con paginación y filtro opcional por estado.

**Endpoint**: `GET /api/posts`

**Query Parameters**:
- `skip` (int, opcional): Número de posts a omitir (default: 0)
- `limit` (int, opcional): Máximo de posts a retornar (default: 100)
- `status` (string, opcional): Filtrar por estado (`draft`, `processing`, `published`, `failed`)

**Ejemplos**:
```
GET /api/posts
GET /api/posts?status=draft
GET /api/posts?skip=10&limit=20
```

**Response Success (200)**:
```json
{
  "success": true,
  "count": 5,
  "data": [
    {
      "id": "uuid-1",
      "title": "Post 1",
      "status": "draft",
      ...
    },
    ...
  ]
}
```

---

### 3. Ver Detalles de un Post

Obtiene los detalles completos de un post incluyendo todas sus publicaciones.

**Endpoint**: `GET /api/posts/{post_id}`

**Path Parameters**:
- `post_id` (UUID): ID del post

**Response Success (200)**:
```json
{
  "success": true,
  "data": {
    "id": "uuid-del-post",
    "title": "Título",
    "content": "Contenido...",
    "status": "published",
    "created_at": "2025-11-25T10:00:00",
    "publications": [
      {
        "id": "pub-uuid-1",
        "network": "facebook",
        "status": "published",
        "adapted_content": "Contenido adaptado...",
        "published_at": "2025-11-25T10:30:00",
        "metadata": {...}
      },
      ...
    ]
  }
}
```

---

### 4. Adaptar Contenido con LLM

Adapta el contenido del post para diferentes redes sociales usando IA. Crea registros de Publication en estado 'pending' para cada red.

**Endpoint**: `POST /api/posts/{post_id}/adapt`

**Path Parameters**:
- `post_id` (UUID): ID del post

**Request Body**:
```json
{
  "networks": ["facebook", "instagram", "linkedin", "whatsapp"],
  "preview_only": false
}
```

**Networks soportadas**:
- `facebook`
- `instagram`
- `linkedin`
- `tiktok`
- `whatsapp`

**Response Success (200)**:
```json
{
  "success": true,
  "message": "Contenido adaptado exitosamente",
  "data": {
    "post_id": "uuid-del-post",
    "adaptations": {
      "facebook": "Contenido adaptado para Facebook...",
      "instagram": "Contenido adaptado para Instagram... #hashtags",
      "linkedin": "Contenido adaptado para LinkedIn...",
      "whatsapp": "Contenido adaptado para WhatsApp..."
    },
    "publications": [
      {
        "id": "pub-uuid",
        "network": "facebook",
        "status": "pending",
        ...
      },
      ...
    ]
  }
}
```

**Preview Mode**:
```json
{
  "networks": ["facebook", "instagram"],
  "preview_only": true
}
```

Response incluye metadata adicional:
```json
{
  "success": true,
  "message": "Vista previa generada",
  "data": {
    "post_id": "uuid",
    "preview": {
      "facebook": {
        "adapted_text": "...",
        "hashtags": ["#tech", "#innovation"],
        "image_suggestion": "Imagen moderna de tecnología",
        "character_count": 250
      },
      ...
    }
  }
}
```

---

### 5. Publicar en Redes Sociales

Publica el contenido adaptado en todas las redes sociales configuradas. Las publicaciones se procesan de forma asíncrona usando Celery.

**Endpoint**: `POST /api/posts/{post_id}/publish`

**Path Parameters**:
- `post_id` (UUID): ID del post

**Request Body**:
```json
{
  "image_url": "https://ejemplo.com/imagen.jpg"
}
```

**Response Success (200)**:
```json
{
  "success": true,
  "message": "Publicaciones encoladas para procesamiento",
  "data": {
    "post_id": "uuid",
    "results": [
      {
        "publication_id": "pub-uuid-1",
        "network": "facebook",
        "status": "enqueued",
        "task_id": "celery-task-id-1"
      },
      {
        "publication_id": "pub-uuid-2",
        "network": "instagram",
        "status": "enqueued",
        "task_id": "celery-task-id-2"
      },
      ...
    ]
  }
}
```

---

### 6. Ver Estado de Publicaciones

Obtiene el estado actual de todas las publicaciones de un post. Útil para verificar el progreso después de publicar.

**Endpoint**: `GET /api/posts/{post_id}/status`

**Path Parameters**:
- `post_id` (UUID): ID del post

**Response Success (200)**:
```json
{
  "success": true,
  "data": {
    "post_id": "uuid",
    "post_status": "published",
    "total_publications": 4,
    "by_status": {
      "pending": 0,
      "processing": 1,
      "published": 2,
      "failed": 1
    },
    "publications": [
      {
        "id": "pub-uuid-1",
        "network": "facebook",
        "status": "published",
        "published_at": "2025-11-25T10:30:00",
        "error_message": null,
        "metadata": {
          "platform": "facebook",
          "post_id": "fb-post-id-123"
        }
      },
      {
        "id": "pub-uuid-2",
        "network": "instagram",
        "status": "failed",
        "published_at": null,
        "error_message": "Error: Image URL required",
        "metadata": {}
      },
      ...
    ]
  }
}
```

---

## Flujo de Trabajo Completo

### Ejemplo: Crear y Publicar Contenido

1. **Crear Post**:
```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Lanzamiento Nuevo Producto",
    "content": "Estamos emocionados de anunciar..."
  }'
```

2. **Adaptar Contenido** (Vista Previa):
```bash
curl -X POST http://localhost:8000/api/posts/{post_id}/adapt \
  -H "Content-Type: application/json" \
  -d '{
    "networks": ["facebook", "instagram", "linkedin"],
    "preview_only": true
  }'
```

3. **Adaptar y Guardar**:
```bash
curl -X POST http://localhost:8000/api/posts/{post_id}/adapt \
  -H "Content-Type: application/json" \
  -d '{
    "networks": ["facebook", "instagram", "linkedin", "whatsapp"],
    "preview_only": false
  }'
```

4. **Publicar en Redes**:
```bash
curl -X POST http://localhost:8000/api/posts/{post_id}/publish \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://ejemplo.com/imagen.jpg"
  }'
```

5. **Verificar Estado**:
```bash
curl http://localhost:8000/api/posts/{post_id}/status
```

---

## Estados

### Estados de Post
- `draft`: Borrador inicial
- `processing`: Siendo procesado/adaptado
- `published`: Publicado exitosamente
- `failed`: Falló la publicación

### Estados de Publication
- `pending`: Esperando publicación
- `processing`: Publicando en la red
- `published`: Publicado exitosamente
- `failed`: Falló la publicación

---

## Códigos de Error

- `200`: Success
- `400`: Bad Request (datos inválidos)
- `404`: Not Found (recurso no encontrado)
- `500`: Internal Server Error

---

## Endpoints Heredados (Compatibilidad)

Los endpoints directos de publicación siguen disponibles:

- `POST /publish/facebook/text`
- `POST /publish/facebook/image`
- `POST /publish/instagram`
- `POST /publish/linkedin/text`
- `POST /publish/linkedin/image`
- `POST /publish/whatsapp/story`
- `POST /publish/whatsapp/story-from-url`

Ver documentación de Swagger para detalles.

---

## Monitoreo

### Celery Flower (Monitor de Tareas)
```
http://localhost:5555
```

Permite monitorear:
- Tareas en ejecución
- Tareas completadas
- Tareas fallidas
- Workers activos
- Estadísticas de rendimiento
