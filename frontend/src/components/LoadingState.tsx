interface LoadingStateProps {
  message?: string;
}

/**
 * Loading state component
 */
export function LoadingState({ message = "AI agents analyzing context..." }: LoadingStateProps) {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="flex flex-col items-center gap-3">
        <div className="w-8 h-8 border-2 border-neutral-700 border-t-blue-400 rounded-full animate-spin"></div>
        <div className="text-neutral-400">{message}</div>
      </div>
    </div>
  );
}
