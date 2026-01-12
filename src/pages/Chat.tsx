/**
 * Chat Page
 * Main page for AI Document Assistant Chatbot
 */

import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Header } from '@/components/Header';
import { ChatInterface } from '@/chatbot/ChatInterface';
import { ChatSessionsList } from '@/chatbot/ChatSessionsList';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { documentService } from '@/services/document.service';
import { DocumentResponse } from '@/services/document.service';
import { Loader2 } from 'lucide-react';
import { toast } from 'sonner';

const Chat = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [selectedSessionId, setSelectedSessionId] = useState<number | null>(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState<number | null>(null);
  const [selectedDocumentName, setSelectedDocumentName] = useState<string>('');
  const [documents, setDocuments] = useState<DocumentResponse[]>([]);
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false);

  // Initialize from URL params
  useEffect(() => {
    const sessionId = searchParams.get('session');
    const documentId = searchParams.get('document');
    
    if (sessionId) {
      setSelectedSessionId(parseInt(sessionId, 10));
    }
    if (documentId) {
      const docId = parseInt(documentId, 10);
      setSelectedDocumentId(docId);
      // Load document name
      loadDocumentName(docId);
    }
  }, [searchParams]);

  // Load documents for selector
  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    try {
      setIsLoadingDocuments(true);
      const response = await documentService.getDocuments({ per_page: 100 });
      setDocuments(response.documents.filter((doc) => doc.extractedText || doc.summary));
    } catch (error: any) {
      console.error('Failed to load documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setIsLoadingDocuments(false);
    }
  };

  const loadDocumentName = async (docId: number) => {
    try {
      const response = await documentService.getDocumentById(docId);
      setSelectedDocumentName(response.document.name);
    } catch (error) {
      console.error('Failed to load document name:', error);
    }
  };

  const handleSessionCreated = async (sessionId: number) => {
    setSelectedSessionId(sessionId);
    
    // If a document is selected, update the session to include it
    if (selectedDocumentId) {
      try {
        // Optionally update the session with the document, but we'll pass it in messages
        // The session document_id is optional - we'll use the selectedDocumentId from the message
        console.log(`Session ${sessionId} created with document ${selectedDocumentId}`);
      } catch (error) {
        console.error('Failed to update session with document:', error);
      }
    }
    
    setSearchParams((prev) => {
      const newParams = new URLSearchParams(prev);
      newParams.set('session', sessionId.toString());
      if (selectedDocumentId) {
        newParams.set('document', selectedDocumentId.toString());
      }
      return newParams;
    });
  };

  const handleSessionSelected = (sessionId: number | null) => {
    setSelectedSessionId(sessionId);
    setSearchParams((prev) => {
      const newParams = new URLSearchParams(prev);
      if (sessionId) {
        newParams.set('session', sessionId.toString());
      } else {
        newParams.delete('session');
      }
      if (selectedDocumentId) {
        newParams.set('document', selectedDocumentId.toString());
      }
      return newParams;
    });
  };

  const handleDocumentChange = (documentId: string) => {
    if (documentId === 'none') {
      setSelectedDocumentId(null);
      setSelectedDocumentName('');
      setSearchParams((prev) => {
        const newParams = new URLSearchParams(prev);
        newParams.delete('document');
        return newParams;
      });
    } else {
      const docId = parseInt(documentId, 10);
      setSelectedDocumentId(docId);
      loadDocumentName(docId);
      setSearchParams((prev) => {
        const newParams = new URLSearchParams(prev);
        newParams.set('document', docId.toString());
        return newParams;
      });
    }
  };

  const handleMessageSent = () => {
    // Refresh sessions list could go here if needed
  };

  return (
    <div className="min-h-screen gradient-hero">
      <Header />
      
      <main className="container mx-auto px-6 py-8 h-[calc(100vh-80px)]">
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">AI Document Assistant</h1>
          <p className="text-muted-foreground">
            Ask questions about your documents and get instant answers
          </p>
        </div>

        {/* Document Selector */}
        <div className="mb-4 max-w-md">
          <label className="text-sm font-medium mb-2 block">Select Document (Optional)</label>
          <Select
            value={selectedDocumentId?.toString() || 'none'}
            onValueChange={handleDocumentChange}
            disabled={isLoadingDocuments}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select a document to chat about..." />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">All Documents (General Query)</SelectItem>
              {documents.map((doc) => (
                <SelectItem key={doc.id} value={doc.id.toString()}>
                  {doc.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {isLoadingDocuments && (
            <div className="flex items-center gap-2 mt-2 text-sm text-muted-foreground">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Loading documents...</span>
            </div>
          )}
        </div>

        {/* Chat Layout */}
        <div className="flex gap-4 h-[calc(100%-200px)]">
          {/* Sessions List Sidebar */}
          <ChatSessionsList
            selectedSessionId={selectedSessionId}
            onSelectSession={handleSessionSelected}
            onSessionCreated={handleSessionCreated}
            documentId={selectedDocumentId}
            documentName={selectedDocumentName}
          />

          {/* Chat Interface */}
          <div className="flex-1">
            <ChatInterface
              sessionId={selectedSessionId}
              documentId={selectedDocumentId}
              documentName={selectedDocumentName}
              onMessageSent={handleMessageSent}
            />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Chat;

