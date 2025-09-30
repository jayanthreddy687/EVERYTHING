"""
Financial Intelligence Agent - AI-powered financial optimization
EXACT copy from original backend/main.py lines 618-750
"""
import logging
import json
from typing import List
from .base_agent import BaseAgent
from models import AgentInsight, AnalysisRequest
from services import LLMService

logger = logging.getLogger(__name__)


class FinancialIntelligenceAgent(BaseAgent):
    """AI-powered financial optimization"""
    
    def __init__(self, llm: LLMService):
        super().__init__(llm, "Financial Intelligence")
    
    async def analyze(self, request: AnalysisRequest) -> List[AgentInsight]:
        """Analyze spending and suggest optimizations"""
        
        purchases = request.user_data.get("purchases", [])
        social_media = request.user_data.get("social_media", {})
        tweets = social_media.get("twitter", {}).get("recent_posts", [])
        calendar = request.calendar_events
        
        # Extract financial-relevant events from calendar
        shopping_events = [e for e in calendar if any(w in e.get('event', '').lower() 
                          for w in ['market', 'shopping', 'store', 'mall', 'buy'])]
        
        lunch_events = [e for e in calendar if any(w in e.get('event', '').lower() 
                       for w in ['lunch', 'sandwich', 'food', 'grab', 'eat'])]
        
        social_events = [e for e in calendar if any(w in e.get('event', '').lower() 
                        for w in ['drinks', 'pub', 'bar', 'dinner', 'restaurant'])]
        
        # Build context based on calendar
        financial_context = []
        if shopping_events:
            financial_context.append(f"Shopping planned: {shopping_events[0].get('event')} at {shopping_events[0].get('location', 'unknown')}")
        if lunch_events:
            financial_context.append(f"Lunch scheduled: {lunch_events[0].get('event')} at {lunch_events[0].get('location', 'unknown')}")
        if social_events:
            financial_context.append(f"Social event: {social_events[0].get('event')} at {social_events[0].get('location', 'unknown')}")
        
        # Check if this is shopping mode
        is_shopping_mode = request.manual_scenario == "shopping"
        
        if is_shopping_mode or shopping_events:
            # Shopping-specific prompt
            prompt = f"""You are a shopping assistant AI helping with purchases.

Recent Purchases:
{json.dumps(purchases, indent=2)}

Shopping Events from Calendar:
{json.dumps(shopping_events, indent=2) if shopping_events else "No shopping events"}

User's Interests (from social media):
{json.dumps(tweets, indent=2)}

Financial Context:
{chr(10).join('- ' + c for c in financial_context) if financial_context else "- No specific events"}

Task: Based on the ACTUAL calendar events, provide smart shopping advice:
- If "farmers market" scheduled → suggest budget, what to buy, compare vs supermarket prices
- If shopping mall → suggest deal alerts, cashback apps, best timing
- If lunch at expensive place → suggest cheaper alternatives nearby
- Otherwise → general money-saving tips based on recent purchases

Format:
TITLE: [Shopping tip or deal alert specific to calendar]
MESSAGE: [Specific advice for the scheduled event, 2 sentences max]
ACTION: [What to do - e.g., "Check Deals", "Compare Prices"]
PRIORITY: medium
REASONING: [Why this saves money based on calendar]"""
        else:
            # General financial optimization with calendar context
            prompt = f"""You are a financial intelligence AI.

Recent Purchases:
{json.dumps(purchases, indent=2)}

Financial Complaints:
{json.dumps([t for t in tweets if '£' in t], indent=2)}

ALL Calendar Events (Financial Impact):
{json.dumps(calendar[:5], indent=2)}

Lunch Events:
{json.dumps(lunch_events, indent=2) if lunch_events else "None"}

Social/Dining Events:
{json.dumps(social_events, indent=2) if social_events else "None"}

Financial Context:
{chr(10).join('- ' + c for c in financial_context) if financial_context else "- No spending events scheduled"}

Task: Based on ACTUAL calendar events, suggest ONE specific money-saving opportunity.
- If lunch at "Borough Market" → suggest cheaper alternatives (e.g., Pret, meal prep)
- If "pub quiz" or "drinks" → suggest budgeting tips, cheaper venues
- If expensive purchases in history → suggest comparison shopping
- Use actual locations and events from calendar above

Format:
TITLE: [Financial insight specific to calendar]
MESSAGE: [Problem from calendar + Cheaper Alternative, 2 sentences]
ACTION: [Cost-saving action]
PRIORITY: [high/medium/low]
REASONING: [Money saved based on calendar]"""

        response = await self.llm.analyze(prompt)
        return [self._parse_response(response, "ai")]
    
    def _parse_response(self, llm_response: str, category: str) -> AgentInsight:
        lines = llm_response.strip().split('\n')
        title = "Cost Optimization"
        message = llm_response[:200]
        action = "Save Money"
        reasoning = "AI financial analysis"
        priority = "low"
        
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
            confidence=0.81,
            reasoning=reasoning
        )