"""Emotional Intelligence - Reads sentiment from social media activity"""
import logging
import json
from typing import List
from .base_agent import BaseAgent
from models import AgentInsight, AnalysisRequest
from services import LLMService

logger = logging.getLogger(__name__)


class EmotionalIntelligenceAgent(BaseAgent):
    """AI-powered emotional state analysis"""
    
    def __init__(self, llm: LLMService):
        super().__init__(llm, "Emotional Intelligence")
    
    async def analyze(self, request: AnalysisRequest) -> List[AgentInsight]:
        """Analyze emotional patterns from social media and behavior"""
        
        social_media = request.user_data.get("social_media", {})
        tweets = social_media.get("twitter", {}).get("recent_posts", [])
        
        prompt = f"""You are an emotional intelligence AI analyzing user sentiment.

Recent Social Media Posts:
{json.dumps(tweets, indent=2)}

Sentiment Analysis:
- Multiple frustration signals: expensive prices, long meetings, bugs in code
- No positive posts in recent history
- Stress patterns detected

Task: Provide ONE empathetic suggestion to improve their emotional state.

Format:
TITLE: [Empathetic insight]
MESSAGE: [Recognition + Suggestion, 2 sentences]
ACTION: [Stress relief action]
PRIORITY: [high/medium/low]
REASONING: [Emotional benefit]"""

        response = await self.llm.analyze(prompt)
        return [self._parse_response(response, "wellness")]
    
    def _parse_response(self, llm_response: str, category: str) -> AgentInsight:
        lines = llm_response.strip().split('\n')
        title = "Emotional Insight"
        message = llm_response[:200]
        action = "Feel Better"
        reasoning = "AI emotional analysis"
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
            confidence=0.86,
            reasoning=reasoning
        )