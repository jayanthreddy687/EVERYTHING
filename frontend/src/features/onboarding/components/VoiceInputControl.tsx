import { Mic, MicOff, Loader2 } from 'lucide-react';

interface VoiceInputControlProps {
  isListening: boolean;
  isProcessing: boolean;
  isSpeaking: boolean;
  transcript: string;
  onToggleListening: () => void;
}

export function VoiceInputControl({
  isListening,
  isProcessing,
  isSpeaking,
  transcript,
  onToggleListening
}: VoiceInputControlProps) {
  const isDisabled = isProcessing || isSpeaking;

  return (
    <div className="bg-neutral-900 rounded-2xl p-6 border border-neutral-800">
      {transcript && (
        <div className="mb-4 p-3 bg-neutral-800 rounded-lg border border-gray-500/20">
          <p className="text-sm text-neutral-300">
            <span className="text-gray-300 font-semibold">You're saying:</span> {transcript}
          </p>
        </div>
      )}
      
      <div className="flex flex-col items-center gap-4">
        <button
          onClick={onToggleListening}
          disabled={isDisabled}
          className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all ${
            isListening
              ? 'bg-red-500 hover:bg-red-600 scale-110 shadow-lg shadow-red-500/50'
              : isDisabled
              ? 'bg-neutral-700 cursor-not-allowed'
              : 'bg-gradient-to-br from-gray-300 via-gray-100 to-gray-400 hover:from-gray-200 hover:via-white hover:to-gray-300 shadow-lg shadow-gray-400/50'
          }`}
        >
          {isListening && (
            <div className="absolute inset-0 rounded-full bg-red-500 animate-ping opacity-75"></div>
          )}
          {isListening ? (
            <Mic className="w-10 h-10 text-white relative z-10" />
          ) : isDisabled ? (
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
          ) : isSpeaking ? (
            <p className="text-sm font-medium text-gray-300">AI is speaking...</p>
          ) : (
            <p className="text-sm font-medium text-neutral-400">Tap to speak</p>
          )}
        </div>
      </div>
    </div>
  );
}

