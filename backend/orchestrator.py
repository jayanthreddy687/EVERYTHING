"""Agent Orchestrator - Runs the right agents for each scenario"""
import logging
import asyncio
import json
import os
from pathlib import Path
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
        
        # Load user preferences and agent weights
        self.user_preferences = self._load_onboarding_preferences()
        self.agent_weights = self.user_preferences.get("agent_weights", {}) if self.user_preferences else {}
        
        if self.agent_weights:
            logger.info("✨ User preferences loaded - insights will be personalized")
            logger.info(f"   Agent weights: {self.agent_weights}")
    
    def _load_onboarding_preferences(self) -> Dict[str, Any]:
        """Load user onboarding preferences if available"""
        try:
            # Determine data path
            if os.path.exists("/app/data"):
                onboarding_file = Path("/app/data/user_onboarding.json")
            else:
                onboarding_file = Path(__file__).parent.parent / "data" / "user_onboarding.json"
            
            if onboarding_file.exists():
                with open(onboarding_file, 'r') as f:
                    return json.load(f)
            
            return {}
        except Exception as e:
            logger.warning(f"⚠️  Could not load onboarding preferences: {e}")
            return {}
    
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
        
        # STEP 4: Apply user preference weights to insights
        if self.agent_weights:
            for insight in all_insights:
                # Find which agent type this insight came from
                agent_type = None
                for key, agent in self.agent_map.items():
                    if agent.name == insight.agent_name:
                        agent_type = key
                        break
                
                # Apply weight multiplier to confidence
                if agent_type and agent_type in self.agent_weights:
                    weight = self.agent_weights[agent_type]
                    original_confidence = insight.confidence
                    insight.confidence = min(1.0, insight.confidence * weight)
                    
                    if weight > 1.0:
                        logger.debug(f"   🎯 Boosted {insight.agent_name} insight: {original_confidence:.2f} → {insight.confidence:.2f}")
        
        # STEP 5: Sort by priority and weighted confidence
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
