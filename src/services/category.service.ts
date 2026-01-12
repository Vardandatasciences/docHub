/**
 * Category Service
 * Handles all category-related API calls
 */

import { apiClient } from '@/lib/api-client';
import { apiConfig } from '@/lib/api-config';
import { Category } from '@/types/document';

export interface CategoryResponse {
  id: number;
  name: string;
  color: string;
  description?: string;
  icon?: string;
  count: number;
  isActive: boolean;
  createdBy?: string;
  createdAt?: string;
}

export interface CreateCategoryRequest {
  name: string;
  color?: string;
  description?: string;
  icon?: string;
}

export const categoryService = {
  /**
   * Get all categories
   */
  async getCategories(includeInactive = false): Promise<{ categories: CategoryResponse[] }> {
    const endpoint = includeInactive
      ? `${apiConfig.endpoints.categories}?include_inactive=true`
      : apiConfig.endpoints.categories;
    
    return await apiClient.get<{ categories: CategoryResponse[] }>(endpoint);
  },

  /**
   * Get single category by ID
   */
  async getCategoryById(id: string | number): Promise<{ category: CategoryResponse }> {
    return await apiClient.get<{ category: CategoryResponse }>(
      apiConfig.endpoints.categoryById(id)
    );
  },

  /**
   * Create new category
   */
  async createCategory(data: CreateCategoryRequest): Promise<{ message: string; category: CategoryResponse }> {
    return await apiClient.post<{ message: string; category: CategoryResponse }>(
      apiConfig.endpoints.categories,
      data
    );
  },

  /**
   * Update category
   */
  async updateCategory(
    id: string | number,
    data: Partial<CreateCategoryRequest>
  ): Promise<{ message: string; category: CategoryResponse }> {
    return await apiClient.put<{ message: string; category: CategoryResponse }>(
      apiConfig.endpoints.categoryById(id),
      data
    );
  },

  /**
   * Delete category
   */
  async deleteCategory(id: string | number): Promise<{ message: string }> {
    return await apiClient.delete<{ message: string }>(
      apiConfig.endpoints.categoryById(id)
    );
  },

  /**
   * Convert backend category to frontend format
   */
  convertToFrontendFormat(cat: CategoryResponse): Category {
    return {
      id: cat.id.toString(),
      name: cat.name,
      color: cat.color,
      count: cat.count,
    };
  },
};






