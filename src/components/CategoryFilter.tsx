import { cn } from '@/lib/utils';
import { Category } from '@/types/document';
import { FolderOpen, Layers } from 'lucide-react';

interface CategoryFilterProps {
  categories: Category[];
  selectedCategory: string | null;
  onSelectCategory: (category: string | null) => void;
}

export function CategoryFilter({
  categories,
  selectedCategory,
  onSelectCategory,
}: CategoryFilterProps) {
  return (
    <div className="animate-fade-up" style={{ animationDelay: '0.1s' }}>
      <div className="flex items-center gap-2 mb-4">
        <Layers className="w-4 h-4 text-muted-foreground" />
        <h3 className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
          Categories
        </h3>
      </div>
      
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onSelectCategory(null)}
          className={cn(
            "px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
            "border hover:shadow-md",
            !selectedCategory
              ? "bg-primary text-primary-foreground border-primary shadow-md"
              : "bg-card text-foreground border-border hover:border-primary/50"
          )}
        >
          <span className="flex items-center gap-2">
            <FolderOpen className="w-4 h-4" />
            All Documents
          </span>
        </button>
        
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => onSelectCategory(category.name)}
            className={cn(
              "px-4 py-2 rounded-full text-sm font-medium transition-all duration-200",
              "border hover:shadow-md flex items-center gap-2",
              selectedCategory === category.name
                ? "text-accent-foreground border-transparent shadow-md"
                : "bg-card text-foreground border-border hover:border-primary/50"
            )}
            style={{
              backgroundColor:
                selectedCategory === category.name ? category.color : undefined,
            }}
          >
            <span
              className="w-2 h-2 rounded-full"
              style={{
                backgroundColor:
                  selectedCategory === category.name ? 'currentColor' : category.color,
              }}
            />
            {category.name}
            <span className="text-xs opacity-70">({category.count})</span>
          </button>
        ))}
      </div>
    </div>
  );
}
