import { Card } from "../../components/ui/card";
import { Button } from "../../components/ui/button";
import type { UserProfile, CalendarEvent } from "../../types";

interface ProfileViewProps {
  userData: UserProfile;
  calendarData: CalendarEvent[];
}

/**
 * ProfileView - Displays user profile and integrations
 */
export function ProfileView({ userData, calendarData }: ProfileViewProps) {
  // Safely access nested properties with fallbacks
  const name = userData.name || 'User';
  const age = userData.age || '';
  const city = userData.location?.home?.address?.split(',')[0] || 'Unknown';
  const occupation = userData.occupation || 'Unknown';

  return (
    <div className="pb-24">
      {/* Main profile card */}
      <Card className="bg-neutral-900 border border-neutral-800 rounded-xl p-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-sm text-neutral-400">
              {name} {age && `• ${age}`}
            </div>
            <div className="text-lg font-semibold">
              {city} • {occupation}
            </div>
          </div>
          <div className="text-right text-sm text-neutral-400">
            <div>Profile Details</div>
          </div>
        </div>
      </Card>

      {/* Stats cards */}
      <div className="mt-4 space-y-3">
        <ActivityCard userData={userData} calendarData={calendarData} />
        <IntegrationsCard userData={userData} />
      </div>
    </div>
  );
}

interface ActivityCardProps {
  userData: UserProfile;
  calendarData: CalendarEvent[];
}

/**
 * ActivityCard - Shows daily activity stats
 */
function ActivityCard({ userData, calendarData }: ActivityCardProps) {
  const steps = userData.fitness_data?.daily_steps || 0;
  
  return (
    <Card className="bg-neutral-900 border border-neutral-800 rounded-xl p-3">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-neutral-300 font-medium">Today's Activity</div>
          <div className="text-xs text-neutral-400">
            Steps: {steps} • Events: {calendarData.length}
          </div>
        </div>
        <div className="text-xs text-neutral-500">
          Active
        </div>
      </div>
    </Card>
  );
}

interface IntegrationsCardProps {
  userData: UserProfile;
}

/**
 * IntegrationsCard - Shows connected integrations
 */
function IntegrationsCard({ userData }: IntegrationsCardProps) {
  const playlistCount = userData.spotify?.playlists?.length || 0;
  const socialPosts = userData.social_media?.twitter?.posts?.length || 0;
  
  return (
    <Card className="bg-neutral-900 border border-neutral-800 rounded-xl p-3">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-sm text-neutral-300 font-medium">Integrations</div>
          <div className="text-xs text-neutral-400">
            Spotify ({playlistCount} playlists) • Calendar • Location • Social ({socialPosts} posts)
          </div>
        </div>
        <Button variant="secondary" className="rounded-xl">Manage</Button>
      </div>
    </Card>
  );
}
