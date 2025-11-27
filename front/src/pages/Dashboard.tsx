import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { postsApi } from '../api/client';

interface Post {
  id: string;
  title: string;
  content: string;
  status: 'draft' | 'processing' | 'published' | 'failed';
  created_at: string;
  updated_at: string;
  publications_count: number;
}

const STATUS_ICONS: Record<string, string> = {
  draft: '📝',
  processing: '⏳',
  published: '✅',
  failed: '❌',
};

const NETWORK_ICONS: Record<string, string> = {
  facebook: '📘',
  instagram: '📷',
  linkedin: '💼',
  whatsapp: '💬',
  tiktok: '🎵',
};

export default function Dashboard() {
  const navigate = useNavigate();
  const [posts, setPosts] = useState<Post[]>([]);
  const [filteredPosts, setFilteredPosts] = useState<Post[]>([]);
  const [postStatusSummary, setPostStatusSummary] = useState<Record<string, { published: number; total: number }>>({});
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [selectedPost, setSelectedPost] = useState<string | null>(null);
  const [postDetails, setPostDetails] = useState<any>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [retrying, setRetrying] = useState<Record<string, boolean>>({});

  const loadPosts = useCallback(async () => {
    try {
      if (posts.length === 0) {
        setLoading(true);
      }
      const result = await postsApi.listPosts(0, 100);
      setPosts(result.data);
      // Para cada post, obtener el status resumen (publicados/total)
      const statusSummary: Record<string, { published: number; total: number }> = {};
      await Promise.all(
        result.data.map(async (post: Post) => {
          try {
            const statusRes = await postsApi.getStatus(post.id);
            statusSummary[post.id] = {
              published: statusRes.data.by_status.published,
              total: statusRes.data.total_publications,
            };
          } catch (e) {
            statusSummary[post.id] = { published: 0, total: post.publications_count };
          }
        })
      );
      setPostStatusSummary(statusSummary);
    } catch (err) {
      console.error('Error loading posts:', err);
    } finally {
      setLoading(false);
    }
  }, [posts.length]);

  const loadPostDetails = useCallback(async (postId: string) => {
    try {
      const result = await postsApi.getStatus(postId);
      setPostDetails(result.data);
      setSelectedPost(postId);
    } catch (err) {
      console.error('Error loading post details:', err);
    }
  }, []);

  const handleRefreshClick = useCallback(() => {
    loadPosts();
    if (selectedPost) {
      loadPostDetails(selectedPost);
    }
  }, [loadPosts, loadPostDetails, selectedPost]);

  const handleRetryPublication = useCallback(async (publicationId: string) => {
    if (!selectedPost) return;
    
    setRetrying(prev => ({ ...prev, [publicationId]: true }));
    
    try {
      await postsApi.retryPublication(publicationId);
      // Recargar detalles del post
      await loadPostDetails(selectedPost);
      // Recargar lista de posts
      await loadPosts();
    } catch (err: any) {
      console.error('Error al reintentar publicación:', err);
      alert(err.response?.data?.detail || 'Error al reintentar publicación');
    } finally {
      setRetrying(prev => ({ ...prev, [publicationId]: false }));
    }
  }, [selectedPost, loadPostDetails, loadPosts]);

  useEffect(() => {
    loadPosts();
  }, [loadPosts]);

  // Filtrar posts por búsqueda y fechas
  useEffect(() => {
    let filtered = [...posts];

    // Filtrar por título
    if (searchQuery) {
      filtered = filtered.filter(post =>
        post.title.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Filtrar por rango de fechas
    if (startDate) {
      filtered = filtered.filter(post => {
        const postDate = new Date(post.created_at);
        const start = new Date(startDate);
        return postDate >= start;
      });
    }

    if (endDate) {
      filtered = filtered.filter(post => {
        const postDate = new Date(post.created_at);
        const end = new Date(endDate);
        end.setHours(23, 59, 59, 999); // Incluir todo el día
        return postDate <= end;
      });
    }

    setFilteredPosts(filtered);
  }, [posts, searchQuery, startDate, endDate]);

  // Auto-refresh cada 5 segundos si está habilitado
  useEffect(() => {
    if (!autoRefresh) {
      console.log('Auto-refresh desactivado por toggle');
      return;
    }

    console.log('Iniciando auto-refresh');
    
    const interval = setInterval(() => {
      console.log('Actualizando datos...', new Date().toLocaleTimeString());
      loadPosts();
      
      // Si hay un post seleccionado, actualizar sus detalles también
      if (selectedPost) {
        loadPostDetails(selectedPost);
      }
    }, 5000); // Actualizar cada 5 segundos

    return () => {
      console.log('Limpiando interval');
      clearInterval(interval);
    };
  }, [autoRefresh, loadPosts, loadPostDetails, selectedPost]);

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Dashboard de Publicaciones
              </h1>
              <p className="text-gray-600">
                Gestiona y monitorea tus publicaciones en redes sociales
              </p>
            </div>
            <div className="flex gap-3">
              {/* Botón Manual Refresh */}
              <button
                onClick={handleRefreshClick}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors flex items-center gap-2"
                title="Refrescar ahora"
              >
                <span>🔄</span>
                <span className="text-sm">Refrescar</span>
              </button>

              {/* Toggle Auto-refresh */}
              <button
                onClick={() => setAutoRefresh(!autoRefresh)}
                className={`px-4 py-2 rounded-md transition-colors flex items-center gap-2 ${
                  autoRefresh
                    ? 'bg-green-100 text-green-700 border border-green-300'
                    : 'bg-gray-100 text-gray-700 border border-gray-300'
                }`}
              >
                <span>{autoRefresh ? '✅' : '⏸️'}</span>
                <span className="text-sm">
                  {autoRefresh ? 'Auto (5s)' : 'Manual'}
                </span>
              </button>
              
              <button
                onClick={() => navigate('/create')}
                className="px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors font-medium"
              >
                ➕ Nueva Publicación
              </button>
            </div>
          </div>
        </div>

        {/* Buscador y Filtros de Fecha */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Buscador por título */}
            <div className="md:col-span-1">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                🔍 Buscar por título
              </label>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Buscar publicaciones..."
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Fecha inicio */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                📅 Desde
              </label>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Fecha fin */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                📅 Hasta
              </label>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Botón para limpiar filtros */}
          {(searchQuery || startDate || endDate) && (
            <div className="mt-3">
              <button
                onClick={() => {
                  setSearchQuery('');
                  setStartDate('');
                  setEndDate('');
                }}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded-md hover:bg-gray-300 transition-colors text-sm"
              >
                ✕ Limpiar filtros
              </button>
            </div>
          )}
        </div>

        {/* Tabla de Posts */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {loading ? (
            <div className="p-8 text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Cargando publicaciones...</p>
            </div>
          ) : filteredPosts.length === 0 ? (
              <div className="p-8 text-center">
              <p className="text-gray-600">
                {posts.length === 0
                  ? 'No hay publicaciones'
                  : 'No se encontraron publicaciones con los filtros aplicados'}
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Título
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Publicaciones
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Fecha
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredPosts.map((post) => (
                    <tr key={post.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">
                          {post.title}
                        </div>
                        <div className="text-sm text-gray-500 truncate max-w-md">
                          {post.content.substring(0, 100)}...
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {postStatusSummary[post.id]
                          ? `${postStatusSummary[post.id].published}/${postStatusSummary[post.id].total} redes`
                          : `${post.publications_count} redes`}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(post.created_at)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                        <button
                          onClick={() => loadPostDetails(post.id)}
                          className="text-blue-600 hover:text-blue-900 mr-4"
                        >
                          Ver Detalles
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Modal de Detalles */}
        {selectedPost && postDetails && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-2xl font-bold">Detalles de Publicación</h2>
                  <button
                    onClick={() => {
                      setSelectedPost(null);
                      setPostDetails(null);
                    }}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    ✕
                  </button>
                </div>

                <div className="mb-6">
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500">Estado del Post</p>
                      <p className="font-semibold">
                        {STATUS_ICONS[postDetails.post_status]}{' '}
                        {postDetails.post_status}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Total Publicaciones</p>
                      <p className="font-semibold">
                        {postDetails.total_publications}
                      </p>
                    </div>
                  </div>

                  <div className="grid grid-cols-4 gap-2 mb-6">
                    <div className="bg-yellow-50 p-3 rounded-md">
                      <p className="text-xs text-yellow-700">Pendientes</p>
                      <p className="text-xl font-bold text-yellow-900">
                        {postDetails.by_status.pending}
                      </p>
                    </div>
                    <div className="bg-blue-50 p-3 rounded-md">
                      <p className="text-xs text-blue-700">Procesando</p>
                      <p className="text-xl font-bold text-blue-900">
                        {postDetails.by_status.processing}
                      </p>
                    </div>
                    <div className="bg-green-50 p-3 rounded-md">
                      <p className="text-xs text-green-700">Publicados</p>
                      <p className="text-xl font-bold text-green-900">
                        {postDetails.by_status.published}
                      </p>
                    </div>
                    <div className="bg-red-50 p-3 rounded-md">
                      <p className="text-xs text-red-700">Fallidos</p>
                      <p className="text-xl font-bold text-red-900">
                        {postDetails.by_status.failed}
                      </p>
                    </div>
                  </div>

                  <h3 className="font-bold mb-3">Publicaciones por Red</h3>
                  <div className="space-y-3">
                    {postDetails.publications.map((pub: any) => (
                      <div
                        key={pub.id}
                        className="border border-gray-200 rounded-md p-4"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div className="flex items-center">
                            <span className="text-2xl mr-2">
                              {NETWORK_ICONS[pub.network] || '📱'}
                            </span>
                            <div>
                              <p className="font-semibold capitalize">
                                {pub.network}
                              </p>
                              <p className="text-sm text-gray-500">
                                {STATUS_ICONS[pub.status]} {pub.status}
                              </p>
                            </div>
                          </div>
                          {pub.published_at && (
                            <p className="text-sm text-gray-500">
                              {formatDate(pub.published_at)}
                            </p>
                          )}
                        </div>
                        {pub.error_message && (
                          <div className="mt-2">
                            <p className="text-sm text-red-600">
                              ❌ {pub.error_message}
                            </p>
                            {pub.status === 'failed' && (
                              <button
                                onClick={() => handleRetryPublication(pub.id)}
                                disabled={retrying[pub.id]}
                                className="mt-2 px-3 py-1 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                              >
                                {retrying[pub.id] ? '🔄 Reintentando...' : '🔄 Reintentar'}
                              </button>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
