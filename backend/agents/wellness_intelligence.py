"""Wellness Intelligence - Tracks sleep, stress, and health patterns"""
import logging
import json
from typing import List
from .base_agent import BaseAgent
from models import AgentInsight, AnalysisRequest
from services import LLMService

logger = logging.getLogger(__name__)


class WellnessIntelligenceAgent(BaseAgent):
    """AI-powered wellness analysis"""
    
    def __init__(self, llm: LLMService):
        super().__init__(llm, "Wellness Intelligence")
    
    async def analyze(self, request: AnalysisRequest) -> List[AgentInsight]:
        """Analyze sleep, stress, and health patterns"""
        
        logger.info(f"💊 {self.name} starting analysis...")
        
        fitness = request.user_data.get("fitness_data", {})
        sleep = fitness.get("sleep", {})
        workout = fitness.get("last_workout", {})
        screen_time = request.user_data.get("app_usage", {}).get("screen_time", "")
        calendar = request.calendar_events
        
        # Extract fitness/wellness related events from calendar
        fitness_events = [e for e in calendar if any(w in e.get('event', '').lower() 
                         for w in ['run', 'workout', 'gym', 'exercise', 'yoga', 'fitness'])]
        
        sleep_events = [e for e in calendar if any(w in e.get('event', '').lower() 
                       for w in ['drinks', 'pub', 'late', 'party']) and 
                       any(int(e.get('time', '00:00').split(':')[0]) >= 19 for _ in [1])]
        
        # Build wellness insights based on calendar
        calendar_context = []
        if fitness_events:
            next_workout = fitness_events[0]
            calendar_context.append(f"Scheduled workout: {next_workout.get('event')} at {next_workout.get('time')}")
            if workout.get('felt') == 'sluggish':
                calendar_context.append("Recent workout felt sluggish - recovery may be needed")
        
        if sleep_events:
            calendar_context.append(f"Late social event scheduled: {sleep_events[0].get('event')} at {sleep_events[0].get('time')}")
        
        prompt = f"""You are a wellness AI analyzing user health data:

Sleep: {sleep.get('last_night', 'Unknown')} - Quality: {sleep.get('quality', 'Unknown')}
Last Workout: {workout.get('type', 'None')} - Felt: {workout.get('felt', 'N/A')}
Steps Today: {fitness.get('steps_today', 0)}
Screen Time: {screen_time}

Calendar Events (Wellness-Related):
{json.dumps(fitness_events, indent=2) if fitness_events else "No fitness events scheduled"}

Calendar Context:
{chr(10).join('- ' + c for c in calendar_context) if calendar_context else "- No specific wellness concerns from calendar"}

Task: Based on the ACTUAL calendar and fitness data, provide ONE specific wellness suggestion.
- If "morning run" is scheduled but last workout felt "sluggish" → suggest better sleep or recovery
- If sleep quality is "poor" and late events scheduled → suggest digital sunset or earlier bedtime
- If no workouts scheduled but user needs activity → suggest scheduling workout
- If workout scheduled soon → suggest preparation tips (hydration, warm-up)

Be SPECIFIC to the calendar events and actual data.

Format:
TITLE: [Engaging wellness tip]
MESSAGE: [Problem from data + Solution, 2 sentences]
ACTION: [Clear action button text]
PRIORITY: [high/medium/low]
REASONING: [Why this will help based on calendar/data]"""

        logger.debug(f"   Analyzing wellness data: sleep={sleep.get('quality')}, screen_time={screen_time}")
        response = await self.llm.analyze(prompt)
        logger.info(f"✅ {self.name} completed analysis")
        
        insight = self._parse_response(response, "wellness")
        
        if "poor" in sleep.get('quality', '').lower():
            insight.priority = "high"
            logger.info(f"   ⚠️  Elevated to HIGH priority due to poor sleep quality")
        
        return [insight]
    
    def _parse_response(self, llm_response: str, category: str) -> AgentInsight:
        lines = llm_response.strip().split('\n')
        title = "Wellness Insight"
        message = llm_response[:200]
        action = "Improve Wellness"
        reasoning = "AI health analysis"
        priority = "medium"
        
        for line in lines:
            if "TITLE:" in line:
                title = line.split("TITLE:")[-1].strip()
            elif "MESSAGE:" in line:
                message = line.split("MESSAGE:")[-1].strip()
            elif "ACTION:" in line:
                action = line.split("ACTION:")[-1].strip()
            elif "REASONING:" in line:
                reasoning = line.split("REASONING:")[-1].strip()
            elif "PRIORITY:" in line:
                priority = line.split("PRIORITY:")[-1].strip().lower()
        
        return AgentInsight(
            agent_name=self.name,
            title=title,
            message=message,
            action=action,
            category=category,
            priority=priority,
            confidence=0.88,
            reasoning=reasoning
        )