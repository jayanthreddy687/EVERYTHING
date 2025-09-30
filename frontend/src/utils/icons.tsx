import { Bell, Calendar, Music, Moon, Zap, Users, Brain, Sparkles } from "lucide-react";
import type { InsightCategory } from '../types';

/**
 * Get the appropriate icon component for a given category
 */
export function getIconForCategory(category: InsightCategory | string): React.JSX.Element {
  const iconMap: Record<string, React.JSX.Element> = {
    'music': <Music className='w-6 h-6 text-green-400'/>,
    'content': <Music className='w-6 h-6 text-green-400'/>,
    'calendar': <Calendar className='w-6 h-6 text-indigo-400'/>,
    'wellness': <Moon className='w-6 h-6 text-purple-400'/>,
    'productivity': <Zap className='w-6 h-6 text-blue-400'/>,
    'social': <Users className='w-6 h-6 text-pink-400'/>,
    'financial': <Sparkles className='w-6 h-6 text-yellow-400'/>,
    'ai': <Sparkles className='w-6 h-6 text-cyan-400'/>,
    'context': <Brain className='w-6 h-6 text-teal-400'/>,
    'general': <Bell className='w-6 h-6 text-gray-400'/>
  };
  return iconMap[category] || iconMap['general'];
}
