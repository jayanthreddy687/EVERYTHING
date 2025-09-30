import { useState, useCallback } from 'react';
import { apiService } from '../services/api';
import { getIconForCategory } from '../utils/icons';
import type { UserProfile, CalendarEvent, ScenarioDetection, AgentStats, InsightPriority, InsightCategory } from '../types';

interface FormattedInsight {
  title: string;
  message: string;
  action: string;
  category: InsightCategory;
  priority: InsightPriority;
  icon: React.JSX.Element;
  reasoning?: string;
  agentName?: string;
  confidence?: number;
}

interface UseAgentInsightsReturn {
  suggestions: FormattedInsight[];
  loading: boolean;
  error: string | null;
  agentStats: AgentStats | null;
  scenario: ScenarioDetection | null;
  fetchInsights: (selectedScenario?: string | null) => Promise<void>;
}

/**
 * Custom hook for managing agent insights and analysis
 */
export function useAgentInsights(
  userData: UserProfile | null,
  calendarData: CalendarEvent[]
): UseAgentInsightsReturn {
  const [suggestions, setSuggestions] = useState<FormattedInsight[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [agentStats, setAgentStats] = useState<AgentStats | null>(null);
  const [scenario, setScenario] = useState<ScenarioDetection | null>(null);

  const fetchInsights = useCallback(async (selectedScenario: string | null = null) => {
    if (!userData) {
      setError("User data not available");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const analysisRequest = apiService.buildAnalysisRequest(
        userData,
        calendarData,
        selectedScenario
      );

      const data = await apiService.analyze(analysisRequest);

      // Store scenario information
      if (data.scenario) {
        setScenario(data.scenario);
      }

      // Store agent statistics
      if (data.agent_stats) {
        setAgentStats(data.agent_stats);
      }

      // Transform agent insights to UI format
      const formattedSuggestions: FormattedInsight[] = data.insights.map(insight => ({
        title: insight.title,
        message: insight.message,
        action: insight.action,
        category: insight.category,
        priority: insight.priority,
        icon: getIconForCategory(insight.category)
      }));

      setSuggestions(formattedSuggestions);
    } catch (e) {
      console.error("Agent analysis error:", e);
      setError("Failed to connect to AI agents. Make sure backend is running on port 8000.");
      setSuggestions([]);
    } finally {
      setLoading(false);
    }
  }, [userData, calendarData]);

  return {
    suggestions,
    loading,
    error,
    agentStats,
    scenario,
    fetchInsights
  };
}
