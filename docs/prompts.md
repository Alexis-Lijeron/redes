# Documentación de Instrucciones

Estrategias de instrucciones para transformación de material por plataforma digital usando OpenAI GPT-3.5 Turbo.

## Arquitectura

**Instrucciones duales**:
1. **Instrucciones de Sistema**: Contexto y restricciones por plataforma digital
2. **Solicitud de Usuario**: Material original y estructura de respuesta JSON

## Diseño de Instrucciones por Plataforma Digital

### Facebook - Instrucciones de Interacción
**Estrategia de Diseño**: 
- Orientado a generar conversación e interacción
- Equilibrio entre conversacional y profesional para audiencia variada
- Uso moderado de emojis para mantener credibilidad

**Instrucciones de Sistema Específicas**:
```
Eres un especialista en marketing digital para Facebook. Transforma el contenido para maximizar engagement con estas directrices:
- Estilo: Conversacional y cercano, manteniendo credibilidad
- Extensión: Óptimo 500 caracteres para mejor alcance
- Emojis: Moderado uso (1-3 por publicación)
- Etiquetas: Máximo 5, relevantes y con alto engagement
- Objetivo: Impulsar interacción y comentarios
- Estructura: Texto fluido con saltos naturales de línea
```

### Instagram - Instrucciones Visuales
**Estrategia de Diseño**:
- Orientado a narrativa visual e inspiración
- Énfasis en descripción de contenido visual sugerido
- Etiquetas abundantes para descubrimiento

**Instrucciones de Sistema Específicas**:
```
Eres un creador de contenido especializado en Instagram. Optimiza el material para máximo impacto visual con estas pautas:
- Estilo: Inspirador, visual y contemporáneo
- Extensión: Máximo 2200 caracteres
- Emojis: Uso abundante para enriquecer visualmente
- Etiquetas: Entre 5-10, combinando populares y específicas
- Objetivo: Contar historias visuales y generar engagement
- Estructura: Párrafos cortos, optimizados para móviles
- Visual: Incluir suggested_image_prompt con descripción detallada para contenido gráfico atractivo
- Elementos: Estética, paleta de colores, composición que capture atención
```

### LinkedIn - Instrucciones Profesionales
**Estrategia de Diseño**:
- Enfocado en valor profesional y networking
- Estilo formal pero accesible
- Etiquetas específicas de sector

**Instrucciones de Sistema Específicas**:
```
Eres un consultor en comunicación empresarial para LinkedIn. Desarrolla contenido que genere valor profesional con estas especificaciones:
- Estilo: Profesional, informativo y con insights valiosos
- Extensión: Máximo 3000 caracteres
- Emojis: Uso mínimo, únicamente para énfasis estratégico
- Etiquetas: Máximo 3-5, enfocadas en sector profesional
- Objetivo: Compartir conocimiento, networking, valor corporativo
- Estructura: Organización clara con viñetas cuando sea necesario
```

### TikTok - Instrucciones Virales
**Estrategia de Diseño**:
- Máxima creatividad para contenido viral
- Énfasis en tendencias y desafíos
- Descripción detallada de contenido audiovisual sugerido

**Instrucciones de Sistema Específicas**:
```
Eres un creador de contenido viral especializado en TikTok. Transforma el material para máximo potencial viral con estas características:
- Estilo: Dinámico, entretenido y siguiendo tendencias
- Extensión: Máximo 4000 caracteres
- Emojis: Uso expresivo y abundante
- Etiquetas: Entre 3-8, incluyendo tendencias y challenges actuales
- Objetivo: Entretenimiento, viralidad, seguir trends
- Estructura: Ritmo acelerado, llamadas a la acción directas
- Audiovisual: Incluir suggested_video_prompt con descripción detallada para contenido viral
- Elementos: Transiciones, efectos, música trending, ganchos visuales
```

