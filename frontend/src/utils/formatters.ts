import type { CalendarEvent } from '../types';

/**
 * Format date and time into a readable string
 */
export function formatDateTime(date: string, time: string): string {
  return `${date} ${time}`;
}

/**
 * Group calendar events by date
 */
export function groupEventsByDate(calendar: CalendarEvent[]): Record<string, CalendarEvent[]> {
  return calendar.reduce((acc, event) => {
    if (!acc[event.date]) {
      acc[event.date] = [];
    }
    acc[event.date].push(event);
    return acc;
  }, {} as Record<string, CalendarEvent[]>);
}
