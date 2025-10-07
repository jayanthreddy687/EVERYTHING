import logging
import json
from typing import Dict, Any
from datetime import datetime
from models import AnalysisRequest
from services import LLMService

logger = logging.getLogger(__name__)


class LLMContextDetector:
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
        self.scenarios = {
            "commuting_to_work": {
                "desc": "Traveling to work",
                "agents": ["context", "content", "productivity"]
            },
            "at_work": {
                "desc": "At workplace, productivity mode",
                "agents": ["productivity", "content", "emotional"]
            },
            "before_sleep": {
                "desc": "Late night winding down",
                "agents": ["wellness", "content", "emotional"]
            },
            "lunch_time": {
                "desc": "Midday break",
                "agents": ["financial", "social", "content"]
            },
            "social_evening": {
                "desc": "Evening social activities",
                "agents": ["social", "context", "emotional", "financial"]
            },
            "weekend": {
                "desc": "Weekend leisure",
                "agents": ["social", "wellness", "content"]
            },
            "workout_time": {
                "desc": "Exercise time",
                "agents": ["wellness", "social", "content"]
            },
            "shopping": {
                "desc": "Shopping activities",
                "agents": ["financial", "context"]
            },
            "general": {
                "desc": "General adaptive mode",
                "agents": ["context", "emotional"]
            }
        }
    
    async def detect_scenario(self, request: AnalysisRequest) -> Dict[str, Any]:
        if request.manual_scenario:
            logger.info(f"📱 Manual scenario: {request.manual_scenario}")
            return self._build_response(request.manual_scenario, 1.0, "User selected")
        
        if not self.llm.use_llm:
            return self._fallback_detection(request)
        
        context = self._extract_context(request)
        prompt = f"""Analyze this situation and classify into ONE scenario.

**Situation:**
{context}

**Available Scenarios:**
{self._format_scenarios()}

**Response (JSON only):**
{{
  "scenario_type": "...",
  "confidence": 0.0-1.0,
  "reasoning": "why this fits"
}}"""

        try:
            response_text = await self.llm.analyze(prompt, max_tokens=400)
            data = self._parse_json(response_text)
            
            scenario = data.get('scenario_type', 'general')
            if scenario not in self.scenarios:
                logger.warning(f"Unknown scenario '{scenario}', using general")
                scenario = 'general'
            
            confidence = min(1.0, max(0.0, float(data.get('confidence', 0.7))))
            reasoning = data.get('reasoning', '')
            agents = self.scenarios[scenario]['agents']
            
            logger.info(f"🎯 Detected: {scenario} ({confidence:.2f}) - {reasoning}")
            
            return {
                "type": scenario,
                "description": self.scenarios[scenario]["desc"],
                "confidence": confidence,
                "triggers": agents,
                "context_data": {"reasoning": reasoning, "method": "llm"}
            }
            
        except Exception as e:
            logger.error(f"LLM detection error: {e}")
            return self._fallback_detection(request)
    
    def _extract_context(self, request: AnalysisRequest) -> str:
        try:
            time_obj = datetime.fromisoformat(
                request.current_context.get("time", "").replace('Z', '+00:00')
            )
            time_str = time_obj.strftime("%A %I:%M %p")
            is_weekend = time_obj.weekday() >= 5
        except:
            time_str = "Unknown"
            is_weekend = False
        
        location = request.current_context.get("location", {}).get("name", "Unknown")
        profession = request.user_data.get("profession", "User")
        
        events = request.calendar_events[:3]
        next_event = events[0] if events else None
        
        context = f"Time: {time_str} ({'weekend' if is_weekend else 'weekday'})\n"
        context += f"Location: {location}\n"
        context += f"Profession: {profession}\n"
        
        if next_event:
            context += f"Next: {next_event.get('event')} at {next_event.get('time')}"
            if len(events) > 1:
                context += f"\nUpcoming: {len(events)} events today"
        
        return context
    
    def _format_scenarios(self) -> str:
        lines = []
        for name, info in self.scenarios.items():
            agents = ", ".join(info['agents'])
            lines.append(f"- {name}: {info['desc']} (agents: {agents})")
        return "\n".join(lines)
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    
    def _build_response(self, scenario: str, confidence: float, reasoning: str) -> Dict[str, Any]:
        info = self.scenarios.get(scenario, self.scenarios["general"])
        return {
            "type": scenario,
            "description": info["desc"],
            "confidence": confidence,
            "triggers": info["agents"],
            "context_data": {"reasoning": reasoning, "method": "manual"}
        }
    
    def _fallback_detection(self, request: AnalysisRequest) -> Dict[str, Any]:
        try:
            time_obj = datetime.fromisoformat(
                request.current_context.get("time", "").replace('Z', '+00:00')
            )
            hour, is_weekend = time_obj.hour, time_obj.weekday() >= 5
        except:
            hour, is_weekend = 12, False
        
        scenario = (
            "weekend" if is_weekend else
            "commuting_to_work" if 7 <= hour <= 9 else
            "lunch_time" if 12 <= hour <= 14 else
            "before_sleep" if hour >= 22 or hour <= 2 else
            "at_work" if 9 <= hour <= 18 else
            "general"
        )
        
        logger.info(f"🔄 Fallback: {scenario} (time-based)")
        return self._build_response(scenario, 0.6, f"Time-based fallback")

