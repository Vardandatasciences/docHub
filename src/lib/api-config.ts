/**
 * Centralized API Configuration
 * Easy switching between development and production
 */

// Get API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002/api';

// Environment
const ENV = import.meta.env.VITE_ENV || 'development';

// Token storage keys
const TOKEN_KEY = 'docHub_access_token';
const REFRESH_TOKEN_KEY = 'docHub_refresh_token';
const USER_KEY = 'docHub_user';

// API Configuration
export const apiConfig = {
  baseURL: API_BASE_URL,
  environment: ENV,
  timeout: 30000, // 30 seconds
  
  // Token management
  tokenKey: TOKEN_KEY,
  refreshTokenKey: REFRESH_TOKEN_KEY,
  userKey: USER_KEY,
  
  // Endpoints
  endpoints: {
    // Auth
    register: '/auth/register',
    login: '/auth/login',
    logout: '/auth/logout',
    me: '/auth/me',
    refresh: '/auth/refresh',
    
    // Documents
    documents: '/documents',
    documentUpload: '/documents/upload',
    documentUploadAuto: '/documents/upload-auto',
    documentUpdateCategory: (id: string | number) => `/documents/${id}/category`,
    documentById: (id: string | number) => `/documents/${id}`,
    
    // Categories
    categories: '/categories',
    categoryById: (id: string | number) => `/categories/${id}`,
    
    // Users
    users: '/users',
    profile: '/users/profile',
    
    // Stats
    stats: '/stats',
    
    // Chat
    chat: {
      sessions: '/chat/sessions',
      sessionById: (id: number) => `/chat/sessions/${id}`,
      messages: (sessionId: number) => `/chat/sessions/${sessionId}/messages`,
      messagesStream: (sessionId: number) => `/chat/sessions/${sessionId}/messages/stream`,
    },
    
    // Health
    health: '/health',
  },
};

// Helper function to get full URL
export const getApiUrl = (endpoint: string): string => {
  return `${apiConfig.baseURL}${endpoint}`;
};

// Helper to get stored token
export const getStoredToken = (): string | null => {
  return localStorage.getItem(apiConfig.tokenKey);
};

// Helper to get stored refresh token
export const getStoredRefreshToken = (): string | null => {
  return localStorage.getItem(apiConfig.refreshTokenKey);
};

// Helper to store tokens
export const storeTokens = (accessToken: string, refreshToken: string): void => {
  localStorage.setItem(apiConfig.tokenKey, accessToken);
  localStorage.setItem(apiConfig.refreshTokenKey, refreshToken);
};

// Helper to clear tokens
export const clearTokens = (): void => {
  localStorage.removeItem(apiConfig.tokenKey);
  localStorage.removeItem(apiConfig.refreshTokenKey);
  localStorage.removeItem(apiConfig.userKey);
};

// Helper to check if running in development
export const isDevelopment = (): boolean => {
  return apiConfig.environment === 'development';
};

// Log configuration in development
if (isDevelopment()) {
  console.log('🔧 API Configuration:', {
    baseURL: apiConfig.baseURL,
    environment: apiConfig.environment,
  });
}



