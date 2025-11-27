# Sistema de Colas - Guía Detallada

## 🔄 ¿Cómo Funciona el Sistema de Colas?

### Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    Cliente HTTP                              │
│              POST /api/posts/{id}/publish                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI API                                │
│  1. Crea 4 tareas en Redis (una por red)                   │
│  2. Responde inmediatamente (no espera)                     │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Redis Queue                             │
│  [Task FB] [Task IG] [Task LI] [Task WA]                    │
└──┬────────┬──────────┬──────────┬──────────────────────────┘
   │        │          │          │
   │        │          │          │  (Se procesan en paralelo)
   │        │          │          │
   ▼        ▼          ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Worker 1│ │Worker 2│ │Worker 3│ │Worker 4│
│   FB   │ │   IG   │ │   LI   │ │   WA   │
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │
    └──────────┴──────────┴──────────┘
                    │
                    ▼
          ┌──────────────────┐
          │    PostgreSQL     │
          │ (Actualiza estado)│
          └──────────────────┘
```

---

## ⚡ Procesamiento Paralelo vs Secuencial

### Sin Colas (Secuencial) ❌

```python
# Código síncrono tradicional
def publish_all():
    facebook_service.publish()    # 3 segundos
    instagram_service.publish()   # 5 segundos
    linkedin_service.publish()    # 4 segundos
    whatsapp_service.publish()    # 2 segundos
    
    # Total: 14 segundos esperando
```

### Con Colas (Paralelo) ✅

```python
# Código con Celery
def publish_all():
    task1 = publish_fb.delay()     # Encola y continúa
    task2 = publish_ig.delay()     # Encola y continúa
    task3 = publish_li.delay()     # Encola y continúa
    task4 = publish_wa.delay()     # Encola y continúa
    
    # Responde en ~100ms
    # Workers procesan en paralelo
    # Total: ~5 segundos (el más lento)
```

---

## 🔧 Configuraciones de Workers

### Opción 1: Un Worker con Múltiples Procesos (Actual)

```yaml
# docker-compose.yml
celery_worker:
  command: celery -A src.queue.celery_app worker --loglevel=info --concurrency=4
```

- **1 container** con **4 procesos**
- Puede procesar **4 tareas simultáneamente**
- Mejor para CPU-bound tasks

### Opción 2: Múltiples Workers (Escalabilidad)

```yaml
# docker-compose.yml
celery_worker_1:
  command: celery -A src.queue.celery_app worker --loglevel=info -n worker1@%h

celery_worker_2:
  command: celery -A src.queue.celery_app worker --loglevel=info -n worker2@%h

celery_worker_3:
  command: celery -A src.queue.celery_app worker --loglevel=info -n worker3@%h

celery_worker_4:
  command: celery -A src.queue.celery_app worker --loglevel=info -n worker4@%h
```

- **4 containers** independientes
- Cada uno procesa tareas de la cola
- Mejor para escalar horizontalmente

### Opción 3: Worker con Threads (I/O Bound)

```yaml
# Para tareas de red (publicar en APIs)
celery_worker:
  command: celery -A src.queue.celery_app worker --pool=threads --concurrency=10
```

- **10 threads** en paralelo
- Ideal para operaciones de red/API
- Menos uso de memoria que procesos

---

## 📊 Ejemplo Real

### Timeline de Publicación

```
Tiempo (segundos)
0    1    2    3    4    5    6
│────┼────┼────┼────┼────┼────│
│
├─ API recibe request (0.1s)
│
├─ Encola 4 tareas (0.05s)
│
├─ API responde (0.15s total) ✅
│
├─ Worker 1: Facebook ─────────┐ (3s)
├─ Worker 2: Instagram ────────┼──┐ (5s)
├─ Worker 3: LinkedIn ─────────┤  │ (4s)
└─ Worker 4: WhatsApp ────┐    │  │ (2s)
                          ↓    ↓  ↓
                      Todos terminan en ~5s
```

**Sin colas**: 14 segundos  
**Con colas**: 5 segundos (paralelo)  
**Mejora**: 64% más rápido

---

## 🎯 Flujo Detallado del Código

### 1. API Encola las Tareas

```python
# src/api/controllers/posts_controller.py

def publish_to_networks(self, db, post_id, image_url):
    publications = get_publications_by_post(db, post_id)
    
    results = []
    for pub in publications:
        if pub.status == PublicationStatus.PENDING:
            # ⚡ Encola tarea (NO espera a que termine)
            task = publish_to_network_task.delay(
                str(pub.id),
                pub.network.value,
                pub.adapted_content,
                image_url
            )
            
            # Actualiza estado a "processing"
            update_publication_status(db, pub.id, "processing")
            
            results.append({
                "network": pub.network.value,
                "status": "enqueued",
                "task_id": task.id  # ID para rastrear la tarea
            })
    
    return {"results": results}  # Responde inmediatamente
```

### 2. Worker Procesa la Tarea

```python
# src/queue/tasks.py

