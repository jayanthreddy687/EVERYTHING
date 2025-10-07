import { useState, useEffect } from 'react';

interface UseSpeechSynthesisOptions {
  rate?: number;
  pitch?: number;
  volume?: number;
  onEnd?: () => void;
}

export function useSpeechSynthesis({
  rate = 0.95,
  pitch = 1.0,
  volume = 1.0,
  onEnd
}: UseSpeechSynthesisOptions = {}) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [currentText, setCurrentText] = useState('');

  useEffect(() => {
    return () => {
      window.speechSynthesis.cancel();
    };
  }, []);

  function speak(text: string) {
    window.speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = rate;
    utterance.pitch = pitch;
    utterance.volume = volume;

    setCurrentText(text);
    setIsSpeaking(true);

    utterance.onend = () => {
      setIsSpeaking(false);
      setCurrentText('');
      onEnd?.();
    };

    utterance.onerror = () => {
      setIsSpeaking(false);
      setCurrentText('');
    };

    window.speechSynthesis.speak(utterance);
  }

  function cancel() {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
    setCurrentText('');
  }

  return {
    speak,
    cancel,
    isSpeaking,
    currentText
  };
}

