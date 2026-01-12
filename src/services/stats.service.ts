/**
 * Statistics Service
 * Handles all statistics-related API calls
 */

import { apiClient } from '@/lib/api-client';
import { apiConfig } from '@/lib/api-config';

export interface StatsResponse {
  totalDocuments: number;
  totalCategories: number;
  totalUsers: number;
  totalStorage: number;
  totalStorageFormatted: string;
  recentUploads: number;
  categoryStats: Array<{
    name: string;
    color: string;
    count: number;
    size: number;
    sizeFormatted: string;
  }>;
  topUploaders: Array<{
    name: string;
    email: string;
    count: number;
  }>;
  fileTypeStats: Array<{
    type: string;
    count: number;
  }>;
}

export const statsService = {
  /**
   * Get dashboard statistics
   */
  async getStats(): Promise<StatsResponse> {
    return await apiClient.get<StatsResponse>(apiConfig.endpoints.stats);
  },
};






