/**
 * Type definitions for the Everything App
 */

// User Profile Types
export interface Location {
  home: {
    city: string;
    country: string;
    coordinates: {
      latitude: number;
      longitude: number;
    };
  };
  work: {
    city: string;
    country: string;
    coordinates: {
      latitude: number;
      longitude: number;
    };
  };
}

export interface SpotifyTrack {
  name: string;
  artist: string;
  album: string;
  duration_ms: number;
}

export interface SpotifyPlaylist {
  name: string;
  tracks: SpotifyTrack[];
}

export interface SpotifyData {
  playlists: SpotifyPlaylist[];
  top_artists?: string[];
  recently_played?: SpotifyTrack[];
}

export interface TwitterPost {
  id: string;
  text: string;
  timestamp: string;
  likes?: number;
  retweets?: number;
}

export interface SocialMediaData {
  twitter?: {
    posts: TwitterPost[];
    followers?: number;
  };
  instagram?: {
    posts: any[];
    followers?: number;
  };
}

export interface Contact {
  name: string;
  relationship: string;
  last_contacted?: string;
  frequency?: string;
}

export interface FitnessData {
  daily_steps?: number;
  weekly_goal?: number;
  activities?: Array<{
    type: string;
    duration: number;
    calories: number;
  }>;
}

export interface UserProfile {
  name: string;
  age?: number;
  occupation?: string;
  profession?: string;
  location: Location;
  spotify: SpotifyData;
  social_media?: SocialMediaData;
  contacts?: Contact[];
  fitness_data?: FitnessData;
  preferences?: {
    music_genres?: string[];
    interests?: string[];
  };
}

// Calendar Types
export interface CalendarEvent {
  id?: string;
  date: string;
  time: string;
  event?: string;
  title?: string;
  duration?: number;
  duration_hours?: number;
  location: string;
  description?: string;
}

// Location Types
export interface LocationPoint {
  name: string;
  latitude: number;
  longitude: number;
  timestamp?: string;
}

export interface CurrentContext {
  location: LocationPoint;
  time: string;
  context_type: string;
}

// AI Insights Types
export type InsightPriority = 'low' | 'medium' | 'high';
export type InsightCategory = 'wellness' | 'productivity' | 'social' | 'financial' | 'content';

export interface Insight {
  id: string;
  title: string;
  message: string;
  action: string;
  priority: InsightPriority;
  category: InsightCategory;
  icon: string;
  timestamp?: string;
}

// Scenario Types
export interface Scenario {
  id: string;
  name: string;
  description: string;
  icon: string;
  triggers: string[];
}

// Agent Stats Types
export interface AgentStats {
  activeAgents: number;
  lastUpdate: string;
  totalInsights: number;
}

// API Request/Response Types
export interface AnalysisRequest {
  user_data: UserProfile;
  calendar_events: CalendarEvent[];
  location_data: LocationPoint[];
  current_context: CurrentContext;
  manual_scenario?: string | null;
}

export interface ScenarioDetection {
  type: string;
  confidence: number;
  triggers: string[];
  description: string;
}

export interface AnalysisResponse {
  insights: Insight[];
  scenario: ScenarioDetection;
  agent_stats: AgentStats;
  timestamp: string;
}

// API Error Types
export interface ApiError {
  message: string;
  status?: number;
  detail?: string;
}

// Feedback Types
export type FeedbackAction = 'clicked' | 'dismissed' | 'ignored';

export interface FeedbackInsightData {
  agent_name: string;
  category: string;
  title: string;
  message: string;
}

export interface FeedbackRequest {
  insight: FeedbackInsightData;
  action: FeedbackAction;
}

export interface FeedbackResponse {
  status: string;
  action: FeedbackAction;
  category: string;
  average_score?: number;
}

// Component Props Types
export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'secondary' | 'ghost' | 'outline';
  size?: 'default' | 'sm' | 'lg';
}

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}
