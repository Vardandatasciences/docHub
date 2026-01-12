import { useState, useEffect } from 'react';
import { Loader2, CheckCircle2, FileText, Sparkles, Plus, X } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Category } from '@/types/document';
import { documentService } from '@/services/document.service';
import { cn } from '@/lib/utils';
import { toast } from 'sonner';

interface ProcessingModalProps {
  open: boolean;
  documentId: number;
  fileName: string;
  categories: Category[];
  onSave: (documentId: number, categoryId: number, summary?: string) => Promise<void>;
  onCancel: () => void;
  onAddCategory: (name: string) => Promise<Category>;
}

type ProcessingStage = 'processing' | 'categories' | 'summary' | 'ready';

export function ProcessingModal({
  open,
  documentId,
  fileName,
  categories,
  onSave,
  onCancel,
  onAddCategory,
}: ProcessingModalProps) {
  const [stage, setStage] = useState<ProcessingStage>('processing');
  const [progress, setProgress] = useState(0);
  const [processingStatus, setProcessingStatus] = useState<string>('uploading');
  const [suggestedCategories, setSuggestedCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [summary, setSummary] = useState<string | null>(null);
  const [isGeneratingSummary, setIsGeneratingSummary] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isCreatingCategory, setIsCreatingCategory] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [localCategories, setLocalCategories] = useState<Category[]>(categories);

  // Update local categories when categories prop changes
  useEffect(() => {
    setLocalCategories(categories);
  }, [categories]);

  // Poll document status
  useEffect(() => {
    if (!open || stage !== 'processing') return;

    let pollInterval: NodeJS.Timeout;
    let progressTimer: NodeJS.Timeout;
    let currentProgress = 0;

    const pollStatus = async () => {
      try {
        const response = await documentService.getDocumentById(documentId);
        const doc = response.document;

        // Update progress based on processing status
        if (doc.processingStatus === 'ocr') {
          setProcessingStatus('Extracting text from document...');
          if (currentProgress < 40) currentProgress = 40;
        } else if (doc.processingStatus === 'ai_analysis') {
          setProcessingStatus('Analyzing document with AI...');
          if (currentProgress < 70) currentProgress = 70;
        } else if (doc.processingStatus === 'completed' && doc.suggestedCategory) {
          setProcessingStatus('Processing complete!');
          currentProgress = 100;
          setProgress(100);
          
          // Show suggested category first, then all available categories
          const suggested = doc.suggestedCategory ? [doc.suggestedCategory] : [];
          // Get all category names that aren't the suggested one
          const otherCategories = localCategories
            .map(c => c.name)
            .filter(name => !suggested.includes(name));
          setSuggestedCategories([...suggested, ...otherCategories]);
          setStage('categories');
          return;
        } else if (doc.status === 'failed') {
          setProcessingStatus('Processing failed. Please try again.');
          return;
        }

        setProgress(currentProgress);
      } catch (error) {
        console.error('Failed to poll document status:', error);
      }
    };

    // Simulate progress increment
    progressTimer = setInterval(() => {
      if (currentProgress < 90 && stage === 'processing') {
        currentProgress += 5;
        setProgress(Math.min(currentProgress, 90));
      }
    }, 1000);

    // Poll status every 2 seconds
    pollInterval = setInterval(pollStatus, 2000);
    pollStatus(); // Initial poll

    return () => {
      if (pollInterval) clearInterval(pollInterval);
      if (progressTimer) clearInterval(progressTimer);
    };
  }, [open, documentId, stage, localCategories]);

  // Generate summary after category selection
  useEffect(() => {
    if (stage === 'summary' && selectedCategory && !summary && !isGeneratingSummary) {
      generateSummary();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [stage, selectedCategory, summary, isGeneratingSummary]);

  const generateSummary = async () => {
    setIsGeneratingSummary(true);
    try {
      const response = await documentService.getDocumentById(documentId);
      const doc = response.document;
      
      // If summary already exists, use it
      if (doc.summary) {
        setSummary(doc.summary);
        setStage('ready');
        setIsGeneratingSummary(false);
        return;
      }

      // Otherwise, generate a simple summary from extracted text
      const extractedText = doc.extractedText || '';
      if (extractedText && extractedText.length > 100) {
        // Create a better summary: first paragraph or first 500 chars, then a preview
        const firstParagraph = extractedText.split('\n\n')[0] || extractedText.split('\n')[0];
        const preview = firstParagraph.length > 500 
          ? firstParagraph.substring(0, 500) + '...'
          : firstParagraph;
        
        // Get word count for context
        const wordCount = extractedText.split(/\s+/).length;
        const pageCount = doc.pageCount ? ` (${doc.pageCount} pages)` : '';
        
        setSummary(
          `Document Summary${pageCount}:\n\n` +
          `${preview}\n\n` +
          `Category: ${selectedCategory}\n` +
          `Total words: ${wordCount.toLocaleString()}`
        );
      } else if (extractedText) {
        // Short text, use it as-is
        setSummary(
          `Document Summary:\n\n${extractedText}\n\n` +
          `Category: ${selectedCategory}`
        );
      } else {
        // No extracted text available
        setSummary(
          `Document "${fileName}" has been uploaded and categorized as "${selectedCategory}".\n\n` +
          `Status: Ready for use.`
        );
      }
      
      setStage('ready');
    } catch (error) {
      console.error('Failed to generate summary:', error);
      setSummary(
        `Document "${fileName}" has been categorized as "${selectedCategory}".\n\n` +
        `Ready for use.`
      );
      setStage('ready');
    } finally {
      setIsGeneratingSummary(false);
    }
  };

  const handleCategorySelect = (categoryName: string) => {
    setSelectedCategory(categoryName);
    setStage('summary');
  };

  const handleCreateCategory = async () => {
    if (!newCategoryName.trim()) {
      toast.error('Please enter a category name');
      return;
    }

    try {
      const newCategory = await onAddCategory(newCategoryName.trim());
      setLocalCategories((prev) => [...prev, newCategory]);
      setNewCategoryName('');
      setIsCreatingCategory(false);
      
      // Auto-select the newly created category
      setSelectedCategory(newCategory.name);
      setSuggestedCategories((prev) => [...prev, newCategory.name]);
      
      // Move to summary stage
      setStage('summary');
      
      toast.success(`Category "${newCategory.name}" created and selected`);
    } catch (error: any) {
      console.error('Failed to create category:', error);
      toast.error(error.message || 'Failed to create category');
    }
  };

  const handleSave = async () => {
    if (!selectedCategory) return;

    const category = localCategories.find(c => c.name === selectedCategory);
    if (!category) {
      toast.error('Selected category not found');
      return;
    }

    try {
      setIsSaving(true);
      await onSave(documentId, parseInt(category.id), summary || undefined);
    } catch (error) {
      console.error('Failed to save:', error);
      throw error;
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    // Reset state
    setStage('processing');
    setProgress(0);
    setProcessingStatus('uploading');
    setSuggestedCategories([]);
    setSelectedCategory(null);
    setSummary(null);
    setIsCreatingCategory(false);
    setNewCategoryName('');
    onCancel();
  };

  // Determine step completion states
  const step2Completed = stage !== 'processing';
  const step3Active = stage === 'categories' || stage === 'summary' || stage === 'ready';

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleCancel()}>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="text-xl font-semibold">Processing Document</DialogTitle>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Step Indicator */}
          <div className="flex items-center justify-between px-2">
            {/* Step 1 - Always completed */}
            <div className="flex flex-col items-center flex-1">
              <div className="w-10 h-10 rounded-full flex items-center justify-center border-2 bg-green-500 border-green-500 text-white">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <p className="mt-2 text-xs font-medium text-center text-green-600">
                Select File
              </p>
            </div>

            {/* Connector Line 1-2 */}
            <div className={cn(
              "h-0.5 flex-1 mx-2 transition-all duration-300",
              step2Completed ? "bg-green-500" : "bg-primary"
            )} />

            {/* Step 2 */}
            <div className="flex flex-col items-center flex-1">
              <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300",
                step2Completed
                  ? "bg-green-500 border-green-500 text-white"
                  : "bg-primary border-primary text-white"
              )}>
                {step2Completed ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : (
                  <Loader2 className="w-5 h-5 animate-spin" />
                )}
              </div>
              <p className={cn(
                "mt-2 text-xs font-medium text-center",
                step2Completed ? "text-green-600" : "text-primary"
              )}>
                Upload & Process
              </p>
            </div>

            {/* Connector Line 2-3 */}
            <div className={cn(
              "h-0.5 flex-1 mx-2 transition-all duration-300",
              step3Active ? "bg-primary" : "bg-border"
            )} />

            {/* Step 3 */}
            <div className="flex flex-col items-center flex-1">
              <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-300",
                stage === 'ready'
                  ? "bg-green-500 border-green-500 text-white"
                  : step3Active
                  ? "bg-primary border-primary text-white"
                  : "bg-background border-border text-muted-foreground"
              )}>
                {stage === 'ready' ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : (
                  <span className="font-semibold text-sm">3</span>
                )}
              </div>
              <p className={cn(
                "mt-2 text-xs font-medium text-center",
                step3Active ? (stage === 'ready' ? "text-green-600" : "text-primary") : "text-muted-foreground"
              )}>
                Category & Summary
              </p>
            </div>
          </div>

          <Separator className="my-4" />

          {/* Step 1: File Selection - Completed */}
          <div className="space-y-4 opacity-60">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full flex items-center justify-center bg-green-500">
                <span className="text-white text-xs font-bold">1</span>
              </div>
              <h3 className="font-semibold text-base">Select Document</h3>
              <CheckCircle2 className="w-5 h-5 text-green-500 ml-auto" />
            </div>
            <div className="p-6 bg-green-50/50 rounded-xl border border-green-200">
              <div className="flex flex-col items-center gap-2">
                <div className="w-12 h-12 rounded-full bg-green-100 flex items-center justify-center">
                  <CheckCircle2 className="w-6 h-6 text-green-600" />
                </div>
                <p className="font-semibold text-foreground">{fileName}</p>
              </div>
            </div>
          </div>

          <Separator className="my-4" />

          {/* Step 2: Upload & Processing */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className={cn(
                "w-6 h-6 rounded-full flex items-center justify-center",
                step2Completed ? "bg-green-500" : "bg-primary"
              )}>
                <span className="text-white text-xs font-bold">2</span>
              </div>
              <h3 className="font-semibold text-base">Upload & Processing</h3>
              {step2Completed && (
                <CheckCircle2 className="w-5 h-5 text-green-500 ml-auto" />
              )}
            </div>

            {stage === 'processing' ? (
              <div className="p-6 bg-primary/5 rounded-xl border border-primary/20">
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <Loader2 className="w-5 h-5 animate-spin text-primary" />
                    <div className="flex-1">
                      <p className="font-medium">{processingStatus}</p>
                      <p className="text-sm text-muted-foreground">{fileName}</p>
                    </div>
                  </div>
                  <Progress value={progress} className="h-2" />
                  <p className="text-xs text-center text-muted-foreground">
                    {progress}% complete
                  </p>
                </div>
              </div>
            ) : (
              <div className="p-6 bg-green-50/50 rounded-xl border border-green-200">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                  <p className="font-medium text-green-700">Processing Complete</p>
                </div>
              </div>
            )}
          </div>

          <Separator className="my-4" />

          {/* Step 3: Category & Summary */}
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <div className={cn(
                "w-6 h-6 rounded-full flex items-center justify-center",
                stage === 'ready' ? "bg-green-500" : step3Active ? "bg-primary" : "bg-border"
              )}>
                <span className={cn(
                  "text-xs font-bold",
                  stage === 'ready' || step3Active ? "text-white" : "text-muted-foreground"
                )}>3</span>
              </div>
              <h3 className="font-semibold text-base">Category & Summary</h3>
              {stage === 'ready' && (
                <CheckCircle2 className="w-5 h-5 text-green-500 ml-auto" />
              )}
            </div>

            {/* Category Selection */}
            {stage === 'categories' && (
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-sm font-medium">Select Category:</p>
                    {!isCreatingCategory && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsCreatingCategory(true)}
                        className="gap-1"
                      >
                        <Plus className="w-3 h-3" />
                        New
                      </Button>
                    )}
                  </div>

                  {isCreatingCategory ? (
                    <div className="space-y-3 p-4 border-2 border-dashed border-border rounded-lg">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium">Create New Category</p>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setIsCreatingCategory(false);
                            setNewCategoryName('');
                          }}
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                      <div className="flex gap-2">
                        <Input
                          placeholder="Category name..."
                          value={newCategoryName}
                          onChange={(e) => setNewCategoryName(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') {
                              handleCreateCategory();
                            }
                          }}
                          className="flex-1"
                          autoFocus
                        />
                        <Button
                          variant="accent"
                          size="sm"
                          onClick={handleCreateCategory}
                          disabled={!newCategoryName.trim()}
                        >
                          Create
                        </Button>
                      </div>
                    </div>
                  ) : (
                    <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto">
                      {suggestedCategories.map((catName, idx) => {
                        const category = localCategories.find(c => c.name === catName);
                        const isSuggested = idx === 0;
                        return (
                          <button
                            key={catName}
                            onClick={() => handleCategorySelect(catName)}
                            className={cn(
                              "p-3 rounded-lg border-2 text-left transition-all",
                              "hover:border-primary hover:bg-primary/5",
                              selectedCategory === catName
                                ? "border-primary bg-primary/10"
                                : "border-border",
                              isSuggested && "ring-2 ring-accent"
                            )}
                          >
                            <div className="flex items-center gap-2">
                              {isSuggested && <Sparkles className="w-4 h-4 text-accent" />}
                              <div className="flex-1">
                                <p className="font-medium text-sm">{catName}</p>
                                {isSuggested && (
                                  <p className="text-xs text-muted-foreground">AI Suggested</p>
                                )}
                              </div>
                              {category && (
                                <div
                                  className="w-4 h-4 rounded-full"
                                  style={{ backgroundColor: category.color }}
                                />
                              )}
                            </div>
                          </button>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Summary */}
            {(stage === 'summary' || stage === 'ready') && (
              <div className="space-y-4">
                {selectedCategory && (
                  <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                    <CheckCircle2 className="w-5 h-5 text-green-500" />
                    <div>
                      <p className="text-sm font-medium">Category Selected</p>
                      <p className="text-xs text-muted-foreground">{selectedCategory}</p>
                    </div>
                  </div>
                )}

                {isGeneratingSummary ? (
                  <div className="flex items-center gap-2 p-4 bg-muted rounded-lg">
                    <Loader2 className="w-5 h-5 animate-spin text-primary" />
                    <p className="text-sm text-muted-foreground">Generating summary...</p>
                  </div>
                ) : summary ? (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <FileText className="w-5 h-5 text-primary" />
                      <p className="font-medium">Summary</p>
                    </div>
                    <div className="p-4 bg-muted rounded-lg max-h-40 overflow-y-auto">
                      <p className="text-sm whitespace-pre-wrap">{summary}</p>
                    </div>
                  </div>
                ) : null}
              </div>
            )}

            {stage === 'processing' && (
              <div className="p-6 bg-muted/50 rounded-xl border border-border">
                <p className="text-sm text-muted-foreground text-center">
                  Category selection will be available after processing completes
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3 pt-4 border-t border-border">
          {(stage === 'categories' || stage === 'summary') && (
            <Button
              variant="outline"
              onClick={handleCancel}
              className="flex-1"
              disabled={isSaving}
            >
              Cancel
            </Button>
          )}
          {stage === 'ready' && (
            <>
              <Button
                variant="outline"
                onClick={handleCancel}
                className="flex-1"
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button
                variant="accent"
                onClick={handleSave}
                disabled={!selectedCategory || isSaving}
                className="flex-1"
              >
                {isSaving ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Document'
                )}
              </Button>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
