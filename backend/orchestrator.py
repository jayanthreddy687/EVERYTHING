import logging
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

from models import AnalysisRequest
from services import LLMService, RAGService
from utils import ContextDetector, LLMContextDetector
from agents import (
    ContextAnalyzerAgent,
    WellnessIntelligenceAgent,
    ProductivityIntelligenceAgent,
    SocialIntelligenceAgent,
    EmotionalIntelligenceAgent,
    FinancialIntelligenceAgent,
    ContentCurationAgent
)
from config import PRIORITY_MAP, MAX_INSIGHTS_PER_REQUEST

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    def __init__(self, use_llm_detection=True):
        self.llm = LLMService()
        self.rag = RAGService()
        
        if use_llm_detection and self.llm.use_llm:
            self.context_detector = LLMContextDetector(self.llm)
            logger.info("Using LLM context detection")
        else:
            self.context_detector = ContextDetector()
            logger.info("Using rule-based detection")
        
        self.agent_map = {
            "context": ContextAnalyzerAgent(self.llm, self.rag),
            "wellness": WellnessIntelligenceAgent(self.llm),
            "productivity": ProductivityIntelligenceAgent(self.llm, self.rag),
            "social": SocialIntelligenceAgent(self.llm),
            "emotional": EmotionalIntelligenceAgent(self.llm),
            "financial": FinancialIntelligenceAgent(self.llm),
            "content": ContentCurationAgent(self.llm)
        }
        
        self.agents = list(self.agent_map.values())
        self.user_preferences = self._load_preferences()
        self.agent_weights = self.user_preferences.get("agent_weights", {}) if self.user_preferences else {}
    
    def _load_preferences(self) -> Dict[str, Any]:
        try:
            path = Path("/app/data/user_onboarding.json") if os.path.exists("/app/data") else \
                   Path(__file__).parent.parent / "data" / "user_onboarding.json"
            
            if path.exists():
                with open(path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.debug(f"No preferences loaded: {e}")
            return {}
    
    async def orchestrate(self, request: AnalysisRequest) -> Dict[str, Any]:
        start = datetime.now()
        user = request.user_data.get('name', 'User')
        location = request.current_context.get('location', {}).get('name', 'Unknown')
        
        logger.info(f" {user} | {location} | {len(request.calendar_events)} events")
        
        scenario = await self.context_detector.detect_scenario(request)
        
        active_agents = [
            self.agent_map[key] for key in scenario["triggers"] 
            if key in self.agent_map
        ]
        
        logger.info(f"Running {len(active_agents)}/{len(self.agent_map)} agents")
        
        tasks = [agent.analyze(request) for agent in active_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        insights = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                insights.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"{active_agents[i].name} error: {result}")
        
        if self.agent_weights:
            insights = self._apply_weights(insights)
        
        insights.sort(key=lambda x: (PRIORITY_MAP.get(x.priority, 2), -x.confidence))
        
        duration = (datetime.now() - start).total_seconds()
        logger.info(f"{duration:.2f}s | {scenario['type']} | {len(insights)} insights")
        
        return {
            "insights": insights[:MAX_INSIGHTS_PER_REQUEST],
            "scenario": scenario,
            "active_agents": len(active_agents),
            "total_agents": len(self.agent_map),
            "insights_generated": len(insights),
            "using_llm": self.llm.use_llm,
            "timestamp": datetime.now().isoformat()
        }
    
    def _apply_weights(self, insights):
        for insight in insights:
            agent_type = next(
                (key for key, agent in self.agent_map.items() 
                 if agent.name == insight.agent_name),
                None
            )
            if agent_type and agent_type in self.agent_weights:
                weight = self.agent_weights[agent_type]
                insight.confidence = min(1.0, insight.confidence * weight)
        return insights
