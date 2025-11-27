import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { postsApi } from '../api/client';

interface AdaptationPreview {
  adapted_text: string;
  hashtags: string[];
  image_suggestion: string;
  character_count: number;
  tone: string;
}

const NETWORK_ICONS: Record<string, string> = {
  facebook: '📘',
  instagram: '📷',
  linkedin: '💼',
  whatsapp: '💬',
  tiktok: '🎵',
};

export default function Preview() {
  const { postId } = useParams<{ postId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const { networks, imageUrl } = location.state || {};

  const [previews, setPreviews] = useState<Record<string, AdaptationPreview>>({});
  const [editedContent, setEditedContent] = useState<Record<string, string>>({});
  const [imageUrls, setImageUrls] = useState<Record<string, string>>({});
  const [videoUrls, setVideoUrls] = useState<Record<string, string>>({});
  const [localImagePaths, setLocalImagePaths] = useState<Record<string, string>>({}); // Rutas locales para publicación
  const [localVideoPaths, setLocalVideoPaths] = useState<Record<string, string>>({}); // Rutas locales de videos
  const [localImages, setLocalImages] = useState<Record<string, File>>({});
  const [localVideos, setLocalVideos] = useState<Record<string, File>>({}); // Videos subidos localmente
  const [imagePreviewUrls, setImagePreviewUrls] = useState<Record<string, string>>({});
  const [videoPreviewUrls, setVideoPreviewUrls] = useState<Record<string, string>>({}); // Preview de videos locales
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState(false);
  const [generatingImage, setGeneratingImage] = useState<Record<string, boolean>>({});
  const [generatingVideo, setGeneratingVideo] = useState<Record<string, boolean>>({});
  const [error, setError] = useState('');

  useEffect(() => {
    loadPreviews();
  }, [postId]);

  const loadPreviews = async () => {
    if (!postId) return;

    try {
      setLoading(true);
      
      const result = await postsApi.adaptContent(
        postId,
        networks || ['facebook'],
        true
      );
      setPreviews(result.data.preview);
      
      // Inicializar contenido editable con el texto adaptado
      const initialContent: Record<string, string> = {};
      const initialImages: Record<string, string> = {};
      Object.entries(result.data.preview).forEach(([network, preview]) => {
        initialContent[network] = (preview as AdaptationPreview).adapted_text;
        initialImages[network] = imageUrl || '';
      });
      setEditedContent(initialContent);
      setImageUrls(initialImages);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error al cargar previews');
    } finally {
      setLoading(false);
    }
  };

  const handleContentEdit = (network: string, newContent: string) => {
    setEditedContent(prev => ({
      ...prev,
      [network]: newContent
    }));
  };

  const handleImageUrlChange = (network: string, url: string) => {
    setImageUrls(prev => ({
      ...prev,
      [network]: url
    }));
    // Limpiar archivo local si se ingresa URL
    if (url && localImages[network]) {
      setLocalImages(prev => {
        const newImages = { ...prev };
        delete newImages[network];
        return newImages;
      });
      if (imagePreviewUrls[network]) {
        URL.revokeObjectURL(imagePreviewUrls[network]);
        setImagePreviewUrls(prev => {
          const newPreviews = { ...prev };
          delete newPreviews[network];
          return newPreviews;
        });
      }
    }
  };

  const handleGenerateImageAI = async (network: string) => {
    if (!postId) {
      setError('No se encontró el ID del post');
      return;
    }

    // Obtener el texto adaptado actual de esta red
    const adaptedText = editedContent[network] || previews[network]?.adapted_text || '';
    
    if (!adaptedText.trim()) {
      setError('No hay texto adaptado para generar la imagen');
      return;
    }

    setGeneratingImage(prev => ({ ...prev, [network]: true }));
    setError('');

    try {
      const result = await postsApi.generateImage(postId, network, adaptedText);
      const generatedUrl = result.data.url;
      const localPath = result.data.local_path;
      
      // Establecer la URL para preview y la ruta local para publicación
      setImageUrls(prev => ({
        ...prev,
        [network]: generatedUrl
      }));
      
      // Guardar la ruta local para usarla al publicar
      if (localPath) {
        setLocalImagePaths(prev => ({
          ...prev,
          [network]: localPath
        }));
      }

      // Limpiar imagen local si existe
      if (localImages[network]) {
        setLocalImages(prev => {
          const newImages = { ...prev };
          delete newImages[network];
          return newImages;
        });
        if (imagePreviewUrls[network]) {
          URL.revokeObjectURL(imagePreviewUrls[network]);
          setImagePreviewUrls(prev => {
            const newPreviews = { ...prev };
            delete newPreviews[network];
            return newPreviews;
          });
        }
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error generando imagen con IA');
    } finally {
      setGeneratingImage(prev => ({ ...prev, [network]: false }));
    }
  };

  const handleGenerateVideoAI = async (network: string) => {
    if (!postId) {
      setError('No se encontró el ID del post');
      return;
    }

    // Obtener el texto adaptado actual de esta red
    const adaptedText = editedContent[network] || previews[network]?.adapted_text || '';
    
    if (!adaptedText.trim()) {
      setError('No hay texto adaptado para generar el video');
      return;
    }

    setGeneratingVideo(prev => ({ ...prev, [network]: true }));
    setError('');

    try {
      const result = await postsApi.generateVideo(postId, network, adaptedText, 4);
      const generatedUrl = result.data.url;
      const localPath = result.data.local_path;
      
      // Establecer la URL para preview y la ruta local para publicación
      setVideoUrls(prev => ({
        ...prev,
        [network]: generatedUrl
      }));
      
      // Guardar la ruta local para usarla al publicar
      if (localPath) {
        setLocalVideoPaths(prev => ({
          ...prev,
          [network]: localPath
        }));
      }

      // Limpiar imagen si se genera video
      setImageUrls(prev => {
        const newUrls = { ...prev };
        delete newUrls[network];
        return newUrls;
      });
      setLocalImagePaths(prev => {
        const newPaths = { ...prev };
        delete newPaths[network];
        return newPaths;
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Error generando video con IA');
    } finally {
      setGeneratingVideo(prev => ({ ...prev, [network]: false }));
    }
  };

  const handleLocalImageChange = (network: string, file: File | null) => {
    if (!file) {
      // Remover imagen local
      setLocalImages(prev => {
        const newImages = { ...prev };
        delete newImages[network];
        return newImages;
      });
      if (imagePreviewUrls[network]) {
        URL.revokeObjectURL(imagePreviewUrls[network]);
        setImagePreviewUrls(prev => {
          const newPreviews = { ...prev };
          delete newPreviews[network];
          return newPreviews;
        });
      }
      return;
    }

    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
      setError(`El archivo para ${network} debe ser una imagen`);
      return;
    }

    // Validar tamaño (máximo 5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError(`La imagen para ${network} debe ser menor a 5MB`);
      return;
    }

    // Guardar archivo y crear preview
    setLocalImages(prev => ({
      ...prev,
      [network]: file
    }));

    // Crear URL para preview
    const previewUrl = URL.createObjectURL(file);
    setImagePreviewUrls(prev => ({
      ...prev,
      [network]: previewUrl
    }));

    // Limpiar URL de imagen si hay archivo local
    if (imageUrls[network]) {
      setImageUrls(prev => ({
        ...prev,
        [network]: ''
      }));
    }
  };

  const handleLocalVideoChange = (network: string, file: File | null) => {
    if (!file) {
      // Remover video local
      setLocalVideos(prev => {
        const newVideos = { ...prev };
        delete newVideos[network];
        return newVideos;
      });
      if (videoPreviewUrls[network]) {
        URL.revokeObjectURL(videoPreviewUrls[network]);
        setVideoPreviewUrls(prev => {
          const newPreviews = { ...prev };
          delete newPreviews[network];
          return newPreviews;
        });
      }
      return;
    }

    // Validar tipo de archivo
    if (!file.type.startsWith('video/')) {
      setError(`El archivo para ${network} debe ser un video`);
      return;
    }

    // Validar tamaño (máximo 50MB para videos)
    if (file.size > 50 * 1024 * 1024) {
      setError(`El video para ${network} debe ser menor a 50MB`);
      return;
    }

    // Guardar archivo y crear preview
    setLocalVideos(prev => ({
      ...prev,
      [network]: file
    }));

    // Crear URL para preview
    const previewUrl = URL.createObjectURL(file);
    setVideoPreviewUrls(prev => ({
      ...prev,
      [network]: previewUrl
    }));

    // Limpiar video generado con IA si hay archivo local
    if (videoUrls[network]) {
      setVideoUrls(prev => {
        const newUrls = { ...prev };
        delete newUrls[network];
        return newUrls;
      });
      setLocalVideoPaths(prev => {
        const newPaths = { ...prev };
        delete newPaths[network];
        return newPaths;
      });
    }
  };

  const handlePublish = async () => {
    if (!postId) return;

    setPublishing(true);
    setError('');

    try {
      console.log('🚀 Iniciando publicación...');
      console.log('Networks:', networks);
      console.log('LocalVideos:', localVideos);
      console.log('LocalVideoPaths:', localVideoPaths);
      
      // Adaptar contenido usando el contenido editado
      await postsApi.adaptContent(postId, networks || ['facebook'], false);

      // Subir todas las imágenes locales primero (las que el usuario subió manualmente)
      const uploadedUrls: Record<string, string> = {};
      for (const network of networks || ['facebook']) {
        if (localImages[network]) {
          try {
            const uploadResult = await postsApi.uploadImage(localImages[network]);
            uploadedUrls[network] = uploadResult.data.url;
          } catch (err) {
            console.error(`Error subiendo imagen para ${network}:`, err);
            setError(`Error subiendo imagen para ${network}`);
            setPublishing(false);
            return;
          }
        }
      }

      // Publicar cada red con su media específica
      for (const network of networks || ['facebook']) {
        console.log(`📤 Procesando red: ${network}`);
        
        // Caso especial: TikTok con video (generado por IA o subido)
        const hasTikTokVideo = network === 'tiktok' && (localVideoPaths[network] || localVideos[network]);
        console.log(`  - Es TikTok con video: ${hasTikTokVideo}`);
        
        if (hasTikTokVideo) {
          try {
            // Usar el texto adaptado como título
            const tiktokTitle = editedContent[network] || previews[network]?.adapted_text || 'Video generado con IA';
            // Limitar título a 150 caracteres para TikTok
            const truncatedTitle = tiktokTitle.length > 150 ? tiktokTitle.substring(0, 147) + '...' : tiktokTitle;
            
            console.log(`  - Título TikTok: ${truncatedTitle}`);
            
            if (localVideos[network]) {
              // Video subido por el usuario
              console.log(`  - Subiendo video local: ${localVideos[network].name}`);
              const result = await postsApi.uploadVideoToTikTok(
                localVideos[network],
                truncatedTitle,
                'PUBLIC_TO_EVERYONE',
                postId // Pasar el postId para actualizar estado
              );
              console.log(`  - ✅ Resultado:`, result);
            } else if (localVideoPaths[network]) {
              // Video generado con IA - usar ruta local
              console.log(`  - Publicando video IA desde: ${localVideoPaths[network]}`);
              const result = await postsApi.publishToTikTok(
                localVideoPaths[network],
                truncatedTitle,
                'PUBLIC_TO_EVERYONE',
                postId // Pasar el postId para actualizar estado
              );
              console.log(`  - ✅ Resultado:`, result);
            }
          } catch (err: any) {
            console.error(`❌ Error publicando video en TikTok:`, err);
            setError(`Error publicando en TikTok: ${err.response?.data?.detail || err.message}`);
            // Continuar con las demás redes
          }
        } else {
          // Para otras redes o TikTok sin video, usar el flujo normal
          const finalMediaUrl = uploadedUrls[network] || localImagePaths[network] || imageUrls[network] || imageUrl;
          console.log(`  - Publicando con flujo normal, media: ${finalMediaUrl || 'sin media'}`);
          await postsApi.publish(postId, finalMediaUrl || undefined);
        }
      }

      console.log('✅ Publicación completada, navegando a dashboard...');
      // Navegar a dashboard
      navigate('/dashboard', { replace: true });
    } catch (err: any) {
      console.error('❌ Error general:', err);
      setError(err.response?.data?.detail || 'Error al publicar');
    } finally {
      setPublishing(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Generando adaptaciones...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Preview de Adaptaciones
          </h1>
          <p className="text-gray-600">
            Revisa cómo se verá tu contenido en cada red social
          </p>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Grid de Previews */}
        <div className="grid md:grid-cols-2 gap-6 mb-6">
          {Object.entries(previews).map(([network, preview]) => (
            <div
              key={network}
              className="bg-white rounded-lg shadow-md p-6 border-t-4 border-blue-500"
            >
              <div className="flex items-center mb-4">
                <span className="text-3xl mr-3">
                  {NETWORK_ICONS[network] || '📱'}
                </span>
                <div>
                  <h3 className="text-xl font-bold capitalize">{network}</h3>
                  <p className="text-sm text-gray-500">
                    {editedContent[network]?.length || 0} caracteres
                  </p>
                </div>
              </div>

              {/* Texto Adaptado - EDITABLE */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Texto Adaptado (editable)
                </label>
                <textarea
                  value={editedContent[network] || preview.adapted_text}
                  onChange={(e) => handleContentEdit(network, e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={6}
                  placeholder="Edita el contenido adaptado..."
                />
              </div>

              {/* URL de Imagen - EDITABLE */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  URL de Imagen (opcional)
                </label>
                <input
                  type="url"
                  value={imageUrls[network] || ''}
                  onChange={(e) => handleImageUrlChange(network, e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="https://ejemplo.com/imagen.jpg"
                  disabled={!!localImages[network]}
                />
                {imageUrls[network] && (
                  <button
                    onClick={() => handleImageUrlChange(network, '')}
                    className="mt-2 text-sm text-red-600 hover:text-red-800"
                  >
                    ✕ Quitar imagen URL
                  </button>
                )}
              </div>

              {/* Generar Imagen/Video con IA */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Generar contenido con IA
                </label>
                <div className={`grid ${network === 'tiktok' ? 'grid-cols-2' : 'grid-cols-1'} gap-2`}>
                  {/* Botón Generar Imagen - Para todas las redes excepto TikTok */}
                  {network !== 'tiktok' && (
                    <button
                      onClick={() => handleGenerateImageAI(network)}
                      disabled={generatingImage[network] || !!localImages[network]}
                      className="px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-md hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2"
                    >
                      {generatingImage[network] ? (
                        <>
                          <span className="animate-spin">🎨</span>
                          <span className="text-sm">Generando...</span>
                        </>
                      ) : (
                        <>
                          <span>🖼️</span>
                          <span className="text-sm">Generar Imagen con IA</span>
                        </>
                      )}
                    </button>
                  )}
                  
                  {/* Botón Generar Video - Solo para TikTok */}
                  {network === 'tiktok' && (
                    <>
                      <button
                        onClick={() => handleGenerateImageAI(network)}
                        disabled={generatingImage[network] || generatingVideo[network] || !!localImages[network]}
                        className="px-4 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-md hover:from-purple-700 hover:to-blue-700 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2"
                      >
                        {generatingImage[network] ? (
                          <>
                            <span className="animate-spin">🎨</span>
                            <span className="text-sm">Generando...</span>
                          </>
                        ) : (
                          <>
                            <span>🖼️</span>
                            <span className="text-sm">Imagen IA</span>
                          </>
                        )}
                      </button>
                      <button
                        onClick={() => handleGenerateVideoAI(network)}
                        disabled={generatingVideo[network] || generatingImage[network] || !!localImages[network]}
                        className="px-4 py-3 bg-gradient-to-r from-pink-600 to-orange-500 text-white rounded-md hover:from-pink-700 hover:to-orange-600 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all font-medium flex items-center justify-center gap-2"
                      >
                        {generatingVideo[network] ? (
                          <>
                            <span className="animate-spin">🎬</span>
                            <span className="text-sm">Generando...</span>
                          </>
                        ) : (
                          <>
                            <span>🎬</span>
                            <span className="text-sm">Video IA (4s)</span>
                          </>
                        )}
                      </button>
                    </>
                  )}
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  {network === 'tiktok' 
                    ? 'Genera una imagen con DALL-E o un video de 4 segundos con Sora'
                    : 'Genera una imagen profesional con DALL-E basada en el contenido'
                  }
                </p>
              </div>

              {/* Vista previa de Video generado con IA - Solo para TikTok */}
              {network === 'tiktok' && videoUrls[network] && !localVideos[network] && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    🎬 Video generado con IA
                  </label>
                  <div className="relative">
                    <video
                      src={videoUrls[network]}
                      controls
                      className="w-full rounded-md border border-gray-200"
                    />
                    <button
                      onClick={() => {
                        setVideoUrls(prev => {
                          const newUrls = { ...prev };
                          delete newUrls[network];
                          return newUrls;
                        });
                        setLocalVideoPaths(prev => {
                          const newPaths = { ...prev };
                          delete newPaths[network];
                          return newPaths;
                        });
                      }}
                      className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-600 text-sm"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              )}

              {/* Subir Video Local - Solo para TikTok */}
              {network === 'tiktok' && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    📹 Subir video desde tu computadora
                  </label>
                  <div className="flex items-center gap-3">
                    <label className="flex-1 cursor-pointer">
                      <div className="border-2 border-dashed border-pink-300 rounded-md p-4 hover:border-pink-500 transition-colors text-center bg-pink-50">
                        <input
                          type="file"
                          accept="video/*"
                          onChange={(e) => {
                            const file = e.target.files?.[0] || null;
                            handleLocalVideoChange(network, file);
                          }}
                          className="hidden"
                          disabled={!!videoUrls[network]}
                        />
                        <span className="text-sm text-gray-600">
                          {localVideos[network]
                            ? `✅ ${localVideos[network].name}`
                            : '🎬 Seleccionar video (máx 50MB)'}
                        </span>
                      </div>
                    </label>
                    {localVideos[network] && (
                      <button
                        onClick={() => handleLocalVideoChange(network, null)}
                        className="px-3 py-2 text-sm text-red-600 hover:text-red-800 border border-red-300 rounded-md hover:bg-red-50"
                      >
                        ✕ Quitar
                      </button>
                    )}
                  </div>
                  {videoPreviewUrls[network] && (
                    <div className="mt-3">
                      <video
                        src={videoPreviewUrls[network]}
                        controls
                        className="w-full rounded-md border border-gray-300"
                      />
                    </div>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    Formatos soportados: MP4, MOV, WebM. Máximo 50MB.
                  </p>
                </div>
              )}

              {/* Subir Imagen Local */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  O subir imagen desde tu computadora
                </label>
                <div className="flex items-center gap-3">
                  <label className="flex-1 cursor-pointer">
                    <div className="border-2 border-dashed border-gray-300 rounded-md p-4 hover:border-blue-500 transition-colors text-center">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={(e) => {
                          const file = e.target.files?.[0] || null;
                          handleLocalImageChange(network, file);
                        }}
                        className="hidden"
                        disabled={!!imageUrls[network]}
                      />
                      <span className="text-sm text-gray-600">
                        {localImages[network]
                          ? `✅ ${localImages[network].name}`
                          : '📎 Seleccionar imagen'}
                      </span>
                    </div>
                  </label>
                  {localImages[network] && (
                    <button
                      onClick={() => handleLocalImageChange(network, null)}
                      className="px-3 py-2 text-sm text-red-600 hover:text-red-800 border border-red-300 rounded-md hover:bg-red-50"
                    >
                      ✕ Quitar
                    </button>
                  )}
                </div>
                {imagePreviewUrls[network] && (
                  <div className="mt-3">
                    <img
                      src={imagePreviewUrls[network]}
                      alt={`Preview ${network}`}
                      className="w-full h-48 object-cover rounded-md border border-gray-300"
                    />
                  </div>
                )}
                {imageUrls[network] && (
                  <div className="mt-3">
                    <img
                      src={imageUrls[network]}
                      alt={`Preview ${network}`}
                      className="w-full h-48 object-cover rounded-md border border-gray-300"
                      onError={(e) => {
                        (e.target as HTMLImageElement).style.display = 'none';
                      }}
                    />
                  </div>
                )}
              </div>

              {/* Hashtags */}
              {preview.hashtags && preview.hashtags.length > 0 && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hashtags Sugeridos
                  </label>
                  <div className="flex flex-wrap gap-2">
                    {preview.hashtags.map((tag, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          const currentText = editedContent[network] || preview.adapted_text;
                          if (!currentText.includes(tag)) {
                            handleContentEdit(network, currentText + ' ' + tag);
                          }
                        }}
                        className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm hover:bg-blue-200 cursor-pointer transition-colors"
                      >
                        {tag}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Tono */}
              {preview.tone && (
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tono
                  </label>
                  <p className="text-gray-600 text-sm">{preview.tone}</p>
                </div>
              )}

              {/* Sugerencia de Imagen */}
              {preview.image_suggestion && !imageUrls[network] && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    💡 Sugerencia de Imagen IA
                  </label>
                  <p className="text-gray-600 text-sm italic bg-yellow-50 p-3 rounded-md border border-yellow-200">
                    {preview.image_suggestion}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Botones de Acción */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex gap-4">
            <button
              onClick={() => navigate('/create')}
              className="flex-1 px-6 py-3 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors font-medium"
            >
              ← Volver a Editar
            </button>
            <button
              onClick={handlePublish}
              disabled={publishing}
              className="flex-1 px-6 py-3 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:bg-green-400 disabled:cursor-not-allowed transition-colors font-medium"
            >
              {publishing ? 'Publicando...' : '✅ Confirmar y Publicar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
