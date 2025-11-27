import { useNavigate } from 'react-router-dom';

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-gray-900 mb-4">
            📱 Social Media Publisher
          </h1>
          <p className="text-2xl text-gray-600 mb-8">
            Publica en todas tus redes sociales con un solo clic
          </p>
          <p className="text-lg text-gray-500 max-w-2xl mx-auto">
            Crea contenido una vez, adáptalo automáticamente con IA para cada red social,
            y publica en Facebook, Instagram, LinkedIn, WhatsApp y TikTok simultáneamente.
          </p>
        </div>

        {/* Action Cards */}
        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto mb-16">
          {/* Crear Publicación */}
          <div 
            onClick={() => navigate('/create')}
            className="bg-white rounded-xl shadow-lg p-8 cursor-pointer transform transition-all hover:scale-105 hover:shadow-2xl"
          >
            <div className="text-5xl mb-4">✍️</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Crear Publicación
            </h2>
            <p className="text-gray-600 mb-4">
              Escribe tu contenido y selecciona las redes sociales donde quieres publicar.
              Nuestra IA adaptará el mensaje para cada plataforma.
            </p>
            <button className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium">
              Crear Nueva Publicación
            </button>
          </div>

          {/* Dashboard */}
          <div 
            onClick={() => navigate('/dashboard')}
            className="bg-white rounded-xl shadow-lg p-8 cursor-pointer transform transition-all hover:scale-105 hover:shadow-2xl"
          >
            <div className="text-5xl mb-4">📊</div>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">
              Ver Dashboard
            </h2>
            <p className="text-gray-600 mb-4">
              Monitorea todas tus publicaciones, revisa su estado en cada red social
              y accede al historial completo.
            </p>
            <button className="w-full px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium">
              Ir al Dashboard
            </button>
          </div>
        </div>

        {/* Features */}
        <div className="bg-white rounded-xl shadow-lg p-8 max-w-5xl mx-auto">
          <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">
            ✨ Características
          </h3>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-4xl mb-3">🤖</div>
              <h4 className="font-bold text-gray-900 mb-2">Adaptación con IA</h4>
              <p className="text-gray-600 text-sm">
                GPT adapta tu contenido con el tono, emojis y hashtags perfectos para cada red
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-3">⚡</div>
              <h4 className="font-bold text-gray-900 mb-2">Publicación Paralela</h4>
              <p className="text-gray-600 text-sm">
                Publica en todas las redes simultáneamente con sistema de colas
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-3">👁️</div>
              <h4 className="font-bold text-gray-900 mb-2">Vista Previa</h4>
              <p className="text-gray-600 text-sm">
                Revisa cómo se verá tu contenido antes de publicar en cada plataforma
              </p>
            </div>
          </div>
        </div>

        {/* Redes Soportadas */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 mb-4">Redes Sociales Soportadas</p>
          <div className="flex justify-center items-center gap-6 text-4xl">
            <span title="Facebook">📘</span>
            <span title="Instagram">📷</span>
            <span title="LinkedIn">💼</span>
            <span title="WhatsApp">💬</span>
            <span title="TikTok">🎵</span>
          </div>
        </div>
      </div>
    </div>
  );
}
