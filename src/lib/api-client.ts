/**
 * Centralized API Client
 * Handles all HTTP requests with authentication
 */

import { apiConfig, getStoredToken, getStoredRefreshToken, storeTokens, clearTokens } from './api-config';

// API Error class
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// Request options interface
interface RequestOptions extends RequestInit {
  skipAuth?: boolean;
  timeout?: number;
}

/**
 * Make HTTP request with automatic token handling
 */
async function request<T>(
  endpoint: string,
  options: RequestOptions = {}
): Promise<T> {
  const {
    skipAuth = false,
    timeout = apiConfig.timeout,
    headers = {},
    ...fetchOptions
  } = options;

  const url = `${apiConfig.baseURL}${endpoint}`;
  
  // Setup headers
  const requestHeaders: HeadersInit = {
    ...headers,
  };
  
  // Only set Content-Type for non-FormData requests
  if (!(fetchOptions.body instanceof FormData) && !headers['Content-Type']) {
    requestHeaders['Content-Type'] = 'application/json';
  }

  // Add authentication token if not skipped
  if (!skipAuth) {
    const token = getStoredToken();
    if (token) {
      requestHeaders['Authorization'] = `Bearer ${token}`;
    }
  }

  // Setup abort controller for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const response = await fetch(url, {
      ...fetchOptions,
      headers: requestHeaders,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    const isJson = contentType?.includes('application/json');

    if (!response.ok) {
      const errorData = isJson ? await response.json() : await response.text();
      
      // Handle 401 - try to refresh token
      if (response.status === 401 && !skipAuth && endpoint !== apiConfig.endpoints.refresh) {
        const refreshed = await tryRefreshToken();
        if (refreshed) {
          // Retry the original request
          return request<T>(endpoint, options);
        }
      }

      throw new ApiError(
        errorData?.message || errorData?.error || 'Request failed',
        response.status,
        errorData
      );
    }

    // Return parsed response
    return isJson ? await response.json() : await response.text();
  } catch (error) {
    clearTimeout(timeoutId);
    
    if (error instanceof ApiError) {
      throw error;
    }
    
    if (error.name === 'AbortError') {
      throw new ApiError('Request timeout', 408);
    }
    
    throw new ApiError(
      error instanceof Error ? error.message : 'Network error',
      0
    );
  }
}

/**
 * Try to refresh authentication token
 */
async function tryRefreshToken(): Promise<boolean> {
  try {
    const refreshToken = getStoredRefreshToken();
    if (!refreshToken) {
      clearTokens();
      return false;
    }

    const response = await fetch(`${apiConfig.baseURL}${apiConfig.endpoints.refresh}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${refreshToken}`,
      },
    });

    if (!response.ok) {
      clearTokens();
      return false;
    }

    const data = await response.json();
    if (data.tokens) {
      storeTokens(data.tokens.access_token, data.tokens.refresh_token);
      return true;
    }

    return false;
  } catch (error) {
    clearTokens();
    return false;
  }
}

/**
 * HTTP Methods
 */

export const apiClient = {
  // GET request
  get: <T>(endpoint: string, options?: RequestOptions) => {
    return request<T>(endpoint, { ...options, method: 'GET' });
  },

  // POST request
  post: <T>(endpoint: string, data?: any, options?: RequestOptions) => {
    return request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  // PUT request
  put: <T>(endpoint: string, data?: any, options?: RequestOptions) => {
    return request<T>(endpoint, {
      ...options,
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
  },

  // DELETE request
  delete: <T>(endpoint: string, options?: RequestOptions) => {
    return request<T>(endpoint, { ...options, method: 'DELETE' });
  },

  // Upload file (multipart/form-data)
  upload: <T>(endpoint: string, formData: FormData, options?: RequestOptions) => {
    // FormData automatically sets correct Content-Type with boundary
    return request<T>(endpoint, {
      ...options,
      method: 'POST',
      body: formData,
    });
  },
};

// Export utility functions
export { getStoredToken, storeTokens, clearTokens };

