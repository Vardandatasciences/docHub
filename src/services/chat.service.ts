/**
 * Chat Service
 * Handles all chatbot-related API calls
 */

import { apiClient } from '@/lib/api-client';
import { apiConfig } from '@/lib/api-config';
import {
  ChatSession,
  ChatSessionWithMessages,
  CreateSessionRequest,
  SendMessageRequest,
  SendMessageResponse,
} from '@/types/chat';

export interface SessionsListResponse {
  sessions: ChatSession[];
  count: number;
}

export interface SessionResponse {
  session: ChatSessionWithMessages;
}

export interface CreateSessionResponse {
  message: string;
  session: ChatSession;
}

export const chatService = {
  /**
   * Create a new chat session
   */
  async createSession(data?: CreateSessionRequest): Promise<CreateSessionResponse> {
    return apiClient.post<CreateSessionResponse>(
      apiConfig.endpoints.chat.sessions,
      data || {}
    );
  },

  /**
   * Get all chat sessions for current user
   */
  async getSessions(): Promise<SessionsListResponse> {
    return apiClient.get<SessionsListResponse>(
      apiConfig.endpoints.chat.sessions
    );
  },

  /**
   * Get a specific chat session with all messages
   */
  async getSession(sessionId: number): Promise<SessionResponse> {
    return apiClient.get<SessionResponse>(
      apiConfig.endpoints.chat.sessionById(sessionId)
    );
  },

  /**
   * Delete a chat session
   */
  async deleteSession(sessionId: number): Promise<{ message: string }> {
    return apiClient.delete<{ message: string }>(
      apiConfig.endpoints.chat.sessionById(sessionId)
    );
  },

  /**
   * Update session name
   */
  async updateSession(sessionId: number, sessionName: string): Promise<{ message: string }> {
    return apiClient.put<{ message: string }>(
      apiConfig.endpoints.chat.sessionById(sessionId),
      { session_name: sessionName }
    );
  },

  /**
   * Send a message and get AI response
   */
  async sendMessage(
    sessionId: number,
    data: SendMessageRequest
  ): Promise<SendMessageResponse> {
    return apiClient.post<SendMessageResponse>(
      apiConfig.endpoints.chat.messages(sessionId),
      data
    );
  },

  /**
   * Send a message and stream AI response
   */
  async sendMessageStream(
    sessionId: number,
    data: SendMessageRequest,
    onChunk: (chunk: string) => void,
    onComplete: (fullResponse: string, assistantMessageId: number, sources: any[]) => void,
    onError: (error: string) => void
  ): Promise<void> {
    const token = localStorage.getItem('docHub_access_token');
    const url = `${apiConfig.baseURL}${apiConfig.endpoints.chat.messagesStream(sessionId)}`;
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error = await response.json();
      onError(error.error || 'Failed to stream message');
      return;
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      onError('No response body');
      return;
    }

    let buffer = '';
    let fullResponse = '';
    let assistantMessageId: number | null = null;
    let sources: any[] = [];

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            
            if (data.type === 'start') {
              // Streaming started
              sources = data.sources || [];
            } else if (data.type === 'chunk') {
              // New chunk of text
              fullResponse += data.content;
              onChunk(data.content);
            } else if (data.type === 'done') {
              // Streaming complete
              assistantMessageId = data.assistantMessageId;
              sources = data.sources || [];
              onComplete(data.fullResponse || fullResponse, assistantMessageId, sources);
              return;
            } else if (data.type === 'error') {
              onError(data.error || 'Streaming error');
              return;
            }
          } catch (e) {
            console.error('Error parsing SSE data:', e);
          }
        }
      }
    }
  },
};

