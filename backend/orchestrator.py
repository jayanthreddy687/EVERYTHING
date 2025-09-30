"""Agent Orchestrator - Runs the right agents for each scenario"""
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any

from models import AnalysisRequest
from services import LLMService, RAGService
from utils import ContextDetector
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
    """Coordinates all AI agents based on context"""
    
    def __init__(self):
        self.llm = LLMService()
        self.rag = RAGService()  # Initialize RAG service
        self.context_detector = ContextDetector()
        
        # Initialize all agents with names for mapping
        # Pass RAG service to agents that need contextual memory
        self.agent_map = {
            "context": ContextAnalyzerAgent(self.llm, self.rag),  # Context analyzer uses RAG
            "wellness": WellnessIntelligenceAgent(self.llm),
            "productivity": ProductivityIntelligenceAgent(self.llm, self.rag),  # Productivity uses RAG for work patterns
            "social": SocialIntelligenceAgent(self.llm),
            "emotional": EmotionalIntelligenceAgent(self.llm),
            "financial": FinancialIntelligenceAgent(self.llm),
            "content": ContentCurationAgent(self.llm)
        }
        
        # Keep legacy list for compatibility
        self.agents = list(self.agent_map.values())
    
    async def orchestrate(self, request: AnalysisRequest) -> Dict[str, Any]:
        """Run context-aware agents (only relevant ones for current situation)"""
        
        logger.info("=" * 70)
        logger.info("🚀 CONTEXT-AWARE ORCHESTRATOR STARTING")
        logger.info("=" * 70)
        logger.info(f"   User: {request.user_data.get('name', 'Unknown')}")
        logger.info(f"   Location: {request.current_context.get('location', {}).get('name', 'Unknown')}")
        logger.info(f"   Calendar Events: {len(request.calendar_events)}")
        logger.info("")
        
        start_time = datetime.now()
        
        # STEP 1: Detect current scenario
        scenario = self.context_detector.detect_scenario(request)
        
        # STEP 2: Select only relevant agents for this scenario
        active_agents = []
        for agent_key in scenario["triggers"]:
            if agent_key in self.agent_map:
                active_agents.append(self.agent_map[agent_key])
        
        logger.info(f"   📋 Active Agents for this scenario: {len(active_agents)}/{len(self.agent_map)}")
        for agent in active_agents:
            logger.info(f"      • {agent.name}")
        logger.info("")
        
        # STEP 3: Run only the relevant agents
        tasks = [agent.analyze(request) for agent in active_agents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_insights = []
        for i, result in enumerate(results):
            if isinstance(result, list):
                all_insights.extend(result)
                logger.info(f"   ✅ {active_agents[i].name}: {len(result)} insights")
            elif isinstance(result, Exception):
                logger.error(f"   ❌ {active_agents[i].name}: {str(result)}")
        
        # STEP 4: Sort by priority and confidence
        all_insights.sort(key=lambda x: (PRIORITY_MAP.get(x.priority, 2), -x.confidence))
        
        duration = (datetime.now() - start_time).total_seconds()
        
        logger.info("")
        logger.info(f"📊 ORCHESTRATION COMPLETE")
        logger.info(f"   Duration: {duration:.2f}s")
        logger.info(f"   Scenario: {scenario['type']}")
        logger.info(f"   Active Agents: {len(active_agents)}")
        logger.info(f"   Total Insights: {len(all_insights)}")
        logger.info("=" * 70)
        logger.info("")
        
        return {
            "insights": all_insights[:MAX_INSIGHTS_PER_REQUEST],
            "scenario": scenario,
            "active_agents": len(active_agents),
            "total_agents": len(self.agent_map),
            "insights_generated": len(all_insights),
            "using_llm": self.llm.use_llm,
            "timestamp": datetime.now().isoformat()
        }
