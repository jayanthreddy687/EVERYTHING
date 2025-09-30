import { Brain } from "lucide-react";
import { InsightCard } from "../../components/InsightCard";
import { LoadingState } from "../../components/LoadingState";
import { EmptyState } from "../../components/EmptyState";
import { ErrorBanner } from "../../components/ErrorBanner";
import type { AgentStats, ScenarioDetection, InsightPriority, InsightCategory } from "../../types";

interface Suggestion {
  title: string;
  message: string;
  action: string;
  priority: InsightPriority;
  category: InsightCategory;
  icon: React.JSX.Element;
  agentName?: string;
  confidence?: number;
  reasoning?: string;
}

interface NowViewProps {
  suggestions: Suggestion[];
  loading: boolean;
  error: string | null;
  scenario: ScenarioDetection | null;
  agentStats: AgentStats | null;
  onAccept: (item: Suggestion) => void;
  onDismiss?: (item: Suggestion) => void;
  onRetry: () => void;
}

/**
 * NowView - Displays AI insights for the current context
 */
export function NowView({ 
  suggestions, 
  loading, 
  error, 
  scenario, 
  agentStats, 
  onAccept,
  onDismiss,
  onRetry 
}: NowViewProps) {
  return (
    <div className="flex flex-col gap-4 pb-24">
      {/* Header with scenario info */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold">AI Insights • Now</h2>
          {scenario && (
            <p className="text-xs text-neutral-400 mt-1">
              📍 {scenario.description}
            </p>
          )}
        </div>
        <div className="flex items-center gap-2 text-sm text-neutral-400">
          {loading && (
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
              Analyzing...
            </div>
          )}
          {!loading && agentStats && (
            <div className="flex items-center gap-1">
              <Brain className="w-4 h-4" />
              {agentStats.activeAgents}/{agentStats.totalInsights} agents • {agentStats.totalInsights} insights
            </div>
          )}
        </div>
      </div>

      {/* Error banner */}
      <ErrorBanner error={error} onRetry={onRetry} />

      {/* Content */}
      {loading ? (
        <LoadingState />
      ) : (
        <div className="flex flex-col gap-3">
          {suggestions.map((suggestion, index) => (
            <InsightCard 
              key={index} 
              item={suggestion} 
              onAccept={onAccept}
              onDismiss={onDismiss}
            />
          ))}
          {suggestions.length === 0 && !error && <EmptyState />}
        </div>
      )}
    </div>
  );
}
