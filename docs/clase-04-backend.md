# Clase 04 - Backend Completo con Base de Datos y Colas

## Objetivos de la Clase

✅ Implementar base de datos PostgreSQL con SQLAlchemy  
✅ Crear sistema de migraciones con Alembic  
✅ Implementar API REST completa para posts  
✅ Configurar sistema de colas con Celery + Redis  
✅ Dockerizar toda la aplicación  

---

## Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────┐
│                      Cliente (HTTP)                       │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│                   FastAPI Application                     │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐         │
│  │   Routes   │─▶│Controllers │─▶│  Services  │         │
│  └────────────┘  └────────────┘  └────────────┘         │
└─────────┬─────────────────────────────┬──────────────────┘
          │                             │
          ▼                             ▼
┌──────────────────┐          ┌──────────────────┐
│   PostgreSQL     │          │   Redis          │
│   (Database)     │          │   (Queue)        │
└──────────────────┘          └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Celery Workers   │
                              │ (Async Tasks)    │
                              └────────┬─────────┘
                                       │
                                       ▼
                              ┌──────────────────┐
                              │ Social Networks  │
                              │ (FB, IG, LI, WA) │
                              └──────────────────┘
```

---

## Estructura del Proyecto

```
/top
├── src/
│   ├── api/
│   │   ├── routes/
│   │   │   └── posts_routes.py          # Rutas REST
│   │   ├── controllers/
│   │   │   └── posts_controller.py      # Lógica de negocio
│   │   ├── services/
│   │   │   ├── post_service.py          # CRUD de posts
│   │   │   ├── adaptation_service.py    # Adaptación con LLM
│   │   │   └── publication_service.py   # CRUD de publications
│   │   └── main.py                      # App FastAPI
│   ├── database/
│   │   ├── models/
│   │   │   ├── post.py                  # Modelo Post
│   │   │   └── publication.py           # Modelo Publication
│   │   ├── migrations/                  # Migraciones Alembic
│   │   ├── database.py                  # Configuración DB
│   │   └── seed_data.py                 # Datos de ejemplo
│   ├── queue/
│   │   ├── celery_app.py               # Configuración Celery
│   │   └── tasks.py                     # Tareas asíncronas
│   └── services/                        # Servicios de redes sociales
├── docs/
│   ├── api-documentation.md             # Esta documentación
│   ├── database-schema.md               # Schema de DB
│   └── clase-04-backend.md              # Guía de clase
├── docker-compose.yml                   # Orquestación de servicios
├── Dockerfile                           # Imagen de la app
├── alembic.ini                          # Config de Alembic
└── requirements.txt                     # Dependencias
```

---

## Paso 1: Configurar Entorno

### 1.1 Variables de Entorno

Agregar al `.env`:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/social_media_publisher

# Redis
REDIS_URL=redis://localhost:6379/0

# Redes sociales (ya configuradas)
OPENAI_API_KEY=...
PAGE_ACCESS_TOKEN=...
WHATSAPP_TOKEN=...
```

### 1.2 Instalar Dependencias

```bash
pip install sqlalchemy psycopg2-binary alembic celery redis
```

---

## Paso 2: Modelos de Base de Datos

### 2.1 Modelo Post

```python
# src/database/models/post.py
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(PostStatus), default=PostStatus.DRAFT)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    publications = relationship("Publication", back_populates="post")
```

### 2.2 Modelo Publication

```python
# src/database/models/publication.py
class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID, ForeignKey("posts.id"))
    network = Column(Enum(SocialNetwork))
    adapted_content = Column(Text)
    status = Column(Enum(PublicationStatus))
    metadata = Column(JSONB, default=dict)
    
    post = relationship("Post", back_populates="publications")
```

---

## Paso 3: Migraciones con Alembic

### 3.1 Inicializar Alembic

```bash
alembic init src/database/migrations
```

### 3.2 Configurar env.py

```python
# src/database/migrations/env.py
from src.database.database import Base
from src.database.models import Post, Publication

target_metadata = Base.metadata
```

### 3.3 Crear Migración

```bash
alembic revision --autogenerate -m "create posts and publications"
```

### 3.4 Aplicar Migración

```bash
alembic upgrade head
```

---

## Paso 4: API REST

### 4.1 Endpoints Implementados

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/posts` | Crear nuevo post |
| GET | `/api/posts` | Listar posts |
| GET | `/api/posts/:id` | Ver detalles |
| POST | `/api/posts/:id/adapt` | Adaptar contenido |
| POST | `/api/posts/:id/publish` | Publicar en redes |
| GET | `/api/posts/:id/status` | Ver estado |

### 4.2 Ejemplo de Uso

```bash
# 1. Crear post
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d '{"title":"Nuevo Producto","content":"Lanzamos..."}'

