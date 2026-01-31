import { getApiBaseUrl } from '../constants/config';
import type {
  AnalysisRequest,
  AnalysisResponse,
  CalendarEvent,
  LocationPoint,
  Scenario,
  UserProfile,
  FeedbackRequest,
  FeedbackResponse
} from '../types';

/**
 * API service for backend communication
 */
class ApiService {
  private baseURL: string;

  constructor(baseURL?: string) {
    this.baseURL = baseURL || getApiBaseUrl();
  }

  /**
   * Fetch wrapper with error handling
   */
  private async fetch<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API Error [${endpoint}]:`, error);
      throw error;
    }
  }

  /**
   * Get available scenarios from backend
   */
  async getScenarios(): Promise<{ scenarios: Scenario[] }> {
    return this.fetch('/scenarios');
  }

  /**
   * Analyze user data and get AI insights
   */
  async analyze(analysisRequest: AnalysisRequest): Promise<AnalysisResponse> {
    return this.fetch('/analyze', {
      method: 'POST',
      body: JSON.stringify(analysisRequest),
    });
  }

  /**
   * Get user profile data from backend
   */
  async getUserProfile(): Promise<UserProfile> {
    return this.fetch('/user');
  }

  /**
   * Get calendar events from backend
   */
  async getCalendarEvents(): Promise<{ events: CalendarEvent[] }> {
    return this.fetch('/calendar');
  }

  /**
   * Get current location from backend
   */
  async getCurrentLocation(): Promise<LocationPoint> {
    return this.fetch('/location/current');
  }

  /**
   * Get location history from backend
   */
  async getLocationHistory(): Promise<{ locations: LocationPoint[] }> {
    return this.fetch('/location/history');
  }

  /**
   * Record user feedback on an insight
   */
  async recordFeedback(feedbackRequest: FeedbackRequest): Promise<FeedbackResponse> {
    return this.fetch('/feedback', {
      method: 'POST',
      body: JSON.stringify(feedbackRequest),
    });
  }

  /**
   * Get feedback statistics from backend
   */
  async getFeedbackStats(): Promise<{ status: string; feedback_count: number; message: string }> {
    return this.fetch('/feedback/stats');
  }

  /**
   * Check onboarding status
   */
  async getOnboardingStatus(): Promise<{ completed: boolean; preferences: any | null }> {
    return this.fetch('/onboarding/status');
  }

  /**
   * Send voice onboarding step
   */
  async voiceOnboardingStep(request: {
    conversation_history: Array<{ role: string; text: string; timestamp: string }>;
    current_answer: string;
  }): Promise<{
    next_question: string;
    analysis: string;
    preferences_extracted: any;
    is_complete: boolean;
  }> {
    return this.fetch('/onboarding/voice-step', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Save onboarding preferences
   */
  async saveOnboarding(preferences: any): Promise<{ status: string; preferences: any; message: string }> {
    return this.fetch('/onboarding/save', {
      method: 'POST',
      body: JSON.stringify(preferences),
    });
  }

  /**
   * Reset onboarding (for testing)
   */
  async resetOnboarding(): Promise<{ status: string; message: string }> {
    return this.fetch('/onboarding/reset', {
      method: 'POST',
    });
  }

  /**
   * Build analysis request payload
   */
  buildAnalysisRequest(
    userData: UserProfile,
    calendarData: CalendarEvent[],
    selectedScenario: string | null = null
  ): AnalysisRequest {
    return {
      user_data: userData,
      calendar_events: calendarData.map(event => ({
        date: event.date,
        time: event.time,
        event: event.title || event.event,
        duration_hours: event.duration || event.duration_hours,
        location: event.location
      })),
      location_data: [
        {
          timestamp: new Date().toISOString(),
          latitude: userData.location.home.coordinates.latitude,
          longitude: userData.location.home.coordinates.longitude,
          name: "Home"
        }
      ],
      current_context: {
        location: {
          name: "Home",
          latitude: userData.location.home.coordinates.latitude,
          longitude: userData.location.home.coordinates.longitude
        },
        time: new Date().toISOString(),
        context_type: "morning_routine"
      },
      manual_scenario: selectedScenario
    };
  }
}

export const apiService = new ApiService();
