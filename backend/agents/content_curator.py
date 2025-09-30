"""Content Curator - Picks the right music for the moment"""
import logging
import json
from typing import List
from .base_agent import BaseAgent
from models import AgentInsight, AnalysisRequest
from services import LLMService

logger = logging.getLogger(__name__)


class ContentCurationAgent(BaseAgent):
    """AI-powered music and content recommendations"""
    
    def __init__(self, llm: LLMService):
        super().__init__(llm, "Content Curator")
    
    async def analyze(self, request: AnalysisRequest) -> List[AgentInsight]:
        """Curate music and content based on context"""
        
        spotify = request.user_data.get("spotify", {})
        playlists = spotify.get("playlists", [])
        current_context = request.current_context
        upcoming_events = request.calendar_events[:3]
        
        # Detect scenario for better recommendations
        next_event = upcoming_events[0] if upcoming_events else {}
        next_event_title = next_event.get('event', '').lower()
        
        # PRIORITY 1: Check manual scenario first!
        manual_scenario = request.manual_scenario
        print(f"🎵 Content Curator - Manual Scenario: {manual_scenario}")  # DEBUG
        
        # PRIORITY 2: Auto-detect from events
        is_commuting = any(w in next_event_title for w in ['standup', 'office', 'work', 'meeting'])
        is_deep_work = any(w in next_event_title for w in ['deep work', 'feature', 'coding', 'dev'])
        is_social = any(w in next_event_title for w in ['drinks', 'pub', 'quiz'])
        
        # Handle manual scenario overrides (using correct IDs from /scenarios endpoint)
        if manual_scenario == "before_sleep":
            # Sleep mode - recommend calming late night music
            late_night_playlists = [p for p in playlists if 'late night' in p.get('name', '').lower() or 'night' in p.get('name', '').lower()]
            best_playlist = late_night_playlists[0] if late_night_playlists else (playlists[-1] if playlists else {})
            prompt = f"""You are a sleep music AI. User is winding down for sleep.

User's Playlists:
{json.dumps(playlists, indent=2)}

Best Match for Sleep: {json.dumps(best_playlist, indent=2)}

Task: Recommend the BEST calming playlist for sleep/relaxation.
Prefer "Late Night" or similar calming playlists.
Use ONLY tracks from the playlist data above. Mention 2-3 actual track names.

Format:
TITLE: [Best calming playlist name from above]
MESSAGE: [Why perfect for winding down. Mention 2-3 actual calming tracks from that playlist]
ACTION: Play [Playlist Name]
REASONING: [Sleep/relaxation match]"""
        
        elif manual_scenario == "weekend":
            # Weekend mode - check calendar for specific activities
            weekend_events = [e for e in upcoming_events if any(w in e.get('event', '').lower() 
                             for w in ['weekend', 'market', 'brunch', 'park', 'social', 'friends', 'pub', 'quiz'])]
            
            # Detect weekend activity type
            has_market = any('market' in e.get('event', '').lower() for e in weekend_events)
            has_social = any(w in str(weekend_events).lower() for w in ['pub', 'quiz', 'drinks', 'friends'])
            has_outdoor = any(w in str(weekend_events).lower() for w in ['park', 'run', 'walk', 'market'])
            
            # Choose playlist based on activity
            if has_market or has_outdoor:
                # Upbeat for outdoor activities
                best_playlist = [p for p in playlists if 'commute' in p.get('name', '').lower()]
                best_playlist = best_playlist[0] if best_playlist else playlists[0] if playlists else {}
                activity_context = f"outdoor activity (farmers market/park)"
            elif has_social:
                # Late night vibes for social
                best_playlist = [p for p in playlists if 'late' in p.get('name', '').lower()]
                best_playlist = best_playlist[0] if best_playlist else playlists[-1] if playlists else {}
                activity_context = f"social time (pub quiz/drinks)"
            else:
                # Default relaxing
                best_playlist = [p for p in playlists if 'late' in p.get('name', '').lower()]
                best_playlist = best_playlist[0] if best_playlist else playlists[-1] if playlists else {}
                activity_context = f"relaxing at home"
            
            prompt = f"""You are a weekend music AI. User is enjoying the weekend.

User's Playlists:
{json.dumps(playlists, indent=2)}

Weekend Calendar Events:
{json.dumps(weekend_events, indent=2) if weekend_events else "No specific events"}

Best Match: {json.dumps(best_playlist, indent=2)}

Detected Activity: {activity_context}

Task: Recommend the BEST playlist for this weekend activity.
- If outdoor/market activity → suggest upbeat playlist (like "Commute")
- If social/pub → suggest atmospheric playlist (like "Late Night")
- If no events → suggest relaxing playlist

Use ONLY tracks from the playlist data above. Mention 2-3 actual track names.

Format:
TITLE: [Best playlist name from above matching the activity]
MESSAGE: [Why perfect for THIS weekend activity. Mention 2-3 actual tracks from that playlist]
ACTION: Play [Playlist Name]
REASONING: [Match between music and weekend activity]"""
        
        elif manual_scenario == "commuting_to_work" or (is_commuting and not manual_scenario):
            # Commute-specific recommendation
            commute_playlists = [p for p in playlists if 'commute' in p.get('name', '').lower()]
            best_playlist = commute_playlists[0] if commute_playlists else playlists[0] if playlists else {}
            prompt = f"""You are a music AI for commuters. User is traveling to work.

User's Playlists:
{json.dumps(playlists, indent=2)}

Best Match: {json.dumps(best_playlist, indent=2)}

Next Event: {next_event.get('event')} at {next_event.get('time')}

Task: Recommend the "Commute" playlist with specific tracks from it.
Use ONLY tracks from the playlist data above. Mention 2-3 actual track names.

Format:
TITLE: [Playlist name from above]
MESSAGE: [Why perfect for commuting. Mention 2-3 actual tracks from that playlist]
ACTION: Play Commute Mix
REASONING: [Match between music and travel context]"""
        
        elif manual_scenario == "at_work":
            # Office/work mode - check if deep work
            focus_playlists = [p for p in playlists if 'focus' in p.get('name', '').lower()]
            best_playlist = focus_playlists[0] if focus_playlists else playlists[1] if len(playlists) > 1 else {}
            prompt = f"""You are a music AI for office work. User is at work.

User's Playlists:
{json.dumps(playlists, indent=2)}

Best Match: {json.dumps(best_playlist, indent=2)}

Task: Recommend the "Focus" playlist for concentration.
Use ONLY tracks from the playlist data above. Mention 2-3 actual track names.

Format:
TITLE: [Focus playlist name from above]
MESSAGE: [Why perfect for work focus. Mention 2-3 actual tracks from that playlist]
ACTION: Play Focus Mix
REASONING: [Concentration and productivity match]"""
        
        elif manual_scenario == "workout_time":
            # Workout mode - energetic music
            workout_playlists = [p for p in playlists if 'workout' in p.get('name', '').lower() or 'commute' in p.get('name', '').lower()]
            best_playlist = workout_playlists[0] if workout_playlists else playlists[0] if playlists else {}
            prompt = f"""You are a workout music AI. User is exercising.

User's Playlists:
{json.dumps(playlists, indent=2)}

Best Match: {json.dumps(best_playlist, indent=2)}

Task: Recommend the BEST energetic playlist for workout.
Use ONLY tracks from the playlist data above. Mention 2-3 actual upbeat track names.

Format:
TITLE: [Best workout playlist name from above]
MESSAGE: [Why perfect for workout energy. Mention 2-3 actual tracks from that playlist]
ACTION: Play [Playlist Name]
REASONING: [Workout energy match]"""
        
        elif manual_scenario == "social_evening":
            # Social mode - late night vibes
            social_playlists = [p for p in playlists if 'late' in p.get('name', '').lower() or 'night' in p.get('name', '').lower()]
            best_playlist = social_playlists[0] if social_playlists else playlists[-1] if playlists else {}
            prompt = f"""You are a social music AI. User is out with friends.

User's Playlists:
{json.dumps(playlists, indent=2)}

Best Match: {json.dumps(best_playlist, indent=2)}

Task: Recommend the BEST playlist for social evening vibes.
Use ONLY tracks from the playlist data above. Mention 2-3 actual track names.

Format:
TITLE: [Best social playlist name from above]
MESSAGE: [Why perfect for social time. Mention 2-3 actual tracks from that playlist]
ACTION: Play [Playlist Name]
REASONING: [Social atmosphere match]"""
        
        elif manual_scenario == "lunch_time":
            # Lunch - light background music
            lunch_playlists = [p for p in playlists if 'focus' in p.get('name', '').lower() or 'late' in p.get('name', '').lower()]
            best_playlist = lunch_playlists[0] if lunch_playlists else playlists[1] if len(playlists) > 1 else {}
            prompt = f"""You are a lunch time music AI. User is having lunch.

User's Playlists:
{json.dumps(playlists, indent=2)}

Best Match: {json.dumps(best_playlist, indent=2)}

Task: Recommend light background music for lunch break.
Use ONLY tracks from the playlist data above. Mention 2-3 actual track names.

Format:
TITLE: [Best lunch playlist name from above]
MESSAGE: [Why perfect for lunch break. Mention 2-3 actual tracks from that playlist]
ACTION: Play [Playlist Name]
REASONING: [Lunch break atmosphere]"""
        
        elif manual_scenario == "shopping":
            # Shopping - upbeat background music
            shopping_playlists = [p for p in playlists if 'commute' in p.get('name', '').lower()]
            best_playlist = shopping_playlists[0] if shopping_playlists else playlists[0] if playlists else {}
            prompt = f"""You are a shopping music AI. User is shopping.

User's Playlists:
{json.dumps(playlists, indent=2)}

Best Match: {json.dumps(best_playlist, indent=2)}

Task: Recommend upbeat background music for shopping.
Use ONLY tracks from the playlist data above. Mention 2-3 actual track names.

Format:
TITLE: [Best shopping playlist name from above]
MESSAGE: [Why perfect for shopping. Mention 2-3 actual tracks from that playlist]
ACTION: Play [Playlist Name]
REASONING: [Shopping atmosphere]"""
        
        elif is_deep_work and not manual_scenario:
            # Focus music recommendation
            focus_playlists = [p for p in playlists if 'focus' in p.get('name', '').lower()]
            prompt = f"""You are a music AI for deep work. User needs focus music.

User's Playlists:
{json.dumps(playlists, indent=2)}

Best Match: {json.dumps(focus_playlists[0] if focus_playlists else {}, indent=2)}

Task: Recommend the "Focus" playlist using actual tracks from the playlist data above.
Mention 2-3 specific track names that are in the playlist.

Format:
TITLE: [Actual playlist name from above]
MESSAGE: [Why this helps concentration. Mention actual tracks from the playlist]
ACTION: Play Focus Mix
REASONING: [How music supports deep work]"""
        
        else:
            # General recommendation - pick best playlist for context
            prompt = f"""You are a content curation AI.

User's Available Playlists:
{json.dumps(playlists, indent=2)}

Current Context: {current_context.get('context_type', 'unknown')}
Time: {current_context.get('time', '')}
Next Activity: {next_event.get('event', 'None')}

Task: Pick the BEST playlist from above for this moment.
Use the actual playlist name and tracks from the data above.
Mention 2-3 specific tracks that are in that playlist.

Guidelines:
- Morning/Commute → "Commute" playlist
- Work/Focus → "Focus" playlist  
- Evening/Night → "Late Night" playlist
- Weekend/Relax → Pick most relaxing playlist

Format:
TITLE: [Exact playlist name from above]
MESSAGE: [Why perfect now. Mention 2-3 actual track names from that playlist]
ACTION: Play [Playlist Name]
REASONING: [Context match]"""

        response = await self.llm.analyze(prompt, max_tokens=200)
        return [self._parse_response(response, "music")]
    
    def _parse_response(self, llm_response: str, category: str) -> AgentInsight:
        lines = llm_response.strip().split('\n')
        title = "Perfect Playlist"
        message = llm_response[:150]
        action = "Play Now"
        reasoning = "AI music curation"
        
        for line in lines:
            if "TITLE:" in line:
                title = line.split("TITLE:")[-1].strip()
            elif "MESSAGE:" in line:
                message = line.split("MESSAGE:")[-1].strip()
            elif "ACTION:" in line:
                action = line.split("ACTION:")[-1].strip()
            elif "REASONING:" in line:
                reasoning = line.split("REASONING:")[-1].strip()
        
        return AgentInsight(
            agent_name=self.name,
            title=title,
            message=message,
            action=action,
            category=category,
            priority="medium",
            confidence=0.84,
            reasoning=reasoning
        )