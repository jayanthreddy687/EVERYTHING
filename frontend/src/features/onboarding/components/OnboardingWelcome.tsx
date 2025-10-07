import { Sparkles } from 'lucide-react';

interface OnboardingWelcomeProps {
  onStart: () => void;
}

export function OnboardingWelcome({ onStart }: OnboardingWelcomeProps) {
  return (
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
          onClick={onStart}
          className="px-8 py-4 bg-gradient-to-r from-gray-300 via-gray-100 to-gray-300 hover:from-gray-200 hover:via-white hover:to-gray-200 text-gray-900 rounded-full font-semibold text-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-105"
        >
          Start Voice Conversation
        </button>
        <p className="text-sm text-neutral-400 mt-4">
          You'll need to grant microphone access
        </p>
      </div>
    </div>
  );
}

