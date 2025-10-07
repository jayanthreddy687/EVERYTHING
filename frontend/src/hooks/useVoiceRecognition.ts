import { useState, useEffect, useRef } from 'react';

interface UseVoiceRecognitionOptions {
  onResult: (transcript: string, isFinal: boolean) => void;
  onError: (error: string) => void;
  language?: string;
  continuous?: boolean;
}

export function useVoiceRecognition({
  onResult,
  onError,
  language = 'en-US',
  continuous = false
}: UseVoiceRecognitionOptions) {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(true);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    const SpeechRecognition = 
      (window as any).SpeechRecognition || 
      (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setIsSupported(false);
      onError('Speech recognition not supported in this browser. Please use Chrome, Edge, or Safari.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = continuous;
    recognition.interimResults = true;
    recognition.lang = language;

    recognition.onresult = (event: any) => {
      const result = event.results[event.results.length - 1];
      const transcript = result[0].transcript;
      onResult(transcript, result.isFinal);
    };

    recognition.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);

      if (event.error === 'no-speech') {
        onError('No speech detected. Click the microphone to try again.');
      } else if (event.error === 'not-allowed') {
        onError('Microphone access denied. Please allow microphone access and refresh.');
      } else {
        onError(`Speech error: ${event.error}`);
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
    };
  }, [language, continuous, onResult, onError]);

  function startListening() {
    if (!recognitionRef.current || !isSupported) return;

    try {
      recognitionRef.current.start();
      setIsListening(true);
    } catch (error) {
      console.error('Failed to start recognition:', error);
      setIsListening(false);
    }
  }

  function stopListening() {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
    setIsListening(false);
  }

  return {
    isListening,
    isSupported,
    startListening,
    stopListening
  };
}

