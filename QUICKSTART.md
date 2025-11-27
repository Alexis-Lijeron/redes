# Guía de Inicio Rápido - Social Media Publisher

## 🚀 Inicio Rápido con Docker

### 1. Levantar todos los servicios

```bash
docker-compose up -d
```

Esto inicia:
- PostgreSQL (puerto 5432)
- Redis (puerto 6379)
- API FastAPI (puerto 8000)
- Celery Worker
- Celery Flower (puerto 5555)

### 2. Aplicar migraciones

```bash
docker-compose exec api alembic upgrade head
```

### 3. Cargar datos de ejemplo

```bash
docker-compose exec api python src/database/seed_data.py
```

### 4. Acceder a la aplicación

- **API Swagger**: http://localhost:8000/docs
- **Celery Flower**: http://localhost:5555

---

## 💻 Inicio en Desarrollo Local (sin Docker)

### 1. Instalar PostgreSQL y Redis

**Windows (con Chocolatey)**:
```powershell
choco install postgresql redis
```

**O usar Docker solo para DB**:
```bash
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15-alpine
docker run -d -p 6379:6379 redis:7-alpine
```

### 2. Crear base de datos

```bash
createdb social_media_publisher
```

O con psql:
```sql
CREATE DATABASE social_media_publisher;
```

### 3. Aplicar migraciones

```bash
alembic upgrade head
```

### 4. Cargar datos de ejemplo

```bash
python src/database/seed_data.py
```

### 5. Iniciar API

```bash
python run_api.py
```

### 6. Iniciar Celery Worker (en otra terminal)

```bash
celery -A src.queue.celery_app worker --loglevel=info --pool=solo
```

### 7. (Opcional) Iniciar Flower

```bash
celery -A src.queue.celery_app flower
```

---

## 📝 Ejemplo de Uso Completo

### 1. Crear un nuevo post

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Lanzamiento Nuevo Producto\",\"content\":\"Estamos emocionados de anunciar...\"}"
```

Respuesta:
```json
{
  "success": true,
  "data": {
    "id": "abc-123-def-456",
    "title": "Lanzamiento Nuevo Producto",
    "status": "draft"
  }
}
```

### 2. Adaptar contenido para redes sociales

```bash
curl -X POST http://localhost:8000/api/posts/abc-123-def-456/adapt \
  -H "Content-Type: application/json" \
  -d "{\"networks\":[\"facebook\",\"instagram\",\"linkedin\",\"whatsapp\"]}"
```

### 3. Publicar en todas las redes

```bash
curl -X POST http://localhost:8000/api/posts/abc-123-def-456/publish \
  -H "Content-Type: application/json" \
  -d "{\"image_url\":\"https://ejemplo.com/imagen.jpg\"}"
```

### 4. Verificar estado de publicaciones

```bash
curl http://localhost:8000/api/posts/abc-123-def-456/status
```

---

## 🧪 Endpoints Disponibles

### Posts API (Nuevo Sistema)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/posts` | Crear post |
| GET | `/api/posts` | Listar posts |
| GET | `/api/posts/{id}` | Detalles de post |
| POST | `/api/posts/{id}/adapt` | Adaptar contenido |
| POST | `/api/posts/{id}/publish` | Publicar en redes |
| GET | `/api/posts/{id}/status` | Ver estado |

### Publicación Directa (Sistema Anterior)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/publish/facebook/text` | Facebook texto |
| POST | `/publish/facebook/image` | Facebook imagen |
| POST | `/publish/instagram` | Instagram |
| POST | `/publish/linkedin/text` | LinkedIn texto |
| POST | `/publish/linkedin/image` | LinkedIn imagen |
| POST | `/publish/whatsapp/story` | WhatsApp estado |

---

## 📊 Monitoreo

### Celery Flower

Accede a http://localhost:5555 para ver:
- Tareas en ejecución
- Tareas completadas
- Tareas fallidas
- Estadísticas de workers

### Logs

```bash
# Logs de API
docker-compose logs -f api

# Logs de Celery Worker
docker-compose logs -f celery_worker

# Logs de PostgreSQL
docker-compose logs -f postgres
```

---

## 🛠️ Comandos Útiles

### Docker

```bash
# Detener servicios
docker-compose down

# Reconstruir imágenes
docker-compose build

# Ver servicios corriendo
docker-compose ps

# Reiniciar un servicio específico
docker-compose restart api
```

### Migraciones

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head

# Revertir última migración
alembic downgrade -1

# Ver historial
alembic history
```

### Base de Datos

```bash
# Conectar a PostgreSQL
docker-compose exec postgres psql -U postgres -d social_media_publisher

# Backup
docker-compose exec postgres pg_dump -U postgres social_media_publisher > backup.sql

# Restore
docker-compose exec -T postgres psql -U postgres social_media_publisher < backup.sql
```

---

## 🐛 Troubleshooting

### Error: Cannot connect to database

```bash
# Verificar que PostgreSQL está corriendo
docker-compose ps postgres

# Ver logs
docker-compose logs postgres
```

### Error: Celery no procesa tareas

```bash
# Verificar Redis
docker-compose exec redis redis-cli ping

# Reiniciar worker
docker-compose restart celery_worker
```

### Error: Port already in use

```bash
# Cambiar puertos en docker-compose.yml
# O detener el servicio que usa el puerto
```

---

## 📚 Documentación

- **API Documentation**: `docs/api-documentation.md`
- **Database Schema**: `docs/database-schema.md`
- **Backend Guide**: `docs/clase-04-backend.md`

---

## 🔐 Seguridad

⚠️ **IMPORTANTE**: Antes de producción:

1. Cambiar contraseñas en `.env`
2. Usar variables de entorno seguras
3. Implementar autenticación JWT
4. Configurar CORS apropiadamente
5. Usar HTTPS

---

## ✅ Checklist de Verificación

- [ ] PostgreSQL corriendo
- [ ] Redis corriendo
- [ ] Migraciones aplicadas
- [ ] Seeds cargados
- [ ] API accesible en http://localhost:8000/docs
- [ ] Celery worker procesando tareas
- [ ] Flower accesible en http://localhost:5555
- [ ] Variables de entorno configuradas

---

## 🎯 Próximos Pasos

1. Explorar la API en http://localhost:8000/docs
2. Crear un post de prueba
3. Adaptarlo para diferentes redes
4. Publicarlo y monitorear en Flower
5. Revisar los logs para entender el flujo

¡Listo para publicar en redes sociales! 🚀
