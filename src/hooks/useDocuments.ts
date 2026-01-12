import { useState, useMemo, useEffect, useCallback } from 'react';
import { Document, Category } from '@/types/document';
import { documentService } from '@/services/document.service';
import { categoryService } from '@/services/category.service';
import { toast } from 'sonner';

export function useDocuments() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchCategories = useCallback(async () => {
    try {
      const response = await categoryService.getCategories();
      const formattedCategories = response.categories.map(cat => 
        categoryService.convertToFrontendFormat(cat)
      );
      setCategories(formattedCategories);
    } catch (error: any) {
      console.error('Failed to fetch categories:', error);
      toast.error('Failed to load categories');
    }
  }, []);

  const fetchDocuments = useCallback(async () => {
    try {
      setLoading(true);
      
      // Find category ID if category is selected
      const categoryId = selectedCategory 
        ? categories.find(cat => cat.name === selectedCategory)?.id 
        : undefined;
      
      const response = await documentService.getDocuments({
        category_id: categoryId ? parseInt(categoryId) : undefined,
        search: searchQuery || undefined,
      });
      
      const formattedDocs = response.documents
        .map(doc => documentService.convertToFrontendFormat(doc))
        // Filter out documents that are processing or pending Save
        // Documents with status='processing' or documents in 'Uncategorized' with suggested_category
        // (meaning they're waiting to be saved in the processing modal)
        .filter(doc => {
          // Show documents that are ready and either:
          // 1. Don't have a suggested category (already saved/confirmed)
          // 2. Have a category other than 'Uncategorized' (already saved)
          // 3. Are still processing (will be handled by the modal)
          if (doc.status === 'processing') {
            return false; // Don't show processing documents
          }
          // If document is in 'Uncategorized' and has a suggested category, it's pending Save
          if (doc.category === 'Uncategorized' && doc.suggestedCategory) {
            return false; // Don't show until Save is clicked
          }
          return true;
        });
      
      setDocuments(formattedDocs);
    } catch (error: any) {
      console.error('Failed to fetch documents:', error);
      toast.error('Failed to load documents');
    } finally {
      setLoading(false);
    }
  }, [selectedCategory, searchQuery, categories]);

  // Fetch categories on mount
  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  // Fetch documents on mount and when dependencies change
  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const addDocument = async (file: File) => {
    try {
      const response = await documentService.uploadDocumentAuto(
        file,
        file.name
      );

      // Return documentId - document will be added to list after Save is clicked
      return { documentId: response.document.id };
    } catch (error: any) {
      console.error('Failed to upload document:', error);
      toast.error(error.message || 'Failed to upload document');
      throw error;
    }
  };

  const saveDocument = async (documentId: number, categoryId: number, summary?: string) => {
    try {
      // Update document category and summary
      await documentService.updateDocumentCategory(documentId, categoryId, summary);
      
      // Refresh documents and categories to reflect updated category and counts
      await fetchDocuments();
      await fetchCategories();
      
      toast.success('Document saved successfully!');
    } catch (error: any) {
      console.error('Failed to save document:', error);
      toast.error(error.message || 'Failed to save document');
      throw error;
    }
  };

  const addCategory = async (name: string) => {
    try {
      const response = await categoryService.createCategory({ name });
      const newCategory = categoryService.convertToFrontendFormat(response.category);
      setCategories((prev) => [...prev, newCategory]);
      toast.success('Category created successfully!');
      return newCategory;
    } catch (error: any) {
      console.error('Failed to create category:', error);
      toast.error(error.message || 'Failed to create category');
      throw error;
    }
  };

  const getCategoryColor = (categoryName: string) => {
    const category = categories.find((c) => c.name === categoryName);
    return category?.color || 'hsl(38 92% 50%)';
  };

  const applySuggestedCategory = async (doc: Document) => {
    try {
      if (!doc.suggestedCategory) {
        toast.error('No AI suggested category available for this document.');
        return;
      }

      const category = categories.find(
        (c) => c.name.toLowerCase() === doc.suggestedCategory!.toLowerCase()
      );

      if (!category) {
        toast.error(`Suggested category "${doc.suggestedCategory}" not found. Please create it first.`);
        return;
      }

      await documentService.updateDocumentCategory(doc.id, parseInt(category.id));

      // Refresh documents and categories to reflect updated category and counts
      await fetchDocuments();
      await fetchCategories();

      toast.success('Category updated to AI suggestion.');
    } catch (error: any) {
      console.error('Failed to apply suggested category:', error);
      toast.error(error.message || 'Failed to apply suggested category');
    }
  };

  const filteredDocuments = useMemo(() => {
    return documents;
  }, [documents]);

  return {
    documents: filteredDocuments,
    categories,
    selectedCategory,
    searchQuery,
    setSelectedCategory,
    setSearchQuery,
    addDocument,
    saveDocument,
    addCategory,
    getCategoryColor,
    loading,
    refreshDocuments: fetchDocuments,
    refreshCategories: fetchCategories,
    applySuggestedCategory,
  };
}
