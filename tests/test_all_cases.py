import json
import os
import sys
from datetime import datetime

# Configurar rutas
project_root = os.path.dirname(os.path.dirname(__file__))
services_path = os.path.join(project_root, "src", "services")
sys.path.insert(0, services_path)

# Cargar variables de entorno
try:
    from dotenv import load_dotenv

    env_path = os.path.join(project_root, ".env")
    load_dotenv(env_path)
except ImportError:
    print("Warning: python-dotenv no instalado.")

# Importar desde la ruta correcta
sys.path.append(project_root)
from src.services.llm_adapter import process_content

CASOS_VALIDACION = {
    "empresarial": {
        "encabezado": "Nuestra organización supera los 15,000 usuarios registrados",
        "material": "Con inmensa satisfacción comunicamos que nuestra organización ha superado la significativa marca de 15,000 usuarios registrados activos. Este hito refleja no solo nuestro desarrollo continuo, sino también la credibilidad que nuestros miembros depositan en nuestras plataformas digitales. A lo largo de este período hemos trabajado constantemente para desarrollar herramientas vanguardistas que verdaderamente generen impacto. Valoramos a cada usuario que integra esta extraordinaria red y ratificamos nuestro propósito de continuar evolucionando constantemente para proporcionar la experiencia más satisfactoria.",
        "target_platforms": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"],
    },
    "lanzamiento": {
        "encabezado": "Debut de InnovatePro 3.0: Tu compañero digital avanzado",
        "material": "En este momento nos complace revelar InnovatePro 3.0, una pioneera plataforma digital que fusiona machine learning con experiencia de usuario excepcional. Las funcionalidades renovadas comprenden: procesamiento de lenguaje natural mejorado, algoritmos adaptativos individualizados, conectividad con más de 75 herramientas profesionales, y una arquitectura completamente reimaginada. InnovatePro 3.0 se adapta a tus patrones de trabajo y gustos para brindarte recomendaciones inteligentes que genuinamente optimizan tu eficiencia. Accesible inmediatamente en todas las tiendas digitales con un período de evaluación gratuito de 45 días.",
        "target_platforms": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"],
    },
    "actividad": {
        "encabezado": "Congreso DigitalNext 2025: La revolución digital comienza ahora",
        "material": "Te convocamos al evento más relevante del año en transformación digital: DigitalNext 2025. Participa junto a más de 3,500 especialistas, innovadores y directivos del sector los días 22-24 de abril en el Complejo Empresarial InnovaSpace. Durante tres jornadas intensivas analizaremos las tendencias emergentes en machine learning, criptomonedas, tecnología sostenible y el porvenir del trabajo remoto. Participarán ponentes globales de Amazon, Meta, SpaceX y empresas emergentes revolucionarias. Incluye talleres especializados, conexiones profesionales exclusivas y acceso a demostraciones de innovaciones disruptivas. Registro anticipado hasta el 15 de febrero con 50% de descuento.",
        "target_platforms": ["facebook", "instagram", "linkedin", "tiktok", "whatsapp"],
    },
}


def mostrar_resumen_caso(caso_nombre, results):
    """Muestra resumen detallado de un caso específico"""
    caso = CASOS_VALIDACION[caso_nombre]

    print(f"\n📋 CASO: {caso_nombre.upper()}")
    print("=" * 60)
    print(f"📝 Encabezado: {caso['encabezado'][:50]}...")
    print("=" * 60)

    # Resumen por plataforma digital
    print(f"\n📊 RESUMEN POR PLATAFORMA DIGITAL:")
    for platform, content in results.items():
        if not platform.startswith("_"):
            char_count = content.get("character_count", "N/A")
            hashtags_count = len(content.get("hashtags", []))
            tone = content.get("tone", "N/A")

            print(f"\n🔹 {platform.upper()}:")
            print(
                f"   📏 {char_count} caracteres | 🏷️  {hashtags_count} etiquetas | 🎭 {tone}"
            )

            # Campos específicos por plataforma
            if platform == "instagram" and "suggested_image_prompt" in content:
                image_prompt = (
                    content["suggested_image_prompt"][:70] + "..."
                    if len(content["suggested_image_prompt"]) > 70
                    else content["suggested_image_prompt"]
                )
                print(f"   📸 Visual: {image_prompt}")

            elif platform == "tiktok" and "suggested_video_prompt" in content:
                video_prompt = (
                    content["suggested_video_prompt"][:70] + "..."
                    if len(content["suggested_video_prompt"]) > 70
                    else content["suggested_video_prompt"]
                )
                print(f"   🎬 Audiovisual: {video_prompt}")

            # Mostrar algunas etiquetas
            hashtags = content.get("hashtags", [])[:4]
            if hashtags:
                print(f"   🏷️  Etiquetas: {', '.join(hashtags)}")


