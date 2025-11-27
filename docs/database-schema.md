# Database Schema - Social Media Publisher

## Diagrama de Relaciones

```
┌─────────────────────────────┐
│         Posts               │
├─────────────────────────────┤
│ id (UUID, PK)              │
│ title (VARCHAR 500)        │
│ content (TEXT)             │
│ created_at (TIMESTAMP)     │
│ updated_at (TIMESTAMP)     │
│ status (ENUM)              │
│   - draft                  │
│   - processing             │
│   - published              │
│   - failed                 │
└──────────┬──────────────────┘
           │
           │ 1:N
           │
┌──────────▼──────────────────┐
│     Publications            │
├─────────────────────────────┤
│ id (UUID, PK)              │
│ post_id (UUID, FK)         │
│ network (ENUM)             │
│   - facebook               │
│   - instagram              │
│   - linkedin               │
│   - tiktok                 │
│   - whatsapp               │
│ adapted_content (TEXT)     │
│ status (ENUM)              │
│   - pending                │
│   - processing             │
│   - published              │
│   - failed                 │
│ published_at (TIMESTAMP)   │
│ error_message (TEXT)       │
│ metadata (JSONB)           │
│ created_at (TIMESTAMP)     │
│ updated_at (TIMESTAMP)     │
└─────────────────────────────┘
```

---

## Tabla: `posts`

Almacena el contenido original que será adaptado y publicado en diferentes redes sociales.

### Columnas

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY | Identificador único del post |
| `title` | VARCHAR(500) | NOT NULL | Título del post |
| `content` | TEXT | NOT NULL | Contenido completo del post |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Fecha de última actualización |
| `status` | ENUM | NOT NULL, DEFAULT 'draft' | Estado del post |

### Valores ENUM para `status`

- `draft`: Post creado pero no procesado
- `processing`: Post siendo adaptado para redes
- `published`: Post publicado en al menos una red
- `failed`: Falló el procesamiento del post

### Índices

```sql
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
```

---

## Tabla: `publications`

Almacena cada publicación individual en una red social específica.

### Columnas

| Columna | Tipo | Restricciones | Descripción |
|---------|------|---------------|-------------|
| `id` | UUID | PRIMARY KEY | Identificador único de la publicación |
| `post_id` | UUID | FOREIGN KEY, NOT NULL | Referencia al post original |
| `network` | ENUM | NOT NULL | Red social donde se publica |
| `adapted_content` | TEXT | | Contenido adaptado para la red específica |
| `status` | ENUM | NOT NULL, DEFAULT 'pending' | Estado de la publicación |
| `published_at` | TIMESTAMP | | Fecha de publicación exitosa |
| `error_message` | TEXT | | Mensaje de error si falló |
| `extra_data` | JSONB | DEFAULT '{}' | Datos adicionales (IDs, URLs, etc.) |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `updated_at` | TIMESTAMP | DEFAULT NOW() | Fecha de última actualización |

### Valores ENUM para `network`

- `facebook`: Facebook Page/Profile
- `instagram`: Instagram Business Account
- `linkedin`: LinkedIn Personal/Organization
- `tiktok`: TikTok Account
- `whatsapp`: WhatsApp Status/Story

### Valores ENUM para `status`

- `pending`: Esperando ser publicada
- `processing`: Publicación en progreso
- `published`: Publicada exitosamente
- `failed`: Falló la publicación

### Estructura de `extra_data` (JSONB)

Ejemplo para publicación exitosa en Facebook:
```json
{
  "platform": "facebook",
  "post_id": "123456789_987654321",
  "post_url": "https://facebook.com/posts/...",
  "response": {
    "id": "987654321"
  }
}
```

Ejemplo para publicación exitosa en Instagram:
```json
{
  "platform": "instagram",
  "creation_id": "17841453993603227",
  "post_id": "2983498234",
  "response": {
    "id": "2983498234"
  }
}
```

### Índices

