import { Document } from '@/types/document';
import { DocumentCard } from './DocumentCard';
import { FileX } from 'lucide-react';

interface DocumentGridProps {
  documents: Document[];
  getCategoryColor: (category: string) => string;
  onApplySuggestedCategory: (doc: Document) => Promise<void>;
}

export function DocumentGrid({ documents, getCategoryColor, onApplySuggestedCategory }: DocumentGridProps) {
  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center animate-fade-in">
        <div className="w-20 h-20 rounded-full bg-muted flex items-center justify-center mb-4">
          <FileX className="w-10 h-10 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-semibold text-foreground mb-2">No documents found</h3>
        <p className="text-muted-foreground max-w-md">
          Try adjusting your search or filter criteria, or upload a new document to get started.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
      {documents.map((doc, index) => (
        <DocumentCard
          key={doc.id}
          document={doc}
          categoryColor={getCategoryColor(doc.category)}
          onApplySuggestedCategory={onApplySuggestedCategory}
          index={index}
        />
      ))}
    </div>
  );
}