@celery_app.task(bind=True, max_retries=3)
def publish_to_network_task(self, publication_id, network, content, image_url):
    """
    Esta tarea se ejecuta en un worker separado
    Puede haber múltiples workers procesando en paralelo
    """
    try:
        # Publicar en la red social
        if network == "facebook":
            result = _publish_to_facebook(content, image_url)
        elif network == "instagram":
            result = _publish_to_instagram(content, image_url)
        # ... otras redes
        
        # Actualizar estado a "published"
        update_publication_status(
            db,
            UUID(publication_id),
            PublicationStatus.PUBLISHED,
            metadata=result
        )
        
        return {"status": "success", "result": result}
        
    except Exception as exc:
        # Si falla, actualizar a "failed"
        update_publication_status(
            db,
            UUID(publication_id),
            PublicationStatus.FAILED,
            error_message=str(exc)
        )
        
        # Reintentar automáticamente (hasta 3 veces)
        raise self.retry(exc=exc, countdown=60)  # Espera 1 min
```

### 3. Usuario Verifica el Estado

```python
# El usuario puede consultar el estado en cualquier momento

GET /api/posts/{id}/status

Response:
{
  "by_status": {
    "pending": 0,
    "processing": 1,    # LinkedIn aún procesando
    "published": 3,     # FB, IG, WA ya terminaron
    "failed": 0
  },
  "publications": [
    {
      "network": "facebook",
      "status": "published",
      "published_at": "2025-11-25T10:30:15"
    },
    {
      "network": "linkedin",
      "status": "processing",
      "published_at": null
    },
    ...
  ]
}
```

---

## 🚀 Ventajas del Sistema de Colas

### 1. ⚡ Velocidad
- API responde en milisegundos
- Publicaciones en paralelo
- Usuario no espera

### 2. 🔄 Reintentos Automáticos
```python
@celery_app.task(max_retries=3)
def publish_task(self, ...):
    try:
        publish()
    except Exception as e:
        # Reintenta automáticamente
        raise self.retry(exc=e, countdown=60)
```

### 3. 📊 Monitoreo con Flower
- Ver tareas en tiempo real
- Estadísticas de éxito/fallo
- Tiempos de ejecución

### 4. 🛡️ Resiliencia
- Si falla una red, las otras continúan
- Reintentos automáticos
- No bloquea la API

### 5. 📈 Escalabilidad
- Agregar más workers fácilmente
- Balanceo de carga automático
- Procesar miles de publicaciones

---

## 🔍 Monitoreo en Tiempo Real

### Celery Flower (http://localhost:5555)

```
┌─────────────────────────────────────────┐
│         Celery Flower Dashboard         │
├─────────────────────────────────────────┤
│ Active Tasks:                           │
│ • Task 1: publish_to_facebook [RUNNING] │
│ • Task 2: publish_to_instagram [RUNNING]│
│ • Task 3: publish_to_linkedin [SUCCESS] │
│ • Task 4: publish_to_whatsapp [SUCCESS] │
│                                         │
│ Workers:                                │
│ • worker@localhost [ONLINE] 4 tasks    │
│                                         │
│ Statistics:                             │
│ • Success: 89%                          │
│ • Failed: 11%                           │
│ • Avg time: 3.2s                        │
└─────────────────────────────────────────┘
```

---

## ⚙️ Configuración Recomendada

### Para Producción

```yaml
# docker-compose.yml
celery_worker:
  command: celery -A src.queue.celery_app worker 
           --pool=threads 
           --concurrency=20 
           --loglevel=info
           --max-tasks-per-child=1000
  replicas: 3  # 3 containers con 20 threads cada uno
```

**Capacidad**: 60 tareas simultáneas (3 workers × 20 threads)

### Para Desarrollo

```bash
# Terminal local
celery -A src.queue.celery_app worker --pool=solo --loglevel=info
```

**Capacidad**: 1 tarea a la vez (más fácil de debuggear)

---

## 🎬 Demo de Uso

```bash
# Terminal 1: Iniciar API
python run_api.py

# Terminal 2: Iniciar Worker
celery -A src.queue.celery_app worker --loglevel=info

# Terminal 3: Hacer petición
curl -X POST http://localhost:8000/api/posts/abc-123/publish \
  -H "Content-Type: application/json" \
  -d '{"image_url":"https://ejemplo.com/img.jpg"}'

# Respuesta instantánea:
{
  "results": [
    {"network": "facebook", "status": "enqueued", "task_id": "..."},
    {"network": "instagram", "status": "enqueued", "task_id": "..."}
  ]
}

# En Terminal 2 (Worker) verás:
[2025-11-25 10:30:15] Task publish_to_network_task[abc-123-fb] received
[2025-11-25 10:30:15] Task publish_to_network_task[abc-123-ig] received
[2025-11-25 10:30:17] Task publish_to_network_task[abc-123-fb] succeeded: {...}
[2025-11-25 10:30:19] Task publish_to_network_task[abc-123-ig] succeeded: {...}
```

---

## 🆚 Comparación

| Característica | Sin Colas | Con Colas |
|----------------|-----------|-----------|
| Tiempo de respuesta | 14 segundos | 0.15 segundos |
| Procesamiento | Secuencial | Paralelo |
| Si falla una red | Se detiene todo | Otras continúan |
| Escalabilidad | Limitada | Ilimitada |
| Monitoreo | Manual | Automático (Flower) |
| Reintentos | Manual | Automático |

---

## 💡 Conclusión

**Sí, el sistema crea un "hilo" (task) para cada red social y las publica TODAS en paralelo.**

- ✅ Cada red se procesa independientemente
- ✅ Si una falla, las otras continúan
- ✅ Reintentos automáticos
- ✅ Monitoreo en tiempo real
- ✅ Escalable horizontalmente

**Es como tener 4 asistentes trabajando simultáneamente en lugar de 1 haciendo todo secuencialmente.**