def validar_campos_especificos(results):
    print(f"\n🔍 VERIFICACIÓN DE CAMPOS ESPECÍFICOS:")

    verificaciones = []

    for platform, content in results.items():
        if not platform.startswith("_"):
            if platform == "instagram":
                if "suggested_image_prompt" in content:
                    verificaciones.append(
                        f"✅ Instagram: suggested_image_prompt incluido"
                    )
                else:
                    verificaciones.append(f"❌ Instagram: falta suggested_image_prompt")

            elif platform == "tiktok":
                if "suggested_video_prompt" in content:
                    verificaciones.append(f"✅ TikTok: suggested_video_prompt incluido")
                else:
                    verificaciones.append(f"❌ TikTok: falta suggested_video_prompt")

            elif platform in ["facebook", "linkedin", "whatsapp"]:
                # Estas plataformas NO deben tener campos de medios
                has_media = (
                    "suggested_image_prompt" in content
                    or "suggested_video_prompt" in content
                )
                if not has_media:
                    verificaciones.append(
                        f"✅ {platform.capitalize()}: sin campos multimedia (correcto)"
                    )
                else:
                    verificaciones.append(
                        f"❌ {platform.capitalize()}: tiene campos multimedia no permitidos"
                    )

    for verificacion in verificaciones:
        print(f"  {verificacion}")


def analizar_contenido_por_tipo(caso_nombre, results):
    """Análisis específico según el tipo de caso"""

    elementos_por_caso = {
        "empresarial": [
            "hito",
            "usuarios",
            "desarrollo", 
            "red",
            "propósito",
        ],
        "lanzamiento": [
            "innovatepro",
            "ml",
            "machine learning",
            "tiendas digitales",
            "evaluación",
            "45 días",
        ],
        "actividad": [
            "digitalnext",
            "congreso",
            "abril",
            "22-24",
            "registro",
            "anticipado",
            "descuento",
        ],
    }

    elementos = elementos_por_caso.get(caso_nombre, [])

    if elementos:
        print(f"\n🔍 ANÁLISIS DE MATERIAL:")
        print("✅ Elementos clave detectados por plataforma:")

        for platform, content in results.items():
            if not platform.startswith("_"):
                text = content.get("text", "").lower()
                elementos_encontrados = [
                    elemento for elemento in elementos if elemento in text
                ]

                if elementos_encontrados:
                    print(
                        f"   {platform.capitalize()}: {', '.join(elementos_encontrados)}"
                    )


def ejecutar_caso(caso_nombre):

    if caso_nombre not in CASOS_VALIDACION:
        print(f"❌ Caso '{caso_nombre}' no existe")
        return None

    caso = CASOS_VALIDACION[caso_nombre]

    print(f"\n🚀 EJECUTANDO VALIDACIÓN: {caso_nombre.upper()}")
    print("-" * 50)

    try:
        # Procesar directamente con los datos del caso
        results = process_content(caso)

        if results:
            print("✅ Validación completada exitosamente")

            # Mostrar análisis completo
            mostrar_resumen_caso(caso_nombre, results)
            validar_campos_especificos(results)
            analizar_contenido_por_tipo(caso_nombre, results)

            # Guardar resultados
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"validacion_{caso_nombre}_{timestamp}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Resultados guardados en: {filename}")
            return results

        else:
            print(f"❌ Error procesando validación {caso_nombre}")
            return None

    except Exception as e:
        print(f"❌ Error ejecutando {caso_nombre}: {e}")
        return None


