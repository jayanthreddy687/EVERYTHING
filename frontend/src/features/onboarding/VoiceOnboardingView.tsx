import { useState } from 'react';
import { APP_CONFIG } from '../../constants/config';
import { apiService } from '../../services/api';
import { useVoiceRecognition } from '../../hooks/useVoiceRecognition';
import { useSpeechSynthesis } from '../../hooks/useSpeechSynthesis';
import { OnboardingWelcome } from './components/OnboardingWelcome';
import { ConversationDisplay } from './components/ConversationDisplay';
import { VoiceInputControl } from './components/VoiceInputControl';
import type { ConversationMessage, OnboardingPreferences } from '../../types';

interface VoiceOnboardingViewProps {
  onComplete: () => void;
}

export function VoiceOnboardingView({ onComplete }: VoiceOnboardingViewProps) {
  const [hasStarted, setHasStarted] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [conversation, setConversation] = useState<ConversationMessage[]>([]);
  const [preferences, setPreferences] = useState<any>({});
  const [isProcessing, setIsProcessing] = useState(false);

  function addSystemMessage(text: string) {
    setConversation(prev => [...prev, {
      role: 'system',
      text,
      timestamp: new Date().toISOString()
    }]);
  }

  const { speak, isSpeaking, currentText } = useSpeechSynthesis({
    onEnd: () => {
      if (currentText) {
        addSystemMessage(currentText);
      }
      setTimeout(() => {
        startListening();
      }, 500);
    }
  });

  const { isListening, startListening, stopListening } = useVoiceRecognition({
    onResult: (text, isFinal) => {
      setTranscript(text);
      if (isFinal) {
        handleUserResponse(text);
      }
    },
    onError: (errorMessage) => {
      setError(errorMessage);
    }
  });

  function handleStartConversation() {
    setHasStarted(true);
    setError(null);
    
    setTimeout(() => {
      speak("Hi! I'm EVERYTHING, your personal AI assistant. Let's get to know each other! What matters most to you these days?");
    }, 300);
  }

  async function handleUserResponse(userAnswer: string) {
    if (!userAnswer.trim()) return;

    setTranscript('');
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

      if (response.is_complete || response.next_question === 'ONBOARDING_COMPLETE') {
        await handleComplete(updatedConversation);
      } else {
        setTimeout(() => {
          speak(response.next_question);
        }, 800);
      }
    } catch (error) {
      console.error('Failed to process response:', error);
      setError('Failed to process your response. Please try again.');
      setIsProcessing(false);
    }
  }

  async function handleComplete(finalConversation: ConversationMessage[]) {
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
      raw_conversation: finalConversation
    };

    try {
      await apiService.saveOnboarding(onboardingPreferences);
      
      const completionMessage = "Perfect! I've got everything I need. EVERYTHING is now personalized just for you. Let me show you your first insights!";
      
      addSystemMessage(completionMessage);
      
      const utterance = new SpeechSynthesisUtterance(completionMessage);
      utterance.rate = 0.95;
      
      utterance.onend = () => {
        setTimeout(() => {
          onComplete();
        }, 1500);
      };
      
      window.speechSynthesis.speak(utterance);
      
    } catch (error) {
      console.error('Failed to save onboarding:', error);
      setError('Failed to save your preferences. Please try again.');
      setIsProcessing(false);
    }
  }

  function handleToggleListening() {
    if (isListening) {
      stopListening();
    } else {
      setError(null);
      startListening();
    }
  }

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-6 flex flex-col">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{APP_CONFIG.APP_NAME}</h1>
          <p className="text-neutral-400 text-sm">{APP_CONFIG.APP_TAGLINE}</p>
        </div>
      </div>

      <div className="bg-gray-500/10 border border-gray-400/20 rounded-lg p-4 mb-6">
        <p className="text-sm text-gray-300">
          🎙️ <strong>Microphone Access:</strong> We need your microphone to have a conversation. 
          Your voice data is processed in real-time and never stored.
        </p>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
          <p className="text-sm text-red-200">{error}</p>
        </div>
      )}

      {!hasStarted ? (
        <OnboardingWelcome onStart={handleStartConversation} />
      ) : (
        <>
          <ConversationDisplay
            messages={conversation}
            currentSystemMessage={currentText}
            isProcessing={isProcessing}
          />
          <VoiceInputControl
            isListening={isListening}
            isProcessing={isProcessing}
            isSpeaking={isSpeaking}
            transcript={transcript}
            onToggleListening={handleToggleListening}
          />
        </>
      )}
    </div>
  );
}
