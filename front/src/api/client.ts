import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const TIKTOK_API_URL = import.meta.env.VITE_TIKTOK_API_URL || 'http://localhost:8001'; // URL del backend de TikTok

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para agregar token de autenticación
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Interceptor para manejar errores de autenticación
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Cliente separado para TikTok (otro backend)
export const tiktokApiClient = axios.create({
  baseURL: TIKTOK_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Tipos
export interface User {
  id: string;
  email: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Post {
  id: string;
  title: string;
  content: string;
  status: 'draft' | 'processing' | 'published' | 'failed';
  created_at: string;
  updated_at: string;
  publications_count: number;
}

export interface Publication {
  id: string;
  network: string;
  status: 'pending' | 'processing' | 'published' | 'failed';
  adapted_content: string;
  published_at: string | null;
  error_message: string | null;
  metadata: any;
}

export interface AdaptationPreview {
  adapted_text: string;
  hashtags: string[];
  image_suggestion: string;
  character_count: number;
  tone: string;
}

// API Functions
export const postsApi = {
  // Crear post
  createPost: async (title: string, content: string) => {
    const response = await apiClient.post('/api/posts', { title, content });
    return response.data;
  },

  // Listar posts
  listPosts: async (skip = 0, limit = 100, status?: string) => {
    const response = await apiClient.get('/api/posts', {
      params: { skip, limit, status },
    });
    return response.data;
  },

  // Obtener post
  getPost: async (postId: string) => {
    const response = await apiClient.get(`/api/posts/${postId}`);
    return response.data;
  },

  // Adaptar contenido
  adaptContent: async (
    postId: string,
    networks: string[],
    previewOnly: boolean = false
  ) => {
    const response = await apiClient.post(`/api/posts/${postId}/adapt`, {
      networks,
      preview_only: previewOnly,
    });
    return response.data;
  },

  // Publicar
  publish: async (postId: string, imageUrl?: string) => {
    const response = await apiClient.post(`/api/posts/${postId}/publish`, {
      image_url: imageUrl,
    });
    return response.data;
  },

  // Obtener estado
  getStatus: async (postId: string) => {
    const response = await apiClient.get(`/api/posts/${postId}/status`);
    return response.data;
  },

  // Subir imagen
  uploadImage: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/api/posts/upload-image', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // Reintentar publicación
  retryPublication: async (publicationId: string) => {
    const response = await apiClient.post(`/api/publications/${publicationId}/retry`);
    return response.data;
  },

  // Generar imagen con IA basada en el texto adaptado
  generateImage: async (postId: string, network: string, adaptedText: string) => {
    const response = await apiClient.post('/api/posts/generate-image', {
      post_id: postId,
      network,
      adapted_text: adaptedText,
    });
    return response.data;
  },

  // Generar video con Sora basado en el texto adaptado
  generateVideo: async (postId: string, network: string, adaptedText: string, duration: number = 4) => {
    const response = await apiClient.post('/api/posts/generate-video', {
      post_id: postId,
      network,
      adapted_text: adaptedText,
      duration: Math.min(duration, 4), // Máximo 4 segundos
    });
    return response.data;
  },

  // Publicar video en TikTok usando el archivo local (a través del backend principal)
  publishToTikTok: async (videoPath: string, title: string, privacyLevel: string = 'PUBLIC_TO_EVERYONE', postId?: string) => {
    const response = await apiClient.post('/api/posts/publish-to-tiktok', {
      video_path: videoPath,
      title,
      privacy_level: privacyLevel,
      disable_comment: false,
      post_id: postId,
    });
    return response.data;
  },

  // Subir video a TikTok a través del backend principal
  uploadVideoToTikTok: async (file: File, title: string, privacyLevel: string = 'PUBLIC_TO_EVERYONE', postId?: string) => {
    const formData = new FormData();
    formData.append('video', file);
    formData.append('title', title);
    formData.append('privacy_level', privacyLevel);
    formData.append('disable_comment', 'false');
    if (postId) {
      formData.append('post_id', postId);
    }
    
    const response = await apiClient.post('/api/posts/upload-video-to-tiktok', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 120000, // 2 minutos para subida de video
    });
    return response.data;
  },
};

// API de Autenticación
export const authApi = {
  // Registro de usuario
  register: async (name: string, email: string, password: string): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/register', {
      name,
      email,
      password,
    });
    return response.data;
  },

  // Login
  login: async (email: string, password: string): Promise<AuthResponse> => {
    const response = await apiClient.post('/api/auth/login', {
      email,
      password,
    });
    return response.data;
  },

  // Obtener usuario actual
  getMe: async (): Promise<User> => {
    const response = await apiClient.get('/api/auth/me');
    return response.data;
  },
};