# 2. Adaptar contenido
curl -X POST http://localhost:8000/api/posts/{id}/adapt \
  -H "Content-Type: application/json" \
  -d '{"networks":["facebook","instagram"],"preview_only":false}'

# 3. Publicar
curl -X POST http://localhost:8000/api/posts/{id}/publish \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://..."}'

# 4. Ver estado
curl http://localhost:8000/api/posts/{id}/status
```

---

## Paso 5: Sistema de Colas con Celery

### 5.1 Configuración de Celery

```python
# src/queue/celery_app.py
celery_app = Celery(
    "social_media_publisher",
    broker=REDIS_URL,
    backend=REDIS_URL
)
```

### 5.2 Tarea de Publicación

```python
# src/queue/tasks.py
@celery_app.task(bind=True, max_retries=3)
def publish_to_network_task(self, publication_id, network, content, image_url):
    # Publicar en la red correspondiente
    result = publish_to_network(network, content, image_url)
    
    # Actualizar estado en DB
    update_publication_status(publication_id, "published", result)
```

### 5.3 Iniciar Worker

```bash
celery -A src.queue.celery_app worker --loglevel=info
```

---

## Paso 6: Docker

### 6.1 docker-compose.yml

```yaml
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: social_media_publisher
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  api:
    build: .
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
  
  celery_worker:
    build: .
    command: celery -A src.queue.celery_app worker --loglevel=info
    depends_on:
      - postgres
      - redis
```

### 6.2 Levantar Servicios

```bash
docker-compose up -d
```

---

## Paso 7: Seeds (Datos de Ejemplo)

### 7.1 Ejecutar Seeds

```bash
python src/database/seed_data.py
```

Crea 5 posts de ejemplo:
- Lanzamiento de producto
- Evento de empresa
- Mejoras en servicio
- Historia de éxito
- Oferta especial

---

## Flujo Completo de Trabajo

### 1. Crear Post
```python
POST /api/posts
{
  "title": "Nuevo Producto Tech",
  "content": "Lanzamos innovación..."
}
```

### 2. Adaptar para Redes
```python
POST /api/posts/{id}/adapt
{
  "networks": ["facebook", "instagram", "linkedin", "whatsapp"],
  "preview_only": false
}
```

Response: Crea 4 publications en estado "pending"

### 3. Publicar
```python
POST /api/posts/{id}/publish
{
  "image_url": "https://ejemplo.com/imagen.jpg"
}
```

- Encola 4 tareas en Celery
- Cada worker procesa una red
- Actualiza estado a "processing" → "published"/"failed"

### 4. Monitorear Estado
```python
GET /api/posts/{id}/status
```

Response:
```json
{
  "total_publications": 4,
  "by_status": {
    "published": 3,
    "failed": 1
  },
  "publications": [...]
}
```

---

## Monitoreo y Debugging

### Celery Flower

Monitor visual de tareas:
```bash
http://localhost:5555
```

### Logs de Postgres

```bash
docker logs social_media_db
```

### Logs de Celery

```bash
docker logs social_media_celery_worker
```

### Logs de API

```bash
docker logs social_media_api
```

---

## Mejoras Futuras

1. **Autenticación**: JWT para proteger endpoints
2. **Webhooks**: Notificaciones de estado
3. **Scheduling**: Programar publicaciones
4. **Analytics**: Dashboard de métricas
5. **Retry Logic**: Reintentos inteligentes
6. **Image Processing**: Optimización automática
7. **Multi-tenancy**: Soporte para múltiples usuarios

---

## Troubleshooting

### Error: Cannot connect to database

```bash
# Verificar que postgres está corriendo
docker ps | grep postgres

# Ver logs
docker logs social_media_db
```

### Error: Celery worker not processing

```bash
# Verificar Redis
docker exec -it social_media_redis redis-cli ping

# Reiniciar worker
docker restart social_media_celery_worker
```

### Error: Migrations fail

```bash
# Resetear migraciones
alembic downgrade base
alembic upgrade head
```

---

## Recursos

- **FastAPI**: https://fastapi.tiangolo.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Celery**: https://docs.celeryq.dev/
- **Docker**: https://docs.docker.com/

---

## Conclusión

Has implementado:
✅ Base de datos relacional con PostgreSQL  
✅ ORM con SQLAlchemy  
✅ Migraciones con Alembic  
✅ API REST completa  
✅ Sistema de colas asíncrono  
✅ Dockerización completa  
✅ Monitoreo con Flower  

**Sistema listo para producción!** 🚀
