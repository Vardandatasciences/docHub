import { FileText, FolderOpen, Users, TrendingUp } from 'lucide-react';

interface StatsBarProps {
  totalDocuments: number;
  totalCategories: number;
}

export function StatsBar({ totalDocuments, totalCategories }: StatsBarProps) {
  const stats = [
    {
      label: 'Total Documents',
      value: totalDocuments,
      icon: FileText,
      color: 'hsl(38 92% 50%)',
    },
    {
      label: 'Categories',
      value: totalCategories,
      icon: FolderOpen,
      color: 'hsl(199 89% 48%)',
    },
    {
      label: 'Team Members',
      value: 24,
      icon: Users,
      color: 'hsl(262 83% 58%)',
    },
    {
      label: 'This Month',
      value: '+12%',
      icon: TrendingUp,
      color: 'hsl(142 71% 45%)',
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 animate-fade-up">
      {stats.map((stat, index) => (
        <div
          key={stat.label}
          className="bg-card rounded-xl border border-border p-4 shadow-card hover:shadow-card-hover transition-all duration-300"
          style={{ animationDelay: `${0.05 * index}s` }}
        >
          <div className="flex items-center gap-3">
            <div
              className="w-10 h-10 rounded-lg flex items-center justify-center"
              style={{ backgroundColor: `${stat.color}15` }}
            >
              <stat.icon className="w-5 h-5" style={{ color: stat.color }} />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{stat.value}</p>
              <p className="text-xs text-muted-foreground">{stat.label}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
