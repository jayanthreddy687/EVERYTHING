"""
Productivity Intelligence Agent - AI-powered productivity optimization
EXACT copy from original backend/main.py lines 368-443
"""
import logging
import json
from typing import List
from .base_agent import BaseAgent
from models import AgentInsight, AnalysisRequest
from services import LLMService

logger = logging.getLogger(__name__)


class ProductivityIntelligenceAgent(BaseAgent):
    """AI-powered productivity optimization"""
    
    def __init__(self, llm: LLMService, rag_service=None):
        super().__init__(llm, "Productivity Intelligence")
        self.rag = rag_service  # Optional RAG service for work pattern analysis
    
    async def analyze(self, request: AnalysisRequest) -> List[AgentInsight]:
        """Analyze work patterns and suggest optimizations"""
        
        # Skip if it's weekend mode - no work suggestions on weekends!
        if request.manual_scenario == "weekend":
            return []
        
        logger.info(f"🔍 {self.name} starting analysis...")
        
        calendar = request.calendar_events
        app_usage = request.user_data.get("app_usage", {})
        profession = request.user_data.get("profession", "")
        
        work_events = [e for e in calendar if any(w in e.get('event', '').lower() 
                       for w in ['meeting', 'review', 'work', 'standup', 'demo'])]
        
        # RAG: Retrieve similar past work events if available
        similar_work_events = []
        if self.rag and work_events:
            # Build semantic query based on upcoming work
            next_work = work_events[0] if work_events else None
            if next_work:
                query = f"{next_work.get('event', 'work')} meeting at {next_work.get('location', 'office')}"
                
                # Try feedback-enhanced retrieval first
                try:
                    similar_work_events = self.rag.retrieve_similar_events_with_feedback(
                        query, 
                        category="productivity", 
                        top_k=3
                    )
                except:
                    # Fallback to standard retrieval
                    similar_work_events = self.rag.retrieve_similar_events(query, top_k=3)
                
                if similar_work_events:
                    logger.info(f"   📚 RAG: Retrieved {len(similar_work_events)} similar work events")
        
        # Build enhanced prompt with RAG context
        rag_context = ""
        if similar_work_events:
            rag_context = f"""
Similar Past Work Events:
{json.dumps(similar_work_events, indent=2)}

Note: User has attended similar events before. Use patterns to suggest preparation strategies.
"""
        
        prompt = f"""You are a productivity AI for a {profession}.

Today's Work Schedule:
{json.dumps(work_events, indent=2)}

App Usage Patterns:
- Terminal: 4h 20m (coding)
- Slack: 4h 50m (communication)
- Reddit: 2h 45m (distraction)
- Chrome: 7h 30m

Context: User has complained about "45-minute standups" and finding "3 bugs in code review"
{rag_context}
Task: Provide ONE smart productivity hack based on their schedule and pain points.
{f"Consider patterns from similar past events to suggest what worked before." if similar_work_events else ""}

Format:
TITLE: [Productivity optimization]
MESSAGE: [Insight + Action, 2 sentences]
ACTION: [Button text]
PRIORITY: [high/medium/low]
REASONING: [Why this will boost productivity]"""

        logger.debug(f"   Sending prompt to LLM (length: {len(prompt)} chars)")
        response = await self.llm.analyze(prompt)
        logger.info(f"✅ {self.name} completed analysis")
        
        return [self._parse_response(response, "productivity")]
    
    def _parse_response(self, llm_response: str, category: str) -> AgentInsight:
        lines = llm_response.strip().split('\n')
        title = "Productivity Boost"
        message = llm_response[:200]
        action = "Optimize"
        reasoning = "AI productivity analysis"
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
            confidence=0.87,
            reasoning=reasoning
        )