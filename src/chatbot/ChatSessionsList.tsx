/**
 * ChatSessionsList Component
 * Sidebar showing list of chat sessions
 */

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  MessageSquare,
  Plus,
  Trash2,
  Loader2,
  FileText,
  Clock,
} from 'lucide-react';
import { ChatSession } from '@/types/chat';
import { chatService } from '@/services/chat.service';
import { toast } from 'sonner';
import { format } from 'date-fns';

interface ChatSessionsListProps {
  selectedSessionId: number | null;
  onSelectSession: (sessionId: number | null) => void;
  onSessionCreated: (sessionId: number) => void;
  documentId?: number | null;
  documentName?: string;
}

export function ChatSessionsList({
  selectedSessionId,
  onSelectSession,
  onSessionCreated,
  documentId,
  documentName,
}: ChatSessionsListProps) {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [newSessionName, setNewSessionName] = useState('');
  const [sessionToDelete, setSessionToDelete] = useState<number | null>(null);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setIsLoading(true);
      const response = await chatService.getSessions();
      setSessions(response.sessions);
    } catch (error: any) {
      console.error('Failed to load sessions:', error);
      toast.error(error.message || 'Failed to load chat sessions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateSession = async () => {
    if (isCreating) return;

    try {
      setIsCreating(true);
      const response = await chatService.createSession({
        documentId: documentId || undefined,
        sessionName: newSessionName.trim() || undefined,
      });

      setSessions((prev) => [response.session, ...prev]);
      onSelectSession(response.session.id);
      onSessionCreated(response.session.id);
      setIsDialogOpen(false);
      setNewSessionName('');
      toast.success('Chat session created');
    } catch (error: any) {
      console.error('Failed to create session:', error);
      toast.error(error.message || 'Failed to create chat session');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDeleteSession = async (sessionId: number) => {
    try {
      await chatService.deleteSession(sessionId);
      setSessions((prev) => prev.filter((s) => s.id !== sessionId));
      
      if (selectedSessionId === sessionId) {
        onSelectSession(null);
      }
      
      setSessionToDelete(null);
      toast.success('Session deleted');
    } catch (error: any) {
      console.error('Failed to delete session:', error);
      toast.error(error.message || 'Failed to delete session');
    }
  };

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInHours = (now.getTime() - date.getTime()) / (1000 * 60 * 60);

      if (diffInHours < 24) {
        return format(date, 'HH:mm');
      } else if (diffInHours < 168) {
        return format(date, 'EEE HH:mm');
      } else {
        return format(date, 'MMM d');
      }
    } catch {
      return '';
    }
  };

  return (
    <>
      <Card className="w-80 flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between">
          <h2 className="font-semibold flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            Chat Sessions
          </h2>
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button size="icon" variant="ghost" className="h-8 w-8">
                <Plus className="w-4 h-4" />
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>New Chat Session</DialogTitle>
                <DialogDescription>
                  {documentName
                    ? `Create a new chat session for "${documentName}"`
                    : 'Create a new chat session'}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="session-name">Session Name (Optional)</Label>
                  <Input
                    id="session-name"
                    placeholder={documentName ? `Chat: ${documentName}` : 'New Chat Session'}
                    value={newSessionName}
                    onChange={(e) => setNewSessionName(e.target.value)}
                    onKeyPress={(e) => {
                      if (e.key === 'Enter' && !isCreating) {
                        handleCreateSession();
                      }
                    }}
                  />
                </div>
                {documentName && (
                  <div className="text-sm text-muted-foreground flex items-center gap-2">
                    <FileText className="w-4 h-4" />
                    <span>{documentName}</span>
                  </div>
                )}
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateSession} disabled={isCreating}>
                  {isCreating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create'
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>

        {/* Sessions List */}
        <ScrollArea className="flex-1">
          {isLoading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : sessions.length === 0 ? (
            <div className="p-8 text-center text-muted-foreground">
              <MessageSquare className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-sm">No chat sessions yet</p>
              <p className="text-xs mt-2">Create a new session to start chatting</p>
            </div>
          ) : (
            <div className="p-2 space-y-1">
              {sessions.map((session) => (
                <div
                  key={session.id}
                  className={`group relative p-3 rounded-lg cursor-pointer transition-colors ${
                    selectedSessionId === session.id
                      ? 'bg-primary text-primary-foreground'
                      : 'hover:bg-muted'
                  }`}
                  onClick={() => onSelectSession(session.id)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p
                        className={`font-medium text-sm truncate ${
                          selectedSessionId === session.id
                            ? 'text-primary-foreground'
                            : ''
                        }`}
                      >
                        {session.sessionName || 'Untitled Session'}
                      </p>
                      {session.documentName && (
                        <p
                          className={`text-xs mt-1 flex items-center gap-1 truncate ${
                            selectedSessionId === session.id
                              ? 'text-primary-foreground/80'
                              : 'text-muted-foreground'
                          }`}
                        >
                          <FileText className="w-3 h-3 flex-shrink-0" />
                          <span className="truncate">{session.documentName}</span>
                        </p>
                      )}
                      {session.lastMessage && (
                        <p
                          className={`text-xs mt-1 truncate ${
                            selectedSessionId === session.id
                              ? 'text-primary-foreground/70'
                              : 'text-muted-foreground'
                          }`}
                        >
                          {session.lastMessage}
                        </p>
                      )}
                      <div
                        className={`text-xs mt-1 flex items-center gap-1 ${
                          selectedSessionId === session.id
                            ? 'text-primary-foreground/60'
                            : 'text-muted-foreground'
                        }`}
                      >
                        <Clock className="w-3 h-3" />
                        <span>{formatDate(session.updatedAt)}</span>
                      </div>
                    </div>
                    <Button
                      size="icon"
                      variant="ghost"
                      className={`h-6 w-6 opacity-0 group-hover:opacity-100 transition-opacity ${
                        selectedSessionId === session.id
                          ? 'text-primary-foreground hover:bg-primary-foreground/20'
                          : ''
                      }`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSessionToDelete(session.id);
                      }}
                    >
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </ScrollArea>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        open={sessionToDelete !== null}
        onOpenChange={(open) => !open && setSessionToDelete(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Chat Session</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete this chat session? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={() => sessionToDelete && handleDeleteSession(sessionToDelete)}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}




