import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { ConversationMessage, OnboardingPreferences } from '../types';

export function useOnboarding() {
  const [isComplete, setIsComplete] = useState<boolean | null>(null);
  const [isChecking, setIsChecking] = useState(true);
  const [conversation, setConversation] = useState<ConversationMessage[]>([]);
  const [preferences, setPreferences] = useState<any>({});
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    checkOnboardingStatus();
  }, []);

  async function checkOnboardingStatus() {
    try {
      const status = await apiService.getOnboardingStatus();
      setIsComplete(status.completed);
    } catch (error) {
      console.error('Failed to check onboarding status:', error);
      setIsComplete(true);
    } finally {
      setIsChecking(false);
    }
  }

  async function processUserResponse(userAnswer: string) {
    if (!userAnswer.trim()) return null;

    setIsProcessing(true);

    const userMessage: ConversationMessage = {
      role: 'user',
      text: userAnswer,
      timestamp: new Date().toISOString()
    };

    const updatedConversation = [...conversation, userMessage];
    setConversation(updatedConversation);

    try {
      const response = await apiService.voiceOnboardingStep({
        conversation_history: updatedConversation,
        current_answer: userAnswer
      });

      if (response.preferences_extracted) {
        setPreferences((prev: any) => ({
          ...prev,
          ...response.preferences_extracted
        }));
      }

      setIsProcessing(false);
      return response;
    } catch (error) {
      console.error('Failed to process response:', error);
      setIsProcessing(false);
      throw error;
    }
  }

  async function completeOnboarding() {
    setIsProcessing(true);

    const onboardingPreferences: OnboardingPreferences = {
      name: null,
      priorities: preferences.priorities || [],
      work_stress_areas: preferences.work_stress || [],
      health_goals: preferences.health_goals || [],
      social_preferences: {
        style: preferences.social_style || 'balanced'
      },
      financial_goals: [],
      communication_style: 'balanced',
      agent_weights: {},
      raw_conversation: conversation
    };

    try {
      await apiService.saveOnboarding(onboardingPreferences);
      setIsComplete(true);
      setIsProcessing(false);
    } catch (error) {
      console.error('Failed to save onboarding:', error);
      setIsProcessing(false);
      throw error;
    }
  }

  function addSystemMessage(text: string) {
    setConversation(prev => [...prev, {
      role: 'system',
      text,
      timestamp: new Date().toISOString()
    }]);
  }

  return {
    isComplete,
    isChecking,
    conversation,
    preferences,
    isProcessing,
    processUserResponse,
    completeOnboarding,
    addSystemMessage,
    refreshStatus: checkOnboardingStatus
  };
}

