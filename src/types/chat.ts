/**
 * Chat Types - TypeScript interfaces for chatbot functionality
 */

export interface ChatSession {
  id: number;
  userId: number;
  documentId: number | null;
  documentName?: string | null;
  sessionName: string | null;
  lastMessage?: string;
  createdAt: string;
  updatedAt: string;
}

export interface ChatMessage {
  id: number;
  sessionId: number;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata: {
    sources?: Array<{
      documentId: number;
      documentName: string;
    }>;
    tokensUsed?: number;
    error?: string;
  } | null;
  createdAt: string;
}

export interface ChatSessionWithMessages extends ChatSession {
  messages: ChatMessage[];
}

export interface CreateSessionRequest {
  documentId?: number;
  sessionName?: string;
}

export interface SendMessageRequest {
  message: string;
  documentId?: number;
}

export interface SendMessageResponse {
  message: string;
  userMessage: ChatMessage;
  assistantMessage: ChatMessage;
}




