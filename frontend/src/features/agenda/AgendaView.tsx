import { useMemo } from "react";
import { motion } from "framer-motion";
import { Card } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import { groupEventsByDate, formatDateTime } from "../../utils/formatters";
import type { CalendarEvent } from "../../types";

interface AgendaViewProps {
  calendar: CalendarEvent[];
}

/**
 * AgendaView - Displays calendar events grouped by date
 */
export function AgendaView({ calendar }: AgendaViewProps) {
  const groupedEvents = useMemo(() => groupEventsByDate(calendar), [calendar]);

  return (
    <div className="flex flex-col gap-4 pb-24">
      {Object.entries(groupedEvents).map(([date, events]) => (
        <DaySection key={date} date={date} events={events} />
      ))}
    </div>
  );
}

interface DaySectionProps {
  date: string;
  events: CalendarEvent[];
}

/**
 * DaySection - Displays events for a single day
 */
function DaySection({ date, events }: DaySectionProps) {
  return (
    <div>
      <h4 className="text-sm text-neutral-400 mb-2">{date}</h4>
      <div className="flex flex-col gap-3">
        {events.map((event, index) => (
          <EventCard key={index} event={event} index={index} />
        ))}
      </div>
    </div>
  );
}

interface EventCardProps {
  event: CalendarEvent;
  index: number;
}

/**
 * EventCard - Displays a single calendar event
 */
function EventCard({ event, index }: EventCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, x: -10 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.05 }}
    >
      <Card className="bg-neutral-900 border border-neutral-800 rounded-xl p-3">
        <div className="flex justify-between items-start gap-4">
          <div>
            <div className="text-sm text-neutral-300 font-medium">
              {formatDateTime(event.date, event.time)}
            </div>
            <div className="text-base font-semibold">{event.title || event.event}</div>
            <div className="text-xs text-neutral-500">
              {event.location} • {event.duration || event.duration_hours}h
            </div>
          </div>
          <div className="flex flex-col items-end gap-2">
            <Button variant="ghost" className="text-xs">AI Notes</Button>
            <Button variant="secondary" className="rounded-xl text-xs">Open</Button>
          </div>
        </div>
      </Card>
    </motion.div>
  );
}
