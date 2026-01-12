import { FileText, Download, ExternalLink, Calendar, User, Sparkles } from 'lucide-react';
import { Document } from '@/types/document';
import { Button } from '@/components/ui/button';
import { format } from 'date-fns';
import { documentService } from '@/services/document.service';
import { toast } from 'sonner';
import { useState } from 'react';

interface DocumentCardProps {
  document: Document;
  categoryColor: string;
  index: number;
  onApplySuggestedCategory: (doc: Document) => Promise<void>;
}

const fileIcons: Record<string, string> = {
  pdf: '📄',
  docx: '📝',
  xlsx: '📊',
  pptx: '📽️',
  default: '📁',
};

export function DocumentCard({ document, categoryColor, index, onApplySuggestedCategory }: DocumentCardProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isApplyingCategory, setIsApplyingCategory] = useState(false);

  const isProcessing = document.status === 'processing';
  const hasSuggestion =
    !!document.suggestedCategory &&
    document.suggestedCategory.toLowerCase() !== document.category.toLowerCase();

  const handleView = async () => {
    // If URL is already available, use it directly
    if (document.url) {
      window.open(document.url, '_blank');
      return;
    }

    // Otherwise, fetch the document from the database to get the URL
    try {
      setIsLoading(true);
      const response = await documentService.getDocumentById(document.id);
      const docUrl = response.document.url;
      
      if (docUrl) {
        window.open(docUrl, '_blank');
      } else {
        toast.error('Document URL not found');
      }
    } catch (error: any) {
      console.error('Failed to fetch document URL:', error);
      toast.error('Failed to open document');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownload = async () => {
    // If URL is already available, use it directly
    if (document.url) {
      const link = window.document.createElement('a');
      link.href = document.url;
      link.download = document.name;
      link.click();
      return;
    }

    // Otherwise, fetch the document from the database to get the URL
    try {
      setIsLoading(true);
      const response = await documentService.getDocumentById(document.id);
      const docUrl = response.document.url;
      
      if (docUrl) {
        const link = window.document.createElement('a');
        link.href = docUrl;
        link.download = document.name;
        link.click();
      } else {
        toast.error('Document URL not found');
      }
    } catch (error: any) {
      console.error('Failed to fetch document URL:', error);
      toast.error('Failed to download document');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="group bg-card rounded-xl border border-border p-5 shadow-card hover:shadow-card-hover transition-all duration-300 hover:-translate-y-1 animate-fade-up"
      style={{ animationDelay: `${0.05 * index}s` }}
    >
      <div className="flex items-start gap-4">
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl flex-shrink-0"
          style={{ backgroundColor: `${categoryColor}15` }}
        >
          {fileIcons[document.type] || fileIcons.default}
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-foreground truncate mb-1 group-hover:text-primary transition-colors">
            {document.name}
          </h3>
          
          <div className="flex items-center gap-2 mb-3">
            <span
              className="px-2 py-0.5 rounded-full text-xs font-medium"
              style={{
                backgroundColor: `${categoryColor}20`,
                color: categoryColor,
              }}
            >
              {document.category}
            </span>
            <span className="text-xs text-muted-foreground">{document.size}</span>
          </div>
          
          <div className="flex items-center gap-4 text-xs text-muted-foreground mb-2">
            <span className="flex items-center gap-1">
              <Calendar className="w-3 h-3" />
              {format(document.uploadedAt, 'MMM d, yyyy')}
            </span>
            <span className="flex items-center gap-1">
              <User className="w-3 h-3" />
              {document.uploadedBy}
            </span>
          </div>

          {/* AI status / suggestion */}
          {isProcessing && (
            <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-amber-50 text-amber-700 text-xs font-medium mb-2">
              <Sparkles className="w-3 h-3" />
              AI analyzing...
            </div>
          )}

          {!isProcessing && hasSuggestion && (
            <div className="mt-1 mb-2">
              <div className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-primary/5 text-primary text-xs font-medium">
                <Sparkles className="w-3 h-3" />
                AI suggests:&nbsp;
                <span className="font-semibold">{document.suggestedCategory}</span>
              </div>
            </div>
          )}

          {/* Summary preview */}
          {document.summary && (
            <p className="mt-2 text-xs text-muted-foreground line-clamp-3">
              {document.summary}
            </p>
          )}
        </div>
      </div>
      
      <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border">
        <Button
          variant="ghost"
          size="sm"
          onClick={handleView}
          disabled={isLoading}
          className="flex-1 text-muted-foreground hover:text-foreground"
        >
          <ExternalLink className="w-4 h-4 mr-2" />
          {isLoading ? 'Loading...' : 'View'}
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={handleDownload}
          className="flex-1 text-muted-foreground hover:text-foreground"
        >
          <Download className="w-4 h-4 mr-2" />
          Download
        </Button>
        {!isProcessing && hasSuggestion && (
          <Button
            variant="outline"
            size="sm"
            disabled={isApplyingCategory}
            onClick={async () => {
              try {
                setIsApplyingCategory(true);
                await onApplySuggestedCategory(document);
              } finally {
                setIsApplyingCategory(false);
              }
            }}
            className="flex-1 text-xs"
          >
            {isApplyingCategory ? 'Applying...' : 'Apply AI Category'}
          </Button>
        )}
      </div>
    </div>
  );
}
