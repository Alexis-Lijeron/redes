# Social Media Publisher - Frontend

Frontend de React + TypeScript + Vite para el sistema de publicación en redes sociales.

## 🚀 Características

- ✅ **Crear Publicaciones**: Interfaz para crear posts con título, contenido e imagen
- 👁️ **Preview de Adaptaciones**: Vista previa del contenido adaptado por IA para cada red
- 📊 **Dashboard**: Monitoreo de publicaciones con estados y filtros
- 🎨 **UI Moderna**: Diseño con Tailwind CSS
- 📱 **Responsive**: Adaptado para desktop y móvil

## 📦 Instalación

```bash
npm install
```

## 🏃‍♂️ Ejecutar en Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

## 🔧 Configuración

El archivo `.env` contiene la URL del backend:

```
VITE_API_URL=http://localhost:8000
```

## 📄 Páginas

### 1. Crear Publicación (`/`)
- Input de título
- Textarea de contenido (max 5000 chars)
- Checkboxes para redes sociales
- Campo de URL de imagen
- Botones: "Generar Preview" y "Publicar Directamente"

### 2. Preview de Adaptaciones (`/preview/:postId`)
- Cards con contenido adaptado por red
- Character count
- Hashtags generados
- Tono de la publicación
- Sugerencia de imagen
- Botones: "Volver a Editar" y "Confirmar y Publicar"

### 3. Dashboard (`/dashboard`)
- Tabla de publicaciones
- Filtros por estado (draft, processing, published, failed)
- Modal con detalles de cada publicación
- Estado por red social
- Fechas de publicación

## 🛠️ Stack Tecnológico

- **React 18**: Framework UI
- **TypeScript**: Tipado estático
- **Vite**: Build tool
- **React Router**: Navegación
- **Axios**: Cliente HTTP
- **Tailwind CSS**: Estilos

## 📡 API Integration

El frontend consume el backend en `http://localhost:8000`:

- `POST /api/posts` - Crear post
- `GET /api/posts` - Listar posts
- `POST /api/posts/:id/adapt` - Adaptar contenido
- `POST /api/posts/:id/publish` - Publicar
- `GET /api/posts/:id/status` - Ver estado

## 🏗️ Build para Producción

```bash
npm run build
```

Los archivos compilados estarán en `dist/`
