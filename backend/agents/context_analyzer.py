"""Context Analyzer Agent - Figures out what you're doing based on location, time, and calendar"""
import logging
import json
from typing import List
from .base_agent import BaseAgent
from models import AgentInsight, AnalysisRequest
from services import LLMService

logger = logging.getLogger(__name__)


class ContextAnalyzerAgent(BaseAgent):
    """Understands where user is and what they're doing using AI"""
    
    def __init__(self, llm: LLMService, rag_service=None):
        super().__init__(llm, "Context Analyzer")
        self.rag = rag_service  # Optional RAG service for contextual memory
    
    async def analyze(self, request: AnalysisRequest) -> List[AgentInsight]:
        """Use LLM to understand user's current context"""
        
        logger.info(f"🔍 {self.name} starting analysis...")
        
        current_loc = request.current_context.get("location", {})
        current_time = request.current_context.get("time", "")
        upcoming_events = [e for e in request.calendar_events[:3]]
        user_data = request.user_data
        
        # Check if this is a commuting scenario
        home_coords = user_data.get("location", {}).get("home", {}).get("coordinates", {})
        work_coords = user_data.get("location", {}).get("work", {}).get("coordinates", {})
        
        next_event = upcoming_events[0] if upcoming_events else None
        is_work_commute = (next_event and 
                          any(w in next_event.get('event', '').lower() 
                              for w in ['standup', 'meeting', 'work', 'office', 'review']))
        
        # RAG: Retrieve similar past events if available
        similar_events = []
        if self.rag and next_event:
            # Build semantic query based on current situation
            query = f"Going to {next_event.get('location', 'work')} for {next_event.get('event', 'meeting')}"
            
            # Try feedback-enhanced retrieval first (learns from user interactions)
            try:
                similar_events = self.rag.retrieve_similar_events_with_feedback(query, category="context", top_k=3)
            except:
                # Fallback to standard retrieval if feedback-enhanced fails
                similar_events = self.rag.retrieve_similar_events(query, top_k=3)
            
            if similar_events:
                logger.info(f"   📚 RAG: Retrieved {len(similar_events)} similar past events")
        
        if is_work_commute:
            # Specialized prompt for commuting scenario
            # Add RAG context if available
            rag_context = ""
            if similar_events:
                rag_context = f"""
Similar Past Commutes:
{json.dumps(similar_events, indent=2)}
"""
            
            prompt = f"""You are a commute planning AI. User is about to travel to work.

HOME: {home_coords.get('latitude')}, {home_coords.get('longitude')}
WORK: {work_coords.get('latitude')}, {work_coords.get('longitude')}
Next Event: {next_event.get('event')} at {next_event.get('time')} - {next_event.get('location')}
Current Time: {current_time}
{rag_context}
Task: Provide travel advice for their commute to work.
Consider:
- Best route options (Tube, Bus, Walk, Cycle)
- Estimated travel time (typically 20-35 min for London Shoreditch commute)
- Traffic/transport conditions at this time
- When they should leave to arrive on time
{f"- Past patterns from similar commutes above" if similar_events else ""}

Format:
TITLE: [Commute planning title]
MESSAGE: [Travel options and timing, 2 sentences max. Mention specific routes like 'Northern Line' or 'Bus 55']
ACTION: [Button text like 'View Routes' or 'Check Traffic']
PRIORITY: high
REASONING: [Why this route/timing is best now]"""
        else:
            # General context analysis
            # Add RAG context if available
            rag_context = ""
            if similar_events:
                rag_context = f"""
Similar Past Situations:
{json.dumps(similar_events, indent=2)}
"""
            
            prompt = f"""You are a context analysis AI. Analyze this situation:

Current Location: {current_loc.get('name', 'Unknown')} ({current_loc.get('latitude')}, {current_loc.get('longitude')})
Current Time: {current_time}
Upcoming Events: {json.dumps(upcoming_events, indent=2)}

Recent Locations: {json.dumps(request.location_data[-5:], indent=2)}
{rag_context}
Task: Determine what the user is doing right now and what they'll need soon.
Consider: Are they commuting? At work? At home? Heading somewhere?
{f"Use the similar past situations above to inform your suggestions." if similar_events else ""}

Provide ONE actionable insight in this format:
TITLE: [Short engaging title]
MESSAGE: [What's happening and what to suggest, 2 sentences max]
ACTION: [Button text, 2-3 words]
REASONING: [Why this suggestion makes sense]"""

        logger.debug(f"   Sending prompt to LLM (length: {len(prompt)} chars)")
        response = await self.llm.analyze(prompt)
        logger.info(f"✅ {self.name} completed analysis")
        
        insight = self._parse_response(response, "context")
        
        # Elevate priority for commute scenarios
        if is_work_commute:
            insight.priority = "high"
        
        return [insight]
    
    def _parse_response(self, llm_response: str, category: str) -> AgentInsight:
        """Parse LLM response into structured insight"""
        
        lines = llm_response.strip().split('\n')
        title = "Context Detected"
        message = llm_response[:200]
        action = "View Details"
        reasoning = "AI analysis of current context"
        
        for line in lines:
            if line.startswith("TITLE:"):
                title = line.replace("TITLE:", "").strip()
            elif line.startswith("MESSAGE:"):
                message = line.replace("MESSAGE:", "").strip()
            elif line.startswith("ACTION:"):
                action = line.replace("ACTION:", "").strip()
            elif line.startswith("REASONING:"):
                reasoning = line.replace("REASONING:", "").strip()
        
        return AgentInsight(
            agent_name=self.name,
            title=title,
            message=message,
            action=action,
            category=category,
            priority="medium",
            confidence=0.85,
            reasoning=reasoning
        )