```sql
CREATE INDEX idx_publications_post_id ON publications(post_id);
CREATE INDEX idx_publications_network ON publications(network);
CREATE INDEX idx_publications_status ON publications(status);
CREATE INDEX idx_publications_created_at ON publications(created_at DESC);
```

---

## Relaciones

### Post → Publications (1:N)

- Un post puede tener múltiples publicaciones (una por red social)
- Cuando se elimina un post, se eliminan todas sus publicaciones (CASCADE)

```sql
ALTER TABLE publications
ADD CONSTRAINT fk_publications_post
FOREIGN KEY (post_id)
REFERENCES posts(id)
ON DELETE CASCADE;
```

---

## Migraciones

### Crear Migración Inicial

```bash
alembic revision --autogenerate -m "create posts and publications tables"
```

### Aplicar Migraciones

```bash
alembic upgrade head
```

### Revertir Migraciones

```bash
alembic downgrade -1
```

---

## SQL de Creación (Referencia)

```sql
-- Crear extensión para UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tabla de posts
CREATE TABLE posts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  title VARCHAR(500) NOT NULL,
  content TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR(50) NOT NULL DEFAULT 'draft'
    CHECK (status IN ('draft', 'processing', 'published', 'failed'))
);

-- Tabla de publicaciones por red
CREATE TABLE publications (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  post_id UUID NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
  network VARCHAR(50) NOT NULL
    CHECK (network IN ('facebook', 'instagram', 'linkedin', 'tiktok', 'whatsapp')),
  adapted_content TEXT,
  status VARCHAR(50) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'processing', 'published', 'failed')),
  published_at TIMESTAMP,
  error_message TEXT,
  metadata JSONB DEFAULT '{}',  -- Nota: En el código se llama 'extra_data' (metadata es palabra reservada)
  created_at TIMESTAMP NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Índices
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
CREATE INDEX idx_publications_post_id ON publications(post_id);
CREATE INDEX idx_publications_network ON publications(network);
CREATE INDEX idx_publications_status ON publications(status);
CREATE INDEX idx_publications_created_at ON publications(created_at DESC);
```

---

## Consultas Útiles

### Ver posts con conteo de publicaciones

```sql
SELECT 
  p.id,
  p.title,
  p.status,
  COUNT(pub.id) as total_publications,
  COUNT(CASE WHEN pub.status = 'published' THEN 1 END) as published_count,
  COUNT(CASE WHEN pub.status = 'failed' THEN 1 END) as failed_count
FROM posts p
LEFT JOIN publications pub ON p.id = pub.post_id
GROUP BY p.id, p.title, p.status
ORDER BY p.created_at DESC;
```

### Ver publicaciones por red social

```sql
SELECT 
  network,
  COUNT(*) as total,
  COUNT(CASE WHEN status = 'published' THEN 1 END) as published,
  COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
  COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending
FROM publications
GROUP BY network;
```

### Ver publicaciones fallidas con errores

```sql
SELECT 
  p.title,
  pub.network,
  pub.error_message,
  pub.created_at
FROM publications pub
JOIN posts p ON pub.post_id = p.id
WHERE pub.status = 'failed'
ORDER BY pub.created_at DESC;
```

---

## Consideraciones de Rendimiento

1. **Índices**: Todos los campos frecuentemente consultados tienen índices
2. **JSONB**: Usar para metadata permite flexibilidad sin cambios de schema
3. **Cascade Delete**: Eliminar un post limpia automáticamente sus publicaciones
4. **Timestamps**: Permiten auditoría y análisis temporal
5. **ENUM vs VARCHAR**: Se usa ENUM en código pero VARCHAR en DB para flexibilidad

---

## Backups

### Backup de Base de Datos

```bash
docker exec social_media_db pg_dump -U postgres social_media_publisher > backup.sql
```

### Restore de Backup

```bash
docker exec -i social_media_db psql -U postgres social_media_publisher < backup.sql
```
