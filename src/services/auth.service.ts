/**
 * Authentication Service
 * Handles all authentication-related API calls
 */

import { apiClient, storeTokens, clearTokens } from '@/lib/api-client';
import { apiConfig } from '@/lib/api-config';

export interface User {
  id: number;
  name: string;
  email: string;
  role: string;
  department?: string;
  phone?: string;
  profile_image_url?: string;
  is_active: boolean;
  created_at?: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  tokens: {
    access_token: string;
    refresh_token: string;
  };
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export const authService = {
  /**
   * Register a new user
   */
  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      apiConfig.endpoints.register,
      data,
      { skipAuth: true }
    );
    
    // Store tokens
    storeTokens(response.tokens.access_token, response.tokens.refresh_token);
    
    // Store user
    localStorage.setItem(apiConfig.userKey, JSON.stringify(response.user));
    
    return response;
  },

  /**
   * Login user
   */
  async login(data: LoginRequest): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>(
      apiConfig.endpoints.login,
      data,
      { skipAuth: true }
    );
    
    // Store tokens
    storeTokens(response.tokens.access_token, response.tokens.refresh_token);
    
    // Store user
    localStorage.setItem(apiConfig.userKey, JSON.stringify(response.user));
    
    return response;
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post(apiConfig.endpoints.logout);
    } catch (error) {
      // Logout locally even if API call fails
      console.error('Logout API error:', error);
    } finally {
      clearTokens();
    }
  },

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<{ user: User }> {
    return await apiClient.get<{ user: User }>(apiConfig.endpoints.me);
  },

  /**
   * Get stored user from localStorage
   */
  getStoredUser(): User | null {
    const userStr = localStorage.getItem(apiConfig.userKey);
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    const token = localStorage.getItem(apiConfig.tokenKey);
    const user = this.getStoredUser();
    return !!(token && user);
  },
};






