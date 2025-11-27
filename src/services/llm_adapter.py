import openai
import json
import logging
import re
import os
import sys
from typing import Dict, List

# Cargar variables de entorno desde .env
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAdapter:
    """Motor principal para generar publicaciones optimizadas por plataforma digital"""

    # Límites de caracteres por red social
    PLATFORM_LIMITS = {
        "facebook": 63206,
        "instagram": 2200,
        "linkedin": 3000,
        "tiktok": 4000,
        "whatsapp": 4000,
    }

    # Configuraciones de creatividad por red social
    CREATIVITY_CONFIG = {
        "facebook": 0.7,
        "instagram": 0.8,
        "linkedin": 0.5,
        "tiktok": 0.9,
        "whatsapp": 0.6,
    }

    def __init__(self, api_key: str):
        """Inicializa el transformador de contenido"""
        self.ai_client = openai.OpenAI(api_key=api_key)
        logger.info("LLMAdapter inicializado correctamente")

    def get_platform_instructions(self, platform: str) -> str:
        """Obtiene las instrucciones específicas para cada plataforma social"""
        platform_guides = {
            "facebook": """
Eres un especialista en marketing digital para Facebook. Transforma el contenido para maximizar engagement con estas directrices:
- Estilo: Conversacional y cercano, manteniendo credibilidad
- Extensión: Óptimo 500 caracteres para mejor alcance
- Emojis: Moderado uso (1-3 por publicación)
- Etiquetas: Máximo 5, relevantes y con alto engagement
- Objetivo: Impulsar interacción y comentarios
- Estructura: Texto fluido con saltos naturales de línea
""",
            "instagram": """
Eres un creador de contenido especializado en Instagram. Optimiza el material para máximo impacto visual con estas pautas:
- Estilo: Inspirador, visual y contemporáneo
- Extensión: Máximo 2200 caracteres
- Emojis: Uso abundante para enriquecer visualmente
- Etiquetas: Entre 5-10, combinando populares y específicas
- Objetivo: Contar historias visuales y generar engagement
- Estructura: Párrafos cortos, optimizados para móviles
- Visual: Incluir suggested_image_prompt con descripción detallada para contenido gráfico atractivo
- Elementos: Estética, paleta de colores, composición que capture atención
""",
            "linkedin": """
Eres un consultor en comunicación empresarial para LinkedIn. Desarrolla contenido que genere valor profesional con estas especificaciones:
- Estilo: Profesional, informativo y con insights valiosos
- Extensión: Máximo 3000 caracteres
- Emojis: Uso mínimo, únicamente para énfasis estratégico
- Etiquetas: Máximo 3-5, enfocadas en sector profesional
- Objetivo: Compartir conocimiento, networking, valor corporativo
- Estructura: Organización clara con viñetas cuando sea necesario
""",
            "tiktok": """
Eres un creador de contenido viral especializado en TikTok. Transforma el material para máximo potencial viral con estas características:
- Estilo: Dinámico, entretenido y siguiendo tendencias
- Extensión: Máximo 4000 caracteres
- Emojis: Uso expresivo y abundante
- Etiquetas: Entre 3-8, incluyendo tendencias y challenges actuales
- Objetivo: Entretenimiento, viralidad, seguir trends
- Estructura: Ritmo acelerado, llamadas a la acción directas
- Audiovisual: Incluir suggested_video_prompt con descripción detallada para contenido viral
- Elementos: Transiciones, efectos, música trending, ganchos visuales
""",
            "whatsapp": """
Eres un comunicador especializado en mensajería directa para WhatsApp. Adapta el contenido para comunicación personal efectiva con estas pautas:
- Estilo: Personal, directo y como conversación natural
- Extensión: Máximo 4000 caracteres, preferiblemente conciso
- Emojis: Uso natural como en conversaciones reales
- Etiquetas: Evitar o usar muy pocas (1-2 máximo)
- Objetivo: Comunicación directa, información práctica
- Estructura: Como mensaje personal, fácil de compartir
""",
        }
        return platform_guides.get(platform, platform_guides["facebook"])

    def build_transformation_request(self, heading: str, material: str, platform: str) -> str:
        """Construye la solicitud específica para la transformación del contenido"""
        # Crear estructura JSON base
        response_format = {
            "text": "contenido transformado aquí",
            "hashtags": ["#etiqueta1", "#etiqueta2"],
            "character_count": "número_de_caracteres",
            "tone": "descripción_del_estilo",
        }

        # Agregar campos específicos por plataforma
        if platform == "instagram":
            response_format["suggested_image_prompt"] = (
                "descripción para contenido visual sugerido"
            )
        elif platform == "tiktok":
            response_format["suggested_video_prompt"] = "descripción para contenido audiovisual sugerido"

        # Convertir a string JSON para mostrar en el prompt
        format_example = json.dumps(response_format, indent=4, ensure_ascii=False)

        return f"""
Transforma el siguiente material para {platform}:

ENCABEZADO: {heading}
MATERIAL: {material}

Genera ÚNICAMENTE un objeto JSON con esta estructura exacta:
{format_example}

CRÍTICO:
- El texto debe estar optimizado para {platform}
- Respeta el límite de {self.PLATFORM_LIMITS[platform]} caracteres
- El character_count debe ser preciso (número entero)
- NO incluyas explicaciones adicionales, solo el JSON
- Responde exclusivamente con el JSON válido
"""

    def transform_for_platform(self, heading: str, material: str, platform: str) -> Dict:
        """Transforma contenido para una plataforma social específica"""
        try:
            logger.info(f"Transformando contenido para {platform}")

            platform_instructions = self.get_platform_instructions(platform)
            transformation_request = self.build_transformation_request(heading, material, platform)
            creativity_level = self.CREATIVITY_CONFIG.get(platform, 0.7)

            ai_response = self.ai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": platform_instructions},
                    {"role": "user", "content": transformation_request},
                ],
                temperature=creativity_level,
                max_tokens=1000,
            )

            # Extraer y limpiar respuesta JSON
            raw_response = ai_response.choices[0].message.content.strip()

            # Limpiar markdown si existe
            if "```json" in raw_response:
                start_idx = raw_response.find("```json") + 7
                end_idx = raw_response.find("```", start_idx)
                raw_response = raw_response[
                    start_idx : end_idx if end_idx != -1 else len(raw_response)
                ].strip()
            elif "```" in raw_response:
                start_idx = raw_response.find("```") + 3
                end_idx = raw_response.find("```", start_idx)
                raw_response = raw_response[
                    start_idx : end_idx if end_idx != -1 else len(raw_response)
                ].strip()

            # Buscar JSON válido
            json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
            if json_match:
                raw_response = json_match.group(0)

            transformed_content = json.loads(raw_response)

            # Validar y corregir conteo de caracteres
            actual_length = len(transformed_content["text"])
            transformed_content["character_count"] = actual_length

            # Validar límite de caracteres
            if transformed_content["character_count"] > self.PLATFORM_LIMITS[platform]:
                logger.warning(
                    f"Contenido excede límite para {platform}: {transformed_content['character_count']}"
                )

            logger.info(f"Contenido transformado exitosamente para {platform}")
            return transformed_content

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response for {platform}: {e}")
            raise Exception(f"Error parsing AI response for {platform}")

        except Exception as e:
            logger.error(f"Error transformando contenido para {platform}: {e}")
            raise Exception(f"Error en transformación para {platform}: {str(e)}")

    def transform_for_multiple_platforms(
        self, heading: str, material: str, target_platforms: List[str]
    ) -> Dict:
        """Transforma contenido para múltiples plataformas sociales"""
        output_results = {}
        processing_errors = {}

        logger.info(f"Iniciando transformación para {len(target_platforms)} plataformas")

        for platform in target_platforms:
            if platform not in self.PLATFORM_LIMITS:
                logger.warning(f"Plataforma no soportada: {platform}")
                processing_errors[platform] = f"Plataforma '{platform}' no está soportada"
                continue

            try:
                output_results[platform] = self.transform_for_platform(heading, material, platform)
            except Exception as e:
                logger.error(f"Error transformando para {platform}: {e}")
                processing_errors[platform] = str(e)

        # Solo agregar errores si los hay, sin otros metadatos
        if processing_errors:
            logger.error(f"Errores en transformación: {processing_errors}")

        successful_transformations = len(
            [p for p in target_platforms if p in output_results and not p.startswith("_")]
        )
        logger.info(
            f"Transformación completada. Éxito: {successful_transformations}, Errores: {len(processing_errors)}"
        )
        return output_results


