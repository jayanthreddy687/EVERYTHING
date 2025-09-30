import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { UserProfile, CalendarEvent } from '../types';

interface UseUserDataReturn {
  userData: UserProfile | null;
  calendarData: CalendarEvent[];
  loading: boolean;
  error: string | null;
}

/**
 * Custom hook to fetch user profile and calendar data from backend
 * Replaces hardcoded mock data
 */
export function useUserData(): UseUserDataReturn {
  const [userData, setUserData] = useState<UserProfile | null>(null);
  const [calendarData, setCalendarData] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch user profile and calendar in parallel
        const [userProfile, calendarResponse] = await Promise.all([
          apiService.getUserProfile(),
          apiService.getCalendarEvents(),
        ]);

        setUserData(userProfile);
        setCalendarData(calendarResponse.events || []);
      } catch (err) {
        console.error('Failed to fetch user data:', err);
        setError(err instanceof Error ? err.message : 'Unknown error');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  return {
    userData,
    calendarData,
    loading,
    error,
  };
}
