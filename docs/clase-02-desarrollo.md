# Sistema de Adaptación LLM - Documentación de Desarrollo

Sistema interactivo de adaptación automática de contenido para múltiples redes sociales usando OpenAI GPT-3.5 Turbo.

## Objetivos

### Principal
Adaptar contenido automáticamente a Facebook, Instagram, LinkedIn, TikTok y WhatsApp, manteniendo la esencia pero optimizando por plataforma.

### Específicos
- Integración con OpenAI GPT-3.5 Turbo
- Prompts especializados por red social
- Campos específicos (imagen para Instagram, video para TikTok)
- Sistema de pruebas unificado
- Interfaz interactiva simple

## Metodología de Desarrollo

### 1. Análisis de Requerimientos

## Especificaciones

### Entrada
```json
{
  "titulo": "Título del contenido",
  "contenido": "Contenido completo original", 
  "target_networks": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
}
```

### Salida
```json
{
  "facebook": {
    "text": "Texto adaptado",
    "hashtags": ["#hash1", "#hash2"],
    "character_count": 245,
    "tone": "casual"
  },
  "instagram": {
    "text": "Texto visual",
    "hashtags": ["#photo", "#insta"],
    "character_count": 180,
    "tone": "inspirational",
    "suggested_image_prompt": "Descripción para imagen"
  },
  "tiktok": {
    "text": "Texto viral",
    "hashtags": ["#viral", "#trend"],
    "character_count": 120,
    "tone": "energetic",
    "suggested_video_prompt": "Descripción para video"
  }
}
```

### 2. Arquitectura del Sistema

## Arquitectura

### Componentes

1. **LLMAdapter** (`src/services/llm_adapter.py`)
   - Sistema principal interactivo
   - Prompts especializados por red social
   - Configuración de límites y temperatura
   - Manejo de campos específicos (imagen/video)
   - Sistema de validaciones robusto con limpieza JSON automática

2. **Sistema de Pruebas** (`tests/test_all_cases.py`)
   - Casos unificados: corporativo, producto, evento
   - Validación automática de campos específicos
   - Análisis de contenido por tipo
   - Guardado automático con timestamp
   - Modo interactivo para selección de casos
   - `tests/test_producto.py` - Caso de lanzamiento de producto
## Sistema de Pruebas Unificado

### Casos Predefinidos

El sistema incluye 3 casos de prueba en `test_all_cases.py`:

```python
CASOS_PRUEBA = {
    "corporativo": {
        "titulo": "Nuestra empresa alcanza los 10,000 clientes",
        "contenido": "Con gran orgullo anunciamos...",
        "target_networks": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
    },
    "producto": {
        "titulo": "Lanzamiento de SmartApp 2.0",
        "contenido": "Hoy estamos emocionados de presentar...",
        "target_networks": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
    },
    "evento": {
        "titulo": "Conferencia TechFuture 2025",
        "contenido": "Te invitamos a la conferencia...",
        "target_networks": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
    }
}
```

### Funcionalidades del Sistema de Pruebas

1. **Validación Automática**
   - Verificación de campos específicos por plataforma
   - Instagram: presencia de `suggested_image_prompt`
   - TikTok: presencia de `suggested_video_prompt`
   - Otras redes: ausencia de campos de medios

2. **Análisis de Contenido**
   - Detección de elementos clave por tipo de caso
   - Corporativo: milestone, clientes, crecimiento, comunidad
   - Producto: features, descarga, IA, beneficios
   - Evento: fechas, registro, speakers, descuentos

3. **Resumen Detallado**
   - Estadísticas por red social (caracteres, hashtags, tono)
   - Vista previa de campos específicos (imagen/video)
   - Guardado automático con timestamp

2. **Sistema de Pruebas** (`tests/test_all_cases.py`)
   - Casos unificados: corporativo, producto, evento
   - Validación de campos específicos
   - Análisis automático de contenido

## Configuración por Red Social

| Red | Temperatura | Tono | Campo Especial |
|-----|-------------|------|----------------|
| Facebook | 0.7 | Casual-profesional | - |
| Instagram | 0.8 | Visual-inspiracional | `suggested_image_prompt` |
| LinkedIn | 0.5 | Profesional | - |
| TikTok | 0.9 | Dinámico-viral | `suggested_video_prompt` |
| WhatsApp | 0.6 | Personal-directo | - |

## Límites de Caracteres

```python
CHARACTER_LIMITS = {
    "facebook": 63206,
    "instagram": 2200,
    "linkedin": 3000, 
    "tiktok": 4000,
    "whatsapp": 4000
}
```

## Uso del Sistema

### Interactivo
```bash
python src/services/llm_adapter.py
```

### Sistema de Pruebas
```bash
# Ver casos
python tests/test_all_cases.py --list

# Ejecutar caso específico  
python tests/test_all_cases.py --caso corporativo

# Todos los casos
python tests/test_all_cases.py --all

# Modo interactivo
python tests/test_all_cases.py --interactive
```

## Validaciones Implementadas

