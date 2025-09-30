// Application configuration
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000",
  TIMEOUT: 10000,
  RETRY_ATTEMPTS: 3
} as const;

export const APP_CONFIG = {
  APP_NAME: "EVERYTHING",
  APP_TAGLINE: "AI Agent Intelligence",
  DEFAULT_TAB: "now"
} as const;

export const PRIORITY_COLORS: Record<string, string> = {
  high: "bg-red-900/30 text-red-400 border-red-800/50",
  medium: "bg-yellow-900/30 text-yellow-400 border-yellow-800/50",
  low: "bg-blue-900/30 text-blue-400 border-blue-800/50"
} as const;

export type TabType = 'now' | 'agenda' | 'profile';
