import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { postsApi } from '../api/client';

const NETWORKS = [
  { id: 'facebook', name: 'Facebook', icon: '📘' },
  { id: 'instagram', name: 'Instagram', icon: '📷' },
  { id: 'linkedin', name: 'LinkedIn', icon: '💼' },
  { id: 'whatsapp', name: 'WhatsApp', icon: '💬' },
  { id: 'tiktok', name: 'TikTok', icon: '🎵' },
];

export default function CreatePost() {
  const navigate = useNavigate();
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [selectedNetworks, setSelectedNetworks] = useState<string[]>(['facebook']);
  const [imageUrl, setImageUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleNetworkToggle = (networkId: string) => {
    setSelectedNetworks((prev) =>
      prev.includes(networkId)
        ? prev.filter((id) => id !== networkId)
        : [...prev, networkId]
    );
  };

  const handlePreview = async () => {
    if (!title.trim() || !content.trim()) {
      setError('El título y contenido son requeridos');
      return;
    }

    if (selectedNetworks.length === 0) {
      setError('Selecciona al menos una red social');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Crear post
      const createResult = await postsApi.createPost(title, content);
      const postId = createResult.data.id;

      // Generar preview
      await postsApi.adaptContent(postId, selectedNetworks, true);

      // Navegar a preview
      navigate(`/preview/${postId}`, {
        state: { networks: selectedNetworks, imageUrl },
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al generar preview');
    } finally {
      setLoading(false);
    }
  };

  const handlePublish = async () => {
    if (!title.trim() || !content.trim()) {
      setError('El título y contenido son requeridos');
      return;
    }

    if (selectedNetworks.length === 0) {
      setError('Selecciona al menos una red social');
      return;
    }

    setLoading(true);
    setError('');

    try {
      // Crear post
      const createResult = await postsApi.createPost(title, content);
      const postId = createResult.data.id;

      // Adaptar contenido
      await postsApi.adaptContent(postId, selectedNetworks, false);

      // Publicar
      await postsApi.publish(postId, imageUrl || undefined);

      // Navegar a dashboard
      navigate('/dashboard', { replace: true });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al publicar');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-6">
            Crear Nueva Publicación
          </h1>

          {error && (
            <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-red-800">{error}</p>
            </div>
          )}

          {/* Título */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Título
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Ej: Promoción 2x1 en tienda online"
              maxLength={200}
            />
          </div>

          {/* Contenido */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Contenido
              <span className="text-gray-500 ml-2">
                ({content.length}/5000)
              </span>
            </label>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={8}
              placeholder="Escribe el contenido de tu publicación..."
              maxLength={5000}
            />
          </div>

          {/* URL de Imagen */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              URL de Imagen (opcional)
            </label>
            <input
              type="url"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="https://ejemplo.com/imagen.jpg"
            />
          </div>

          {/* Redes Sociales */}
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Seleccionar Redes Sociales
            </label>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {NETWORKS.map((network) => (
                <label
                  key={network.id}
                  className={`flex items-center p-3 border rounded-md cursor-pointer transition-colors ${
                    selectedNetworks.includes(network.id)
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-300 hover:border-gray-400'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedNetworks.includes(network.id)}
                    onChange={() => handleNetworkToggle(network.id)}
                    className="mr-3 h-4 w-4 text-blue-600"
                  />
                  <span className="text-2xl mr-2">{network.icon}</span>
                  <span className="font-medium">{network.name}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Botones */}
          <div className="flex gap-4">
            <button
              onClick={handlePreview}
              disabled={loading}
              className="flex-1 px-6 py-3 bg-gray-600 text-white rounded-md hover:bg-gray-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Generando...' : '👁️ Generar Preview'}
            </button>
            <button
              onClick={handlePublish}
              disabled={loading}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-blue-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {loading ? 'Publicando...' : '🚀 Publicar Directamente'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
