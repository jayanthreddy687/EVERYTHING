import { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Loader2, Sparkles } from 'lucide-react';
import { apiService } from '../../services/api';
import { APP_CONFIG } from '../../constants/config';

interface ConversationMessage {
  role: 'system' | 'user';
  text: string;
  timestamp: string;
}

interface VoiceOnboardingViewProps {
  onComplete: () => void;
}

export function VoiceOnboardingView({ onComplete }: VoiceOnboardingViewProps) {
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [conversation, setConversation] = useState<ConversationMessage[]>([]);
  const [currentSystemMessage, setCurrentSystemMessage] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [preferences, setPreferences] = useState<any>({});
  const [hasStarted, setHasStarted] = useState(false);
  
  const recognitionRef = useRef<any>(null);
  const conversationEndRef = useRef<HTMLDivElement>(null);

  // Speech API setup - browser support is spotty, but works in Chrome/Safari
  useEffect(() => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setError('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onresult = (event: any) => {
      const result = event.results[event.results.length - 1];
      const transcriptText = result[0].transcript;
      
      setTranscript(transcriptText);
      
      if (result.isFinal) {
        handleUserResponse(transcriptText);
      }
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      
      if (event.error === 'no-speech') {
        setError('No speech detected. Click the microphone to try again.');
      } else if (event.error === 'not-allowed') {
        setError('Microphone access denied. Please allow microphone access and refresh.');
      } else {
        setError(`Speech error: ${event.error}`);
      }
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognitionRef.current = recognition;

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      window.speechSynthesis.cancel();
    };
  }, []);

  // Auto-scroll conversation
  useEffect(() => {
    conversationEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [conversation, currentSystemMessage]);

  const startConversation = () => {
    setHasStarted(true);
    setError(null);
    
    // Delay a bit before speaking
    setTimeout(() => {
      speak("Hi! I'm EVERYTHING, your personal AI assistant. Let's get to know each other! What matters most to you these days?");
    }, 300);
  };

  const speak = (text: string) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    setCurrentSystemMessage(text);
    
    utterance.onend = () => {
      // Add to conversation history
      setConversation(prev => [...prev, {
        role: 'system',
        text,
        timestamp: new Date().toISOString()
      }]);
      setCurrentSystemMessage('');
      
      // Start listening after system finishes speaking
      setTimeout(() => {
        startListening();
      }, 500);
    };
    
    window.speechSynthesis.speak(utterance);
  };

  const startListening = () => {
    if (!recognitionRef.current) return;
    
    setError(null);
    setTranscript('');
    setIsListening(true);
    
    try {
      recognitionRef.current.start();
    } catch (error) {
      console.error('Failed to start recognition:', error);
      setIsListening(false);
    }
  };

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  };

  const handleUserResponse = async (userAnswer: string) => {
    if (!userAnswer.trim()) return;
    
    setIsListening(false);
    setIsProcessing(true);
    setTranscript('');
    
    // Add user message to conversation
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
      
      // Update preferences
      if (response.preferences_extracted) {
        setPreferences((prev: any) => ({
          ...prev,
          ...response.preferences_extracted
        }));
      }
      
      setIsProcessing(false);
      
      if (response.is_complete || response.next_question === 'ONBOARDING_COMPLETE') {
        await completeOnboarding(updatedConversation);
      } else {
        // Ask next question
        setTimeout(() => {
          speak(response.next_question);
        }, 800);
      }
    } catch (error) {
      console.error('Failed to process response:', error);
      setError('Failed to process your response. Please try again.');
      setIsProcessing(false);
    }
  };

  const completeOnboarding = async (finalConversation: ConversationMessage[]) => {
    setIsProcessing(true);
    
    try {
      // Build preferences object from conversation
      const onboardingPreferences = {
        name: null as string | null,
        priorities: preferences.priorities || [],
        work_stress_areas: preferences.work_stress || [],
        health_goals: preferences.health_goals || [],
        social_preferences: {
          style: preferences.social_style || 'balanced'
        },
        financial_goals: [] as string[],
        communication_style: 'balanced' as string,
        agent_weights: {} as Record<string, number>,
        raw_conversation: finalConversation
      };
      
      await apiService.saveOnboarding(onboardingPreferences);
      
      const completionMessage = "Perfect! I've got everything I need. EVERYTHING is now personalized just for you. Let me show you your first insights!";
      
      const utterance = new SpeechSynthesisUtterance(completionMessage);
      utterance.rate = 0.95;
      
      utterance.onend = () => {
        setTimeout(() => {
          onComplete();
        }, 2000);
      };
      
      window.speechSynthesis.speak(utterance);
      
      setConversation(prev => [...prev, {
        role: 'system',
        text: completionMessage,
        timestamp: new Date().toISOString()
      }]);
      
    } catch (error) {
      console.error('Failed to save onboarding:', error);
      setError('Failed to save your preferences. Please try again.');
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white p-6 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{APP_CONFIG.APP_NAME}</h1>
        <p className="text-neutral-400 text-sm">{APP_CONFIG.APP_TAGLINE}</p>
      </div>      
      </div>

      {/* Permission Notice */}
      <div className="bg-gray-500/10 border border-gray-400/20 rounded-lg p-4 mb-6">
        <p className="text-sm text-gray-300">
          🎙️ <strong>Microphone Access:</strong> We need your microphone to have a conversation. 
          Your voice data is processed in real-time and never stored.
        </p>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
          <p className="text-sm text-red-200">{error}</p>
        </div>
      )}

      {/* Start Button (shown before conversation starts) */}
      {!hasStarted && (
        <div className="flex-1 flex flex-col items-center justify-center gap-6">
          <div className="text-center max-w-md">
            <div className="mb-6">
              <div className="w-24 h-24 bg-gradient-to-br from-gray-300 via-gray-100 to-gray-400 rounded-full mx-auto flex items-center justify-center mb-4 animate-pulse shadow-lg">
                <Sparkles className="w-12 h-12 text-gray-700" />
              </div>
            </div>
            <h2 className="text-3xl font-bold mb-4 bg-gradient-to-r from-gray-200 via-white to-gray-300 text-transparent bg-clip-text">
              Let's Personalize EVERYTHING
            </h2>
            <p className="text-lg text-neutral-300 mb-8">
              I'll ask you a few questions to understand what matters most to you. 
              Just speak naturally, and I'll listen!
            </p>
            <button
              onClick={startConversation}
              className="px-8 py-4 bg-gradient-to-r from-gray-300 via-gray-100 to-gray-300 hover:from-gray-200 hover:via-white hover:to-gray-200 text-gray-900 rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
            >
                Start Voice Conversation
            </button>
            <p className="text-sm text-neutral-400 mt-4">
              You'll need to grant microphone access
            </p>
          </div>
        </div>
      )}

      {/* Conversation Display (shown after starting) */}
      {hasStarted && (
        <>
          <div className="flex-1 overflow-y-auto mb-6 space-y-4">
            {conversation.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-gray-300 via-gray-100 to-gray-300 text-gray-900'
                      : 'bg-neutral-800 text-neutral-100'
                  }`}
                >
                  <p className="text-sm">{message.text}</p>
                </div>
              </div>
            ))}
            
            {/* Current system message (while speaking) */}
            {currentSystemMessage && (
              <div className="flex justify-start">
                <div className="max-w-[80%] rounded-2xl px-4 py-3 bg-neutral-800 text-neutral-100 animate-pulse">
                  <p className="text-sm">{currentSystemMessage}</p>
                </div>
              </div>
            )}
            
            {/* Processing indicator */}
            {isProcessing && (
              <div className="flex justify-center">
                <div className="bg-neutral-800 rounded-full px-4 py-2 flex items-center gap-2 border border-gray-500/20">
                  <Loader2 className="w-4 h-4 animate-spin text-gray-300" />
                  <span className="text-sm text-neutral-300">Thinking...</span>
                </div>
              </div>
            )}
            
            <div ref={conversationEndRef} />
          </div>

          {/* Voice Input Area */}
          <div className="bg-neutral-900 rounded-2xl p-6 border border-neutral-800">
            {/* Live Transcript */}
            {transcript && (
              <div className="mb-4 p-3 bg-neutral-800 rounded-lg border border-gray-500/20">
                <p className="text-sm text-neutral-300">
                  <span className="text-gray-300 font-semibold">You're saying:</span> {transcript}
                </p>
              </div>
            )}
            
            {/* Microphone Button */}
            <div className="flex flex-col items-center gap-4">
              <button
                onClick={isListening ? stopListening : startListening}
                disabled={isProcessing || !!currentSystemMessage}
                className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all ${
                  isListening
                    ? 'bg-red-500 hover:bg-red-600 scale-110 shadow-lg shadow-red-500/50'
                    : isProcessing || currentSystemMessage
                    ? 'bg-neutral-700 cursor-not-allowed'
                    : 'bg-gradient-to-br from-gray-300 via-gray-100 to-gray-400 hover:from-gray-200 hover:via-white hover:to-gray-300 shadow-lg shadow-gray-400/50'
                }`}
              >
                {isListening && (
                  <div className="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-75"></div>
                )}
                {isListening ? (
                  <Mic className="w-10 h-10 text-white relative z-10" />
                ) : isProcessing || currentSystemMessage ? (
                  <Loader2 className="w-10 h-10 text-neutral-400 animate-spin" />
                ) : (
                  <MicOff className="w-10 h-10 text-gray-700" />
                )}
              </button>
              
              <div className="text-center">
                {isListening ? (
                  <p className="text-sm font-medium text-red-400">Listening... Tap to stop</p>
                ) : isProcessing ? (
                  <p className="text-sm font-medium text-gray-300">Processing your answer...</p>
                ) : currentSystemMessage ? (
                  <p className="text-sm font-medium text-gray-300">AI is speaking...</p>
                ) : (
                  <p className="text-sm font-medium text-neutral-400">Tap to speak</p>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
