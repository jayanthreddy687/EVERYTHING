interface ErrorBannerProps {
  error?: string | null;
  message?: string;
  onRetry?: () => void;
}

/**
 * Error banner component
 */
export function ErrorBanner({ error, message, onRetry }: ErrorBannerProps) {
  const displayMessage = error || message;
  
  if (!displayMessage) return null;

  return (
    <div className="mb-4 p-3 bg-red-900/20 border border-red-800 rounded-xl">
      <div className="text-red-400 text-sm">{displayMessage}</div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="text-xs text-red-300 underline mt-2"
        >
          Retry connection
        </button>
      )}
    </div>
  );
}
