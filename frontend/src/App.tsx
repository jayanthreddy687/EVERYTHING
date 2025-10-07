import { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { Navigation } from './components/Navigation';
import { ScenarioSelector } from './features/scenarios/ScenarioSelector';
import { NowView } from './features/now/NowView';
import { AgendaView } from './features/agenda/AgendaView';
import { ProfileView } from './features/profile/ProfileView';
import { VoiceOnboardingView } from './features/onboarding/VoiceOnboardingView';
import { LoadingState } from './components/LoadingState';
import { ErrorBanner } from './components/ErrorBanner';
import { useAgentInsights } from './hooks/useAgentInsights';
import { useScenarios } from './hooks/useScenarios';
import { useUserData } from './hooks/useUserData';
import { useOnboarding } from './hooks/useOnboarding';
import { apiService } from './services/api';
import { APP_CONFIG } from './constants/config';
import type { TabType } from './constants/config';
import type { FeedbackAction } from './types';

function App() {
  const [activeTab, setActiveTab] = useState<TabType>(APP_CONFIG.DEFAULT_TAB as TabType);
  const [feedbackMessage, setFeedbackMessage] = useState<string | null>(null);

  const { 
    isComplete: onboardingComplete, 
    isChecking: checkingOnboarding,
    refreshStatus: refreshOnboardingStatus 
  } = useOnboarding();

  const { 
    userData, 
    calendarData, 
    loading: dataLoading, 
    error: dataError 
  } = useUserData();

  const { availableScenarios, selectedScenario, selectScenario } = useScenarios();
  const {
    suggestions,
    loading,
    error,
    agentStats,
    scenario,
    fetchInsights
  } = useAgentInsights(userData, calendarData);

  useEffect(() => {
    if (userData && calendarData.length > 0 && onboardingComplete) {
      fetchInsights(selectedScenario);
    }
  }, [selectedScenario, userData, calendarData, onboardingComplete, fetchInsights]);

  // Handle scenario selection
  function handleScenarioSelect(scenarioId: string | null): void {
    selectScenario(scenarioId);
  }

  // Record feedback helper
  async function recordFeedback(
    item: any, 
    action: FeedbackAction
  ): Promise<void> {
    try {
      // Record feedback to backend
      const response = await apiService.recordFeedback({
        insight: {
          agent_name: item.agentName || 'Unknown Agent',
          category: item.category || 'general',
          title: item.title,
          message: item.message
        },
        action
      });

      // Show temporary feedback message
      const actionEmoji = action === 'clicked' ? '✓' : action === 'dismissed' ? '✕' : '👁';
      setFeedbackMessage(`${actionEmoji} Feedback recorded (${response.category})`);
      setTimeout(() => setFeedbackMessage(null), 2000);
      
      console.log('Feedback recorded:', response);
    } catch (error) {
      console.error('Failed to record feedback:', error);
      // Don't show error to user, fail silently
    }
  }

  // Handle insight acceptance
  async function handleAcceptInsight(item: { 
    action: string; 
    title: string; 
    message: string; 
    agentName?: string;
    category?: string;
  }): Promise<void> {
    // Record positive feedback
    await recordFeedback(item, 'clicked');
    
    // Show user confirmation
    alert(`${item.action} accepted!\n\n${item.title}\n${item.message}`);
  }

  // Handle insight dismissal
  async function handleDismissInsight(item: { 
    title: string; 
    message: string; 
    agentName?: string;
    category?: string;
  }): Promise<void> {
    // Record negative feedback
    await recordFeedback(item, 'dismissed');
  }

  async function handleOnboardingComplete() {
    await refreshOnboardingStatus();
    if (userData && calendarData.length > 0) {
      fetchInsights(selectedScenario);
    }
  }

  // Show loading state while checking onboarding
  if (checkingOnboarding) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white p-6 flex items-center justify-center">
        <LoadingState message="Loading..." />
      </div>
    );
  }

  // Show voice onboarding if not completed
  if (onboardingComplete === false) {
    return <VoiceOnboardingView onComplete={handleOnboardingComplete} />;
  }

  // Show loading state while fetching user data
  if (dataLoading) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white p-6 flex items-center justify-center">
        <LoadingState message="Loading user data..." />
      </div>
    );
  }

  // Show error if data fetch failed
  if (dataError || !userData) {
    return (
      <div className="min-h-screen bg-neutral-950 text-white p-6 flex flex-col gap-6">
        <ErrorBanner message={dataError || 'Failed to load user data'} />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-6 flex flex-col gap-6">
      {/* Feedback Toast Notification */}
      {feedbackMessage && (
        <div className="fixed top-6 right-6 z-50 bg-green-500/90 text-white px-4 py-2 rounded-lg shadow-lg animate-fade-in">
          {feedbackMessage}
        </div>
      )}

      {/* Header */}
      <Header agentStats={agentStats} onRefresh={() => fetchInsights(selectedScenario)} />

      {/* Scenario Selector */}
      <ScenarioSelector
        scenarios={availableScenarios}
        selectedScenario={selectedScenario}
        onScenarioSelect={handleScenarioSelect}
      />

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {activeTab === 'now' && (
          <NowView
            suggestions={suggestions}
            loading={loading}
            error={error}
            scenario={scenario}
            agentStats={agentStats}
            onAccept={handleAcceptInsight}
            onDismiss={handleDismissInsight}
            onRetry={() => fetchInsights(selectedScenario)}
          />
        )}

        {activeTab === 'agenda' && (
          <AgendaView calendar={calendarData} />
        )}

        {activeTab === 'profile' && (
          <ProfileView userData={userData} calendarData={calendarData} />
        )}
      </main>

      {/* Bottom Navigation */}
      <Navigation activeTab={activeTab} onTabChange={setActiveTab} />
    </div>
  );
}

export default App;