def validate_input_data(data: Dict) -> bool:
    """Valida que la entrada tenga la estructura correcta"""
    required_fields = ["encabezado", "material", "target_platforms"]

    for field in required_fields:
        if field not in data:
            logger.error(f"Campo requerido faltante: {field}")
            return False

    if not isinstance(data["target_platforms"], list):
        logger.error("target_platforms debe ser una lista")
        return False

    if len(data["target_platforms"]) == 0:
        logger.error("target_platforms no puede estar vacía")
        return False

    return True


def process_content(input_data: Dict) -> Dict:
    # Validar entrada
    if not validate_input_data(input_data):
        raise ValueError("Formato de entrada inválido")

    # Obtener clave API
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Se requiere OPENAI_API_KEY como variable de entorno")

    logger.info(f"Procesando material: '{input_data['encabezado'][:50]}...'")

    # Inicializar transformador
    adapter = LLMAdapter(api_key)

    # Procesar transformación
    results = adapter.transform_for_multiple_platforms(
        heading=input_data["encabezado"],
        material=input_data["material"],
        target_platforms=input_data["target_platforms"],
    )

    return results


def interactive_input():
    """Permite entrada interactiva de datos"""
    print("=" * 60)
    print("� MOTOR DE TRANSFORMACIÓN DIGITAL - ENTRADA INTERACTIVA")
    print("=" * 60)

    # Solicitar encabezado
    encabezado = input("\n📌 Ingresa el encabezado del material:\n> ").strip()

    # Solicitar material
    print("\n📄 Ingresa el material completo (presiona Enter dos veces para terminar):")
    material_lines = []
    print("> ", end="")
    while True:
        try:
            line = input()
            if line == "" and material_lines and material_lines[-1] == "":
                break
            material_lines.append(line)
            if line != "":
                print("> ", end="")
        except (EOFError, KeyboardInterrupt):
            break

    # Remover líneas vacías del final
    while material_lines and material_lines[-1] == "":
        material_lines.pop()

    material = "\n".join(material_lines).strip()

    # Solicitar plataformas sociales
    plataformas_disponibles = ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"]
    print("\n🌐 SELECCIÓN DE PLATAFORMAS DIGITALES")
    print("-" * 40)
    print("Plataformas disponibles:")
    for i, plataforma in enumerate(plataformas_disponibles, 1):
        print(f"  {i}. {plataforma.capitalize()}")

    print("\nOpciones de selección:")
    print("  • Ingresa números separados por comas (ej: 1,3,5)")
    print("  • Ingresa nombres separados por comas (ej: facebook,instagram)")
    print("  • Presiona 'a' o Enter para seleccionar TODAS")
    print("  • Presiona 'q' para salir")

    while True:
        seleccion = input("\n> ").strip().lower()

        if seleccion in ["q", "quit", "salir"]:
            print("👋 Operación cancelada")
            sys.exit(0)

        if seleccion in ["a", "all", "todas", ""]:
            target_platforms = plataformas_disponibles.copy()
            print(
                f"✅ Seleccionadas TODAS las plataformas: {', '.join([p.capitalize() for p in target_platforms])}"
            )
            break

        # Intentar parsear como números
        if "," in seleccion or seleccion.isdigit():
            try:
                numeros = [int(num.strip()) for num in seleccion.split(",")]
                target_platforms = []
                for num in numeros:
                    if 1 <= num <= len(plataformas_disponibles):
                        target_platforms.append(plataformas_disponibles[num - 1])
                    else:
                        print(
                            f"❌ Número {num} no válido (debe ser entre 1 y {len(plataformas_disponibles)})"
                        )
                        target_platforms = []
                        break

                if target_platforms:
                    target_platforms = list(set(target_platforms))  # Eliminar duplicados
                    print(
                        f"✅ Seleccionadas: {', '.join([p.capitalize() for p in target_platforms])}"
                    )
                    break
                else:
                    print("🔄 Intenta de nuevo...")
                    continue

            except ValueError:
                # Intentar parsear como nombres
                pass

        # Intentar parsear como nombres de plataformas
        nombres = [nombre.strip().lower() for nombre in seleccion.split(",")]
        target_platforms = []
        nombres_invalidos = []

        for nombre in nombres:
            if nombre in plataformas_disponibles:
                target_platforms.append(nombre)
            else:
                nombres_invalidos.append(nombre)

        if nombres_invalidos:
            print(f"❌ Plataformas no válidas: {', '.join(nombres_invalidos)}")
            print(f"   Plataformas válidas: {', '.join(plataformas_disponibles)}")
            continue

        if target_platforms:
            target_platforms = list(set(target_platforms))  # Eliminar duplicados
            print(
                f"✅ Seleccionadas: {', '.join([p.capitalize() for p in target_platforms])}"
            )
            break
        else:
            print("❌ No se seleccionaron plataformas válidas. Intenta de nuevo.")
            print("   Ejemplo: facebook,instagram o 1,2,3 o 'a' para todas")

    return {
        "encabezado": encabezado,
        "material": material,
        "target_platforms": target_platforms,
    }


def main():
    try:
        # Entrada interactiva de datos
        input_data = interactive_input()

        # Procesar contenido
        results = process_content(input_data)

        # Mostrar resultados
        print("\n" + "=" * 60)
        print("✅ TRANSFORMACIÓN COMPLETADA")
        print("=" * 60)
        print(json.dumps(results, indent=2, ensure_ascii=False))

        # Preguntar si desea guardar
        print("\n💾 ¿Deseas guardar la transformación en un archivo? (s/N)")
        guardar = input("> ").strip().lower()

        if guardar in ["s", "si", "sí", "yes", "y"]:
            from datetime import datetime

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transformacion_digital_{timestamp}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"✅ Transformación guardada en: {filename}")
        else:
            print("📋 Resultados mostrados únicamente en pantalla")

    except KeyboardInterrupt:
        print("\n\n👋 Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error en ejecución: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
