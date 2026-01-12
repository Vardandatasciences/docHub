import { useState, useRef } from 'react';
import { Upload, X, Plus, FileUp, Check, CheckCircle2, Circle, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Category } from '@/types/document';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';
import { ProcessingModal } from '@/components/ProcessingModal';
import { Separator } from '@/components/ui/separator';

interface UploadModalProps {
  categories: Category[];
  // New flow: upload only needs the file; category is chosen later after AI suggestion
  onUpload: (file: File) => Promise<{ documentId: number }>;
  onAddCategory: (name: string) => Promise<Category>;
  onSaveDocument: (documentId: number, categoryId: number, summary?: string) => Promise<void>;
}

export function UploadModal({ categories, onUpload, onAddCategory, onSaveDocument }: UploadModalProps) {
  const [open, setOpen] = useState(false);
  const [newCategory, setNewCategory] = useState('');
  const [isCreatingCategory, setIsCreatingCategory] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [processingModalOpen, setProcessingModalOpen] = useState(false);
  const [processingDocumentId, setProcessingDocumentId] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleCreateCategory = async () => {
    if (newCategory.trim()) {
      try {
        const category = await onAddCategory(newCategory.trim());
        setNewCategory('');
        setIsCreatingCategory(false);
      } catch (error) {
        // Error toast handled in parent
      }
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Please select a file');
      return;
    }

    try {
      setIsUploading(true);
      const result = await onUpload(selectedFile);
      
      // Close upload modal and open processing modal
      setOpen(false);
      setSelectedFile(null);
      setProcessingDocumentId(result.documentId);
      setProcessingModalOpen(true);
    } catch (error) {
      // Error toast handled in parent
    } finally {
      setIsUploading(false);
    }
  };

  const handleProcessingSave = async (documentId: number, categoryId: number, summary?: string) => {
    await onSaveDocument(documentId, categoryId, summary);
    setProcessingModalOpen(false);
    setProcessingDocumentId(null);
  };

  const handleProcessingCancel = () => {
    setProcessingModalOpen(false);
    setProcessingDocumentId(null);
  };

  const resetModal = () => {
    setSelectedFile(null);
    setNewCategory('');
    setIsCreatingCategory(false);
  };

  return (
    <>
    <Dialog open={open} onOpenChange={(isOpen) => {
      setOpen(isOpen);
      if (!isOpen) resetModal();
    }}>
      <DialogTrigger asChild>
        <Button variant="accent" size="lg" className="gap-2">
          <Upload className="w-5 h-5" />
          Upload Document
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">Upload Document</DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Step Indicator */}
          <div className="flex items-center justify-between px-2">
            {/* Step 1 */}
            <div className="flex flex-col items-center flex-1">
              <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300",
                selectedFile
                  ? "bg-green-500 border-green-500 text-white"
                  : "bg-background border-primary text-primary"
              )}>
                {selectedFile ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : (
                  <span className="font-semibold text-sm">1</span>
                )}
              </div>
              <p className={cn(
                "mt-2 text-xs font-medium text-center",
                selectedFile ? "text-green-600" : "text-foreground"
              )}>
                Select File
              </p>
            </div>

            {/* Connector Line 1-2 */}
            <div className={cn(
              "h-0.5 flex-1 mx-2 transition-all duration-300",
              selectedFile ? "bg-green-500" : "bg-border"
            )} />

            {/* Step 2 */}
            <div className="flex flex-col items-center flex-1">
              <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300",
                isUploading
                  ? "bg-primary border-primary text-white"
                  : "bg-background border-border text-muted-foreground"
              )}>
                {isUploading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <span className="font-semibold text-sm">2</span>
                )}
              </div>
              <p className={cn(
                "mt-2 text-xs font-medium text-center",
                isUploading ? "text-primary" : "text-muted-foreground"
              )}>
                Upload & Process
              </p>
            </div>

            {/* Connector Line 2-3 */}
            <div className={cn(
              "h-0.5 flex-1 mx-2 transition-all duration-300",
              isUploading ? "bg-primary/50" : "bg-border"
            )} />

            {/* Step 3 */}
            <div className="flex flex-col items-center flex-1">
              <div className="w-10 h-10 rounded-full flex items-center justify-center border-2 bg-background border-border text-muted-foreground">
                <span className="font-semibold text-sm">3</span>
              </div>
              <p className="mt-2 text-xs font-medium text-center text-muted-foreground">
                Category & Summary
              </p>
            </div>
          </div>

          <Separator className="my-4" />

          {/* Step 1: File Selection */}
          <div className="space-y-4 transition-all duration-300">
            <div className="flex items-center gap-2">
              <div className={cn(
                "w-6 h-6 rounded-full flex items-center justify-center",
                selectedFile ? "bg-green-500" : "bg-primary"
              )}>
                <span className="text-white text-xs font-bold">1</span>
              </div>
              <h3 className="font-semibold text-base">Select Document</h3>
              {selectedFile && (
                <CheckCircle2 className="w-5 h-5 text-green-500 ml-auto" />
              )}
            </div>

            <div
              onClick={() => fileInputRef.current?.click()}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              className={cn(
                "border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all duration-200",
                isDragging
                  ? "border-accent bg-accent/5 scale-[1.02]"
                  : selectedFile
                  ? "border-green-500 bg-green-50/50"
                  : "border-border hover:border-primary/50 hover:bg-muted/50"
              )}
            >
              <input
                ref={fileInputRef}
                type="file"
                onChange={handleFileSelect}
                className="hidden"
                accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt"
              />
              
              {selectedFile ? (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center">
                    <Check className="w-8 h-8 text-green-600" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground text-lg">{selectedFile.name}</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </p>
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Click to change file
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-3">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center">
                    <FileUp className="w-8 h-8 text-primary" />
                  </div>
                  <div>
                    <p className="font-semibold text-foreground text-lg">
                      Drop your file here or click to browse
                    </p>
                    <p className="text-sm text-muted-foreground mt-2">
                      Supports PDF, DOC, XLS, PPT, and TXT files
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>

          <Separator className="my-4" />

          {/* Step 2: Upload & Processing Preview */}
          <div className="space-y-4 opacity-50">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full flex items-center justify-center bg-border">
                <span className="text-muted-foreground text-xs font-bold">2</span>
              </div>
              <h3 className="font-semibold text-base text-muted-foreground">Upload & Processing</h3>
            </div>
            <div className="p-6 bg-muted/50 rounded-xl border border-border">
              <p className="text-sm text-muted-foreground text-center">
                Your document will be uploaded and processed automatically after file selection
              </p>
            </div>
          </div>

          <Separator className="my-4" />

          {/* Step 3: Category & Summary Preview */}
          <div className="space-y-4 opacity-50">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full flex items-center justify-center bg-border">
                <span className="text-muted-foreground text-xs font-bold">3</span>
              </div>
              <h3 className="font-semibold text-base text-muted-foreground">Category & Summary</h3>
            </div>
            <div className="p-6 bg-muted/50 rounded-xl border border-border">
              <p className="text-sm text-muted-foreground text-center">
                AI will suggest a category and generate a summary after processing
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-3 pt-4 border-t border-border">
          <Button
            variant="outline"
            onClick={() => setOpen(false)}
            className="flex-1"
            disabled={isUploading}
          >
            Cancel
          </Button>
          <Button
            variant="accent"
            onClick={handleUpload}
            disabled={!selectedFile || isUploading}
            className="flex-1 gap-2"
          >
            {isUploading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Uploading...
              </>
            ) : (
              <>
                <Upload className="w-4 h-4" />
                Upload & Analyze
              </>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>

      {/* Processing Modal - Separate from UploadModal */}
      {processingDocumentId !== null && (
        <ProcessingModal
          open={processingModalOpen}
          documentId={processingDocumentId}
          fileName={selectedFile?.name || 'Document'}
          categories={categories}
          onSave={handleProcessingSave}
          onCancel={handleProcessingCancel}
          onAddCategory={onAddCategory}
        />
      )}
  </>
  );
}