### Campos Específicos por Plataforma
- **Instagram**: Requiere `suggested_image_prompt`
- **TikTok**: Requiere `suggested_video_prompt`  
- **Facebook/LinkedIn/WhatsApp**: Sin campos de medios

### Análisis Automático
- **Corporativo**: milestone, clientes, crecimiento, comunidad, compromiso
- **Producto**: smartapp, ia, app store, google play, gratis, 30 días
- **Evento**: techfuture, conferencia, marzo, registro, early bird, descuento

### Guardado de Resultados
- Timestamp automático en nombres de archivos
- Formato JSON estructurado
- Resultados individuales y consolidados

## Casos de Prueba Detallados

### Caso Corporativo
```json
{
  "titulo": "Nuestra empresa alcanza los 10,000 clientes",
  "contenido": "Con gran orgullo anunciamos...",
  "target_networks": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
}
```

#### Caso 2: Lanzamiento de Producto
**Escenario**: Presentación de nueva aplicación
```json
{
  "titulo": "Lanzamiento de SmartApp 2.0",
  "contenido": "Hoy estamos emocionados de presentar...",
  "target_networks": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
}
```

#### Caso 3: Anuncio de Evento
**Escenario**: Invitación a conferencia
```json
{
  "titulo": "Conferencia TechFuture 2025",
  "contenido": "Te invitamos a la conferencia más importante...",
  "target_networks": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
}
```

## Challenges Encontrados y Soluciones

### 1. Inconsistencia en Respuestas del LLM

**Problema**: El LLM ocasionalmente devolvía formatos incorrectos o excedía límites de caracteres.

**Solución Implementada**:
```python
def adapt_content(self, title: str, content: str, network: str) -> Dict:
    try:
        # Prompt con estructura JSON dinámica según red social
        json_structure = {
            "text": "texto adaptado aquí",
            "hashtags": ["#hashtag1", "#hashtag2"],
            "character_count": "número_de_caracteres",
            "tone": "descripción_del_tono"
        }
        
        # Campo específico para Instagram
        if network == "instagram":
            json_structure["suggested_image_prompt"] = "descripción para imagen"
        
        # Limpieza automática de respuesta
        response_text = response.choices[0].message.content.strip()
        
        # Limpieza robusta de markdown y extracción de JSON
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            response_text = json_match.group(0)
        
        # Validación y corrección automática de caracteres
        adapted_content = json.loads(response_text)
        adapted_content["character_count"] = len(adapted_content["text"])
        
    except json.JSONDecodeError as e:
        raise Exception(f"Error parsing LLM response for {network}")
```

### 2. Diferenciación Insuficiente entre Redes Sociales

**Problema**: Las adaptaciones iniciales eran muy similares entre redes sociales.

**Solución Implementada**:
- Prompts system específicos y detallados por plataforma
- Configuraciones de temperatura diferenciadas
- Instrucciones explícitas sobre tono y formato
- Validaciones específicas por red social

### 3. Manejo de Errores de API

**Problema**: Rate limits y errores de conectividad con OpenAI API.

**Solución Implementada**:
```python
def adapt_to_multiple_networks(self, title: str, content: str, target_networks: List[str]) -> Dict:
    results = {}
    errors = {}
    
    for network in target_networks:
        if network not in self.CHARACTER_LIMITS:
            errors[network] = f"Red social '{network}' no está soportada"
            continue
            
        try:
            results[network] = self.adapt_content(title, content, network)
        except Exception as e:
            logger.error(f"Error adaptando para {network}: {e}")
            errors[network] = str(e)
    
    # Log de errores sin contaminar la respuesta
    if errors:
        logger.error(f"Errores en adaptación: {errors}")
    
    # Retorno limpio sin metadatos adicionales
    return results
```

### Ejemplos de Salida por Red Social

#### Facebook (Tono: Casual-profesional)
```json
{
  "text": "🎉 ¡Increíbles noticias! Acabamos de alcanzar los 10,000 clientes activos. Gracias a cada uno de ustedes por confiar en nosotros. ¡Seguimos creciendo juntos! 💪",
  "hashtags": ["#Milestone", "#Gratitud", "#Crecimiento"],
  "character_count": 178,
  "tone": "celebratory and grateful"
}
```

#### LinkedIn (Tono: Profesional)
```json
{
  "text": "Orgullosos de anunciar que hemos alcanzado los 10,000 clientes activos. Este logro refleja nuestro compromiso con la excelencia y la confianza depositada por nuestros usuarios. Continuamos enfocados en entregar soluciones de valor.",
  "hashtags": ["#BusinessMilestone", "#Growth", "#Excellence"],
  "character_count": 267,
  "tone": "professional and achievement-focused"
}
```

#### TikTok (Tono: Dinámico-viral)
```json
{
  "text": "🚀 OMG! ¡10K clientes! 🎊 De 0 a 10,000 - ¡qué viaje increíble! 💫 Cada cliente cuenta su historia única con nosotros. ¿Cuál será la tuya? 👀✨ #ClientesIncreíbles",
  "hashtags": ["#10K", "#Success", "#GrowthStory", "#Viral"],
  "character_count": 189,
  "tone": "energetic and engaging"
}
```
