/**
 * Document Service
 * Handles all document-related API calls
 */

import { apiClient } from '@/lib/api-client';
import { apiConfig } from '@/lib/api-config';
import { Document } from '@/types/document';

export interface DocumentResponse {
  id: number;
  name: string;
  originalName: string;
  category: string;
  categoryId: number;
  categoryColor: string;
  size: string;
  type: string;
  uploadedAt: string;
  uploadedBy: string;
  url: string;
  s3Key: string;
  summary?: string;
  extractedText?: string;
  pageCount?: number;
  status: string;
  // AI-related fields from backend
  suggestedCategory?: string | null;
  aiTags?: string[] | null;
  processingStatus?: string | null;
}

export interface DocumentListResponse {
  documents: DocumentResponse[];
  total: number;
  page: number;
  perPage: number;
  totalPages: number;
}

export interface UploadDocumentResponse {
  message: string;
  document: DocumentResponse;
  uploadResult: any;
  // Indicates whether background AI processing started
  processing?: 'started' | 'not_needed';
}

export const documentService = {
  /**
   * Get all documents with filters
   */
  async getDocuments(params?: {
    category_id?: number;
    search?: string;
    page?: number;
    per_page?: number;
  }): Promise<DocumentListResponse> {
    const queryParams = new URLSearchParams();
    
    if (params?.category_id) {
      queryParams.append('category_id', params.category_id.toString());
    }
    if (params?.search) {
      queryParams.append('search', params.search);
    }
    if (params?.page) {
      queryParams.append('page', params.page.toString());
    }
    if (params?.per_page) {
      queryParams.append('per_page', params.per_page.toString());
    }
    
    const queryString = queryParams.toString();
    const endpoint = queryString 
      ? `${apiConfig.endpoints.documents}?${queryString}`
      : apiConfig.endpoints.documents;
    
    return await apiClient.get<DocumentListResponse>(endpoint);
  },

  /**
   * Get single document by ID
   */
  async getDocumentById(id: string | number): Promise<{ document: DocumentResponse }> {
    return await apiClient.get<{ document: DocumentResponse }>(
      apiConfig.endpoints.documentById(id)
    );
  },

  /**
   * Upload document
   */
  async uploadDocument(
    file: File,
    categoryId: number,
    customName?: string
  ): Promise<UploadDocumentResponse> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category_id', categoryId.toString());
    
    if (customName) {
      formData.append('custom_name', customName);
    }
    
    return await apiClient.upload<UploadDocumentResponse>(
      apiConfig.endpoints.documentUpload,
      formData
    );
  },

  /**
   * Upload document WITHOUT requiring category (AI-assisted flow)
   * Uses /documents/upload-auto
   */
  async uploadDocumentAuto(
    file: File,
    customName?: string
  ): Promise<UploadDocumentResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    if (customName) {
      formData.append('custom_name', customName);
    }
    
    return await apiClient.upload<UploadDocumentResponse>(
      apiConfig.endpoints.documentUploadAuto,
      formData
    );
  },

  /**
   * Update document category after upload
   * Optionally update summary as well
   */
  async updateDocumentCategory(
    id: string | number,
    categoryId: number,
    summary?: string
  ): Promise<{ message: string }> {
    return await apiClient.put<{ message: string }>(
      apiConfig.endpoints.documentUpdateCategory(id),
      { category_id: categoryId, summary }
    );
  },

  /**
   * Delete document
   */
  async deleteDocument(id: string | number): Promise<{ message: string }> {
    return await apiClient.delete<{ message: string }>(
      apiConfig.endpoints.documentById(id)
    );
  },

  /**
   * Convert backend document to frontend format
   */
  convertToFrontendFormat(doc: DocumentResponse): Document {
    return {
      id: doc.id.toString(),
      name: doc.name,
      category: doc.category,
      size: doc.size,
      type: doc.type,
      uploadedAt: new Date(doc.uploadedAt),
      uploadedBy: doc.uploadedBy,
      url: doc.url,
      summary: doc.summary,
      suggestedCategory: doc.suggestedCategory ?? null,
      aiTags: doc.aiTags ?? null,
      status: doc.status,
      processingStatus: doc.processingStatus ?? null,
    };
  },
};