def ejecutar_todos_los_casos():
    """Ejecuta todas las validaciones disponibles"""

    print("🎯 EJECUTANDO TODAS LAS VALIDACIONES")
    print("=" * 60)

    resultados_globales = {}
    validaciones_exitosas = 0
    validaciones_fallidas = 0

    for caso_nombre in CASOS_VALIDACION.keys():
        resultado = ejecutar_caso(caso_nombre)

        if resultado:
            resultados_globales[caso_nombre] = resultado
            validaciones_exitosas += 1
        else:
            validaciones_fallidas += 1

        print("\n" + "=" * 60)

    # Resumen final
    print(f"\n📈 RESUMEN FINAL DE VALIDACIONES:")
    print(f"  ✅ Validaciones exitosas: {validaciones_exitosas}")
    print(f"  ❌ Validaciones fallidas: {validaciones_fallidas}")
    print(f"  📊 Total ejecutadas: {validaciones_exitosas + validaciones_fallidas}")

    if resultados_globales:
        # Guardar resultados consolidados
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"validacion_completa_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(resultados_globales, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Resultados consolidados guardados en: {filename}")

    return resultados_globales


def mostrar_casos_disponibles():
    """Muestra la lista de casos disponibles"""
    print("\n📋 CASOS DE VALIDACIÓN DISPONIBLES:")
    print("-" * 40)

    for i, (caso_id, caso) in enumerate(CASOS_VALIDACION.items(), 1):
        print(f"{i}. {caso_id.upper()}")
        print(f"   📝 {caso['encabezado'][:50]}...")
        print(f"   🎯 Plataformas: {len(caso['target_platforms'])} canales")
        print()


def modo_interactivo():
    """Modo interactivo para seleccionar validaciones"""
    print("🎮 MODO INTERACTIVO - SELECCIÓN DE VALIDACIONES")
    print("=" * 50)

    mostrar_casos_disponibles()

    print("Opciones:")
    print("  • Ingresa el ID del caso (ej: empresarial)")
    print("  • Ingresa 'all' o 'todos' para ejecutar todos")
    print("  • Ingresa 'q' para salir")

    while True:
        seleccion = input("\n> ").strip().lower()

        if seleccion in ["q", "quit", "salir"]:
            print("👋 Saliendo...")
            return

        if seleccion in ["all", "todos", "todo"]:
            ejecutar_todos_los_casos()
            return

        if seleccion in CASOS_VALIDACION:
            ejecutar_caso(seleccion)
            return

        print(f"❌ Opción '{seleccion}' no válida. Intenta de nuevo.")
        print(f"   Casos disponibles: {', '.join(CASOS_VALIDACION.keys())}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Sistema de Validación Unificado - Transformación Digital"
    )
    parser.add_argument(
        "--caso",
        "-c",
        choices=list(CASOS_VALIDACION.keys()),
        help="Ejecutar validación específica",
    )
    parser.add_argument(
        "--all", "-a", action="store_true", help="Ejecutar todas las validaciones"
    )
    parser.add_argument(
        "--list", "-l", action="store_true", help="Mostrar casos disponibles"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Modo interactivo"
    )

    args = parser.parse_args()

    # Verificar API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY no configurada")
        print("   Configura tu token API en el archivo .env")
        sys.exit(1)

    print("🤖 SISTEMA DE VALIDACIÓN - TRANSFORMACIÓN DIGITAL")
    print("   DigitalNext 2025 - Versión Avanzada")
    print("=" * 60)

    if args.list:
        mostrar_casos_disponibles()
    elif args.all:
        ejecutar_todos_los_casos()
    elif args.caso:
        ejecutar_caso(args.caso)
    elif args.interactive:
        modo_interactivo()
    else:
        # Por defecto: modo interactivo
        modo_interactivo()
