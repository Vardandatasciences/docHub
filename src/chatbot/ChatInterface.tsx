/**
 * ChatInterface Component
 * Main chat interface for document Q&A
 */

import { useState, useEffect, useRef } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Loader2, Send, Bot, User, FileText } from 'lucide-react';
import { ChatMessage, SendMessageRequest } from '@/types/chat';
import { chatService } from '@/services/chat.service';
import { toast } from 'sonner';

interface ChatInterfaceProps {
  sessionId: number | null;
  documentId?: number | null;
  documentName?: string;
  onMessageSent?: () => void;
}

export function ChatInterface({
  sessionId,
  documentId,
  documentName,
  onMessageSent,
}: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load messages when session changes
  useEffect(() => {
    if (sessionId) {
      loadMessages();
    } else {
      setMessages([]);
    }
  }, [sessionId]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    if (!sessionId) return;

    try {
      setIsLoadingMessages(true);
      const response = await chatService.getSession(sessionId);
      setMessages(response.session.messages || []);
    } catch (error: any) {
      console.error('Failed to load messages:', error);
      toast.error(error.message || 'Failed to load chat history');
    } finally {
      setIsLoadingMessages(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!input.trim() || !sessionId || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);

    // Optimistically add user message
    const tempUserMessage: ChatMessage = {
      id: Date.now(), // Temporary ID
      sessionId,
      role: 'user',
      content: userMessage,
      metadata: null,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempUserMessage]);

    // Create streaming assistant message
    const streamingMessageId = Date.now() + 1;
    const streamingMessage: ChatMessage = {
      id: streamingMessageId,
      sessionId,
      role: 'assistant',
      content: '',
      metadata: null,
      createdAt: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, streamingMessage]);

    try {
      console.log('Sending streaming message with documentId:', documentId, 'sessionId:', sessionId);
      
      let fullResponse = '';
      let assistantMessageId: number | null = null;
      let sources: any[] = [];

      // Ensure documentId is a number if provided, or undefined if not
      const requestData: SendMessageRequest = {
        message: userMessage,
        ...(documentId !== null && documentId !== undefined ? { documentId: Number(documentId) } : {}),
      };
      
      console.log('Sending message with data:', requestData);
      
      await chatService.sendMessageStream(
        sessionId,
        requestData,
        // onChunk - update streaming message
        (chunk: string) => {
          fullResponse += chunk;
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === streamingMessageId
                ? { ...msg, content: fullResponse }
                : msg
            )
          );
        },
        // onComplete - finalize message
        (completeResponse: string, messageId: number, messageSources: any[]) => {
          fullResponse = completeResponse;
          assistantMessageId = messageId;
          sources = messageSources;

          // Replace streaming message with final message
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === streamingMessageId
                ? {
                    ...msg,
                    id: messageId,
                    content: fullResponse,
                    metadata: { sources },
                  }
                : msg
            )
          );

          // Replace temp user message with real one (if we have it from response)
          // For now, keep the temp one as it's already displayed

          setIsLoading(false);
          onMessageSent?.();
        },
        // onError
        (error: string) => {
          console.error('Streaming error:', error);
          toast.error(error || 'Failed to stream message');
          
          // Remove streaming message and add error message
          setMessages((prev) => {
            const filtered = prev.filter((msg) => msg.id !== streamingMessageId);
            const errorMessage: ChatMessage = {
              id: Date.now(),
              sessionId,
              role: 'assistant',
              content: `Error: ${error}. Please try again.`,
              metadata: { error },
              createdAt: new Date().toISOString(),
            };
            return [...filtered, errorMessage];
          });
          
          setIsLoading(false);
        }
      );
    } catch (error: any) {
      console.error('Failed to send message:', error);
      const errorMsg = error?.message || error?.data?.error || 'Failed to send message';
      toast.error(errorMsg);
      
      // Remove streaming message on error
      setMessages((prev) => prev.filter((msg) => msg.id !== streamingMessageId));
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: Date.now(),
        sessionId,
        role: 'assistant',
        content: `Error: ${errorMsg}. Please try again or check if Ollama is running.`,
        metadata: { error: errorMsg },
        createdAt: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMessage]);
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!sessionId) {
    return (
      <Card className="flex-1 flex items-center justify-center p-8">
        <div className="text-center text-muted-foreground">
          <Bot className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>Select a chat session or create a new one to start chatting</p>
        </div>
      </Card>
    );
  }

  return (
    <Card className="flex flex-col h-full">
      {/* Header */}
      {documentName && (
        <div className="p-4 border-b flex items-center gap-2">
          <FileText className="w-4 h-4 text-muted-foreground" />
          <span className="text-sm font-medium">{documentName}</span>
        </div>
      )}

      {/* Messages Area */}
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        {isLoadingMessages ? (
          <div className="flex items-center justify-center h-full">
            <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
          </div>
        ) : messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-muted-foreground">
            <Bot className="w-12 h-12 mb-4 opacity-50" />
            <p className="mb-2">Start a conversation</p>
            <p className="text-sm">
              Ask questions about your document{documentName ? ` "${documentName}"` : 's'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-3 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-primary text-primary-foreground">
                      <Bot className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                )}

                <div
                  className={`max-w-[80%] rounded-lg p-3 ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">
                    {message.content}
                    {isLoading && 
                     message.role === 'assistant' && 
                     message.id === messages[messages.length - 1]?.id && (
                      <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse">▊</span>
                    )}
                  </p>
                  
                  {/* Sources */}
                  {message.metadata?.sources && message.metadata.sources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-border/50">
                      <p className="text-xs opacity-70 mb-1">Sources:</p>
                      <div className="flex flex-wrap gap-1">
                        {message.metadata.sources.map((source, idx) => (
                          <Badge key={idx} variant="secondary" className="text-xs">
                            {source.documentName}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Error */}
                  {message.metadata?.error && (
                    <div className="mt-2 pt-2 border-t border-border/50">
                      <p className="text-xs opacity-70 text-destructive">
                        Error: {message.metadata.error}
                      </p>
                    </div>
                  )}

                  <p className="text-xs opacity-70 mt-1">
                    {new Date(message.createdAt).toLocaleTimeString([], {
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </p>
                </div>

                {message.role === 'user' && (
                  <Avatar className="w-8 h-8">
                    <AvatarFallback className="bg-secondary">
                      <User className="w-4 h-4" />
                    </AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
        )}
      </ScrollArea>

      {/* Input Area */}
      <div className="p-4 border-t">
        <div className="flex gap-2">
          <Textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message... (Press Enter to send, Shift+Enter for new line)"
            className="min-h-[60px] resize-none"
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            size="icon"
            className="h-[60px] w-[60px]"
          >
            {isLoading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </Button>
        </div>
      </div>
    </Card>
  );
}