### WhatsApp - Instrucciones Conversacionales
**Estrategia de Diseño**:
- Estilo personal y directo como mensaje privado
- Evitar etiquetas para mantener naturalidad
- Estructura concisa y fácil de compartir

**Instrucciones de Sistema Específicas**:
```
Eres un comunicador especializado en mensajería directa para WhatsApp. Adapta el contenido para comunicación personal efectiva con estas pautas:
- Estilo: Personal, directo y como conversación natural
- Extensión: Máximo 4000 caracteres, preferiblemente conciso
- Emojis: Uso natural como en conversaciones reales
- Etiquetas: Evitar o usar muy pocas (1-2 máximo)
- Objetivo: Comunicación directa, información práctica
- Estructura: Como mensaje personal, fácil de compartir
```

## Configuración por Plataforma Digital

### Facebook
- **Estilo**: Conversacional y cercano, pero profesional
- **Límite**: 63,206 caracteres
- **Emojis**: Moderado (1-3 por publicación)
- **Etiquetas**: Máximo 5
- **Creatividad**: 0.7
- **Objetivo**: Generar interacción y comentarios

### Instagram
- **Estilo**: Visual, inspirador y moderno  
- **Límite**: 2,200 caracteres
- **Emojis**: Abundante para impacto visual
- **Etiquetas**: 5-10, populares y específicas
- **Campo especial**: `suggested_image_prompt`
- **Creatividad**: 0.8
- **Objetivo**: Narrativa visual y engagement

### LinkedIn
- **Estilo**: Profesional, informativo y valioso
- **Límite**: 3,000 caracteres
- **Emojis**: Mínimo, solo para énfasis estratégico
- **Etiquetas**: 3-5, enfocadas en sector
- **Creatividad**: 0.5
- **Objetivo**: Insights profesionales, networking, valor corporativo

### TikTok
- **Estilo**: Dinámico, entretenido y trending
- **Límite**: 4,000 caracteres
- **Emojis**: Expresivo y abundante
- **Etiquetas**: 3-8, incluir tendencias
- **Campo especial**: `suggested_video_prompt`
- **Creatividad**: 0.9
- **Objetivo**: Entretenimiento, viralidad, seguir trends

### WhatsApp
- **Estilo**: Personal, directo y conversacional
- **Límite**: 4,000 caracteres (preferible conciso)
- **Emojis**: Natural como en conversación
- **Etiquetas**: Evitar o muy pocas (1-2)
- **Creatividad**: 0.6
- **Objetivo**: Comunicación directa, información práctica

## Estructura de Respuesta JSON

Formato base para todas las plataformas:
```json
{
  "text": "Contenido transformado",
  "hashtags": ["#etiqueta1", "#etiqueta2"],
  "character_count": 123,
  "tone": "descripción_del_estilo"
}
```

**Campos adicionales**:
- Instagram: `suggested_image_prompt`
- TikTok: `suggested_video_prompt`

## Metodología de Diseño de Instrucciones

### Proceso de Desarrollo
1. **Análisis de Plataforma**: Estudio de características únicas de cada canal digital
2. **Definición de Especialista**: Creación de "especialista" específico por plataforma
3. **Establecimiento de Parámetros**: Límites técnicos y de estructura
4. **Optimización de Creatividad**: Ajuste de nivel según necesidades
5. **Validación Iterativa**: Pruebas y refinamiento de instrucciones

### Criterios de Diseño por Plataforma Digital

**Facebook**: 
- Diseñado para audiencia variada (personal + profesional)
- Instrucciones que equilibran conversación con credibilidad
- Objetivo en generar interacción auténtica

**Instagram**:
- Optimizado para contenido visual e inspiracional
- Instrucciones que generan descripciones ricas para visuales
- Énfasis en narrativa y estética

**LinkedIn**:
- Orientado a valor profesional y networking
- Instrucciones que mantienen formalidad pero accesibilidad
- Objetivo en insights y conocimiento de sector

