"""
Script para crear datos de ejemplo (seeds)
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from src.database import SessionLocal, engine, Base
from src.database.models import Post, Publication, PostStatus, SocialNetwork, PublicationStatus
from datetime import datetime


def create_sample_posts():
    """Crear posts de ejemplo"""
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Post 1: Lanzamiento de producto
        post1 = Post(
            title="Lanzamiento de Nuevo Producto Tech",
            content="""
Estamos emocionados de anunciar el lanzamiento de nuestro nuevo producto revolucionario.
Después de meses de desarrollo, finalmente está listo para el mercado.

Características principales:
- Tecnología de última generación
- Interface intuitiva y fácil de usar
- Rendimiento optimizado
- Soporte 24/7

¡Únete a la revolución tecnológica!
            """.strip(),
            status=PostStatus.DRAFT
        )
        db.add(post1)
        
        # Post 2: Evento de empresa
        post2 = Post(
            title="Invitación a Conferencia de Tecnología 2025",
            content="""
Te invitamos a nuestro evento anual de tecnología e innovación.

📅 Fecha: 15 de Diciembre, 2025
📍 Lugar: Centro de Convenciones
⏰ Hora: 9:00 AM - 6:00 PM

Agenda:
- Keynote sobre IA y Machine Learning
- Talleres prácticos
- Networking con profesionales
- Exhibición de productos

Registro gratuito en nuestro sitio web.
            """.strip(),
            status=PostStatus.DRAFT
        )
        db.add(post2)
        
        # Post 3: Actualización de servicio
        post3 = Post(
            title="Mejoras en Nuestro Servicio Premium",
            content="""
Grandes noticias para nuestros usuarios Premium!

Hemos actualizado nuestro servicio con nuevas funcionalidades:

✅ Mayor capacidad de almacenamiento
✅ Velocidad mejorada en un 50%
✅ Nuevas integraciones
✅ Dashboard renovado
✅ Soporte prioritario

Actualiza ahora y disfruta de todas las mejoras sin costo adicional.
            """.strip(),
            status=PostStatus.DRAFT
        )
        db.add(post3)
        
        # Post 4: Testimonio de cliente
        post4 = Post(
            title="Historia de Éxito de Nuestro Cliente",
            content="""
Hoy queremos compartir una historia inspiradora.

Nuestro cliente ABC Corp logró aumentar su productividad en un 200% usando nuestra plataforma.

"La herramienta ha transformado completamente nuestra forma de trabajar. 
Lo que antes nos tomaba horas, ahora lo hacemos en minutos." 
- CEO de ABC Corp

¿Quieres resultados similares? Contáctanos.
            """.strip(),
            status=PostStatus.DRAFT
        )
        db.add(post4)
        
        # Post 5: Oferta especial
        post5 = Post(
            title="Oferta Black Friday - 50% de Descuento",
            content="""
🎉 OFERTA ESPECIAL BLACK FRIDAY 🎉

Por tiempo limitado, obtén 50% de descuento en todos nuestros planes.

💰 Código: BLACKFRIDAY2025
⏰ Válido hasta: 30 de Noviembre

Incluye:
- Acceso completo a todas las funciones
- Soporte prioritario
- Actualizaciones gratuitas por 1 año
- Capacitación personalizada

No dejes pasar esta oportunidad única!
            """.strip(),
            status=PostStatus.DRAFT
        )
        db.add(post5)
        
        db.commit()
        
        print("✅ Seeds creados exitosamente!")
        print(f"   - {db.query(Post).count()} posts creados")
        
        # Mostrar IDs de posts creados
        posts = db.query(Post).all()
        print("\n📝 Posts creados:")
        for post in posts:
            print(f"   - {post.id}: {post.title}")
        
    except Exception as e:
        print(f"❌ Error creando seeds: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Creando datos de ejemplo...")
    create_sample_posts()
