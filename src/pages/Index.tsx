import { Header } from '@/components/Header';
import { CategoryFilter } from '@/components/CategoryFilter';
import { SearchBar } from '@/components/SearchBar';
import { DocumentGrid } from '@/components/DocumentGrid';
import { UploadModal } from '@/components/UploadModal';
import { StatsBar } from '@/components/StatsBar';
import { useDocuments } from '@/hooks/useDocuments';

const Index = () => {
  const {
    documents,
    categories,
    selectedCategory,
    searchQuery,
    setSelectedCategory,
    setSearchQuery,
    addDocument,
    saveDocument,
    addCategory,
    getCategoryColor,
    applySuggestedCategory,
  } = useDocuments();

  return (
    <div className="min-h-screen gradient-hero">
      <Header />
      
      <main className="container mx-auto px-6 py-8">
        {/* Hero Section */}
        <div className="text-center mb-10 animate-fade-up">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            Document{' '}
            <span className="bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
              Centralization
            </span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            Your unified platform for managing, organizing, and accessing all company documents
            across every branch. Upload, categorize, and find what you need instantly.
          </p>
          
          <UploadModal
            categories={categories}
            onUpload={addDocument}
            onAddCategory={addCategory}
            onSaveDocument={saveDocument}
          />
        </div>

        {/* Stats Bar */}
        <div className="mb-8">
          <StatsBar
            totalDocuments={documents.length}
            totalCategories={categories.length}
          />
        </div>

        {/* Search & Filters */}
        <div className="space-y-6 mb-8">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
          
          <CategoryFilter
            categories={categories}
            selectedCategory={selectedCategory}
            onSelectCategory={setSelectedCategory}
          />
        </div>

        {/* Document Count */}
        <div className="flex items-center justify-between mb-6 animate-fade-up" style={{ animationDelay: '0.2s' }}>
          <h2 className="text-lg font-semibold text-foreground">
            {selectedCategory ? `${selectedCategory}` : 'All Documents'}
            <span className="ml-2 text-sm font-normal text-muted-foreground">
              ({documents.length} {documents.length === 1 ? 'document' : 'documents'})
            </span>
          </h2>
        </div>

        {/* Document Grid */}
        <DocumentGrid
          documents={documents}
          getCategoryColor={getCategoryColor}
          onApplySuggestedCategory={applySuggestedCategory}
        />
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card/50 mt-16">
        <div className="container mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">
              © 2024 DocHub. Enterprise Document Management Platform.
            </p>
            <p className="text-sm text-muted-foreground">
              Centralizing documents across all branches.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