**TikTok**:
- Diseñado para máxima creatividad y viralidad
- Instrucciones que incorporan tendencias y cultura de la plataforma
- Énfasis en entretenimiento y ganchos visuales

**WhatsApp**:
- Optimizado para comunicación personal directa
- Instrucciones que emulan conversaciones naturales
- Objetivo en practicidad y facilidad de compartir

### Consideraciones Especiales

**Campos Multimedia**:
- **Instagram**: `suggested_image_prompt` incluye composición, colores, elementos visuales
- **TikTok**: `suggested_video_prompt` considera transiciones, efectos, música trending

**Adaptación de Creatividad**:
- **LinkedIn (0.5)**: Respuestas consistentes y profesionales
- **Facebook (0.7)**: Balance entre creatividad y coherencia
- **Instagram (0.8)**: Alta creatividad manteniendo coherencia visual
- **TikTok (0.9)**: Máxima creatividad para contenido viral
- **WhatsApp (0.6)**: Personal pero predecible

## Niveles de Creatividad por Plataforma

| Plataforma | Creatividad | Razón |
|------------|-------------|-------|
| LinkedIn | 0.5 | Profesional, consistente |
| Facebook | 0.7 | Balance creatividad/coherencia |
| Instagram | 0.8 | Creatividad visual |
| TikTok | 0.9 | Máxima creatividad, viral |
| WhatsApp | 0.6 | Personal pero coherente |

## Estrategias de Instrucciones

### Instrucciones de Sistema
Cada plataforma digital tiene instrucciones especializadas que definen:
- Personalidad del especialista
- Características específicas de estructura
- Restricciones de contenido
- Objetivo principal de la plataforma

### Solicitudes de Usuario
Estructura consistente:
1. Material original (encabezado + material)
2. Especificación de plataforma digital
3. Estructura JSON esperada
4. Instrucciones de verificación

## Verificaciones Implementadas

### Límites de Caracteres
- Verificación automática post-generación
- Corrección del `character_count` si es necesario

### Estructura JSON
- Limpieza de markdown (`\`\`\`json`)
- Extracción mediante regex
- Validación de estructura

### Campos Específicos
- Instagram: Verificación de `suggested_image_prompt`
- TikTok: Verificación de `suggested_video_prompt`
- Otras plataformas: Ausencia de campos multimedia

## Mejores Prácticas

### Instrucciones
- Directrices claras y específicas
- Ejemplos de estructura JSON
- Parámetros explícitos
- Contexto de plataforma digital

### Verificación
- Siempre verificar character_count
- Limpiar respuestas de markdown
- Validar estructura JSON
- Confirmar campos específicos por plataforma

### Manejo de Errores
- Registro detallado de errores
- Lógica de retry para fallos de parsing
- Fallback a configuración por defecto
- Manejo elegante de límites de API

## Templates de Instrucciones

### Template de Instrucciones de Sistema
```
Eres un especialista en contenido para {PLATAFORMA_DIGITAL}. Tu tarea es transformar material con estas características:
- Estilo: {ESTILO_ESPECÍFICO}
- Extensión: Máximo {LÍMITE} caracteres
- Emojis: {ESTRATEGIA_EMOJIS}
- Etiquetas: {CANTIDAD_ETIQUETAS}
- Objetivo: {OBJETIVO_PRINCIPAL}
- Estructura: {CONSIDERACIONES_ESTRUCTURA}
```

### Template de Solicitud de Usuario
```
Transforma el siguiente material para {plataforma_digital}:

ENCABEZADO: {encabezado}
MATERIAL: {material}

Genera ÚNICAMENTE un objeto JSON con esta estructura exacta:
{estructura_json}

CRÍTICO:
- El texto debe estar optimizado para {plataforma_digital}
- Respeta el límite de {límite} caracteres
- El character_count debe ser preciso
- NO incluyas explicaciones adicionales
```