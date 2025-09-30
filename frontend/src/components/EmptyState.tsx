import { Sparkles } from "lucide-react";

interface EmptyStateProps {
  message?: string;
}

/**
 * Empty state component
 */
export function EmptyState({ message = "No insights available" }: EmptyStateProps) {
  return (
    <div className="text-center py-8">
      <Sparkles className="w-12 h-12 text-neutral-700 mx-auto mb-3" />
      <div className="text-neutral-400">{message}</div>
    </div>
  );
}
