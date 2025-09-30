"""
Social Intelligence Agent - AI-powered social context and relationship management
EXACT copy from original backend/main.py lines 445-550
"""
import logging
import json
from typing import List
from .base_agent import BaseAgent
from models import AgentInsight, AnalysisRequest
from services import LLMService

logger = logging.getLogger(__name__)


class SocialIntelligenceAgent(BaseAgent):
    """AI-powered social context and relationship management"""
    
    def __init__(self, llm: LLMService):
        super().__init__(llm, "Social Intelligence")
    
    async def analyze(self, request: AnalysisRequest) -> List[AgentInsight]:
        """Analyze social patterns and suggest connections"""
        
        calendar = request.calendar_events
        contacts = request.user_data.get("contacts", [])
        fitness = request.user_data.get("fitness_data", {})
        current_context = request.current_context
        
        # Extract all social-related events from calendar
        social_events = [e for e in calendar if any(w in e.get('event', '').lower() 
                         for w in ['drinks', 'pub', 'quiz', 'market', 'lunch', 'dinner', 'mates', 'friends', 'social'])]
        
        # Extract fitness events that could be social
        fitness_events = [e for e in calendar if any(w in e.get('event', '').lower() 
                         for w in ['run', 'workout', 'gym', 'exercise'])]
        
        # Get next upcoming event
        next_event = calendar[0] if calendar else {}
        
        # Build dynamic context based on actual calendar
        context_points = []
        if fitness_events:
            context_points.append(f"Upcoming fitness: {fitness_events[0].get('event')} at {fitness_events[0].get('time')}")
            if contacts:
                runner_contacts = [c for c in contacts if 'runner' in c.get('email', '').lower()]
                if runner_contacts:
                    context_points.append(f"Runner contact available: {runner_contacts[0].get('name')}")
        
        if social_events:
            context_points.append(f"Social event scheduled: {social_events[0].get('event')} at {social_events[0].get('time')}")
        
        if not context_points:
            context_points.append("No specific social events scheduled")
        
        prompt = f"""You are a social intelligence AI.

ALL Calendar Events:
{json.dumps(calendar[:5], indent=2)}

Social Events Identified:
{json.dumps(social_events, indent=2) if social_events else "None scheduled"}

Fitness Events (Potential Social):
{json.dumps(fitness_events, indent=2) if fitness_events else "None scheduled"}

User's Contacts:
{json.dumps(contacts, indent=2)}

Current Context:
{chr(10).join('- ' + p for p in context_points)}

Task: Based on the ACTUAL calendar events above, suggest ONE relevant social connection or opportunity.
- If there's a "pub quiz" → suggest inviting Tom Walsh or going together
- If there's a "morning run" → suggest connecting with Mike Chen (runner contact)
- If there's a "farmers market" → suggest social outing or meeting friends there
- If there's "drinks with mates" → suggest venue recommendations or who to invite

Be SPECIFIC to the calendar events. Don't make generic suggestions.

Format:
TITLE: [Social insight based on calendar]
MESSAGE: [Specific opportunity from calendar + Benefit, 2 sentences]
ACTION: [Concrete action related to calendar event]
PRIORITY: [high/medium/low]
REASONING: [Why this matches the calendar]"""

        response = await self.llm.analyze(prompt)
        return [self._parse_response(response, "social")]
    
    def _parse_response(self, llm_response: str, category: str) -> AgentInsight:
        lines = llm_response.strip().split('\n')
        title = "Social Opportunity"
        message = llm_response[:200]
        action = "Connect"
        reasoning = "AI social analysis"
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
            confidence=0.82,
            reasoning=reasoning
        )