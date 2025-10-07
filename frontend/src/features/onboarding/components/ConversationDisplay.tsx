import { useEffect, useRef } from 'react';
import { Loader2 } from 'lucide-react';
import type { ConversationMessage } from '../../../types';

interface ConversationDisplayProps {
  messages: ConversationMessage[];
  currentSystemMessage: string;
  isProcessing: boolean;
}

export function ConversationDisplay({ 
  messages, 
  currentSystemMessage, 
  isProcessing 
}: ConversationDisplayProps) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentSystemMessage]);

  return (
    <div className="flex-1 overflow-y-auto mb-6 space-y-4">
      {messages.map((message, index) => (
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
      
      {currentSystemMessage && (
        <div className="flex justify-start">
          <div className="max-w-[80%] rounded-2xl px-4 py-3 bg-neutral-800 text-neutral-100 animate-pulse">
            <p className="text-sm">{currentSystemMessage}</p>
          </div>
        </div>
      )}
      
      {isProcessing && (
        <div className="flex justify-center">
          <div className="bg-neutral-800 rounded-full px-4 py-2 flex items-center gap-2 border border-gray-500/20">
            <Loader2 className="w-4 h-4 animate-spin text-gray-300" />
            <span className="text-sm text-neutral-300">Thinking...</span>
          </div>
        </div>
      )}
      
      <div ref={endRef} />
    </div>
  );
}

