export interface Document {
  id: string;
  name: string;
  category: string;
  size: string;
  type: string;
  uploadedAt: Date;
  uploadedBy: string;
  url: string;
  // Optional AI/summary fields
  summary?: string;
  suggestedCategory?: string | null;
  aiTags?: string[] | null;
  status?: string;
  processingStatus?: string | null;
}

export interface Category {
  id: string;
  name: string;
  color: string;
  count: number;
}
