"""
Unit tests for other AI Agents
"""
import pytest
from agents.context_analyzer import ContextAnalyzerAgent
from agents.wellness_intelligence import WellnessIntelligenceAgent
from agents.productivity_intelligence import ProductivityIntelligenceAgent
from agents.social_intelligence import SocialIntelligenceAgent
from agents.emotional_intelligence import EmotionalIntelligenceAgent
from agents.financial_intelligence import FinancialIntelligenceAgent


@pytest.mark.asyncio
class TestContextAnalyzer:
    """Test Context Analyzer Agent"""
    
    async def test_context_analyzer_commute_detection(self, mock_llm_service, sample_analysis_request):
        """Test that context analyzer detects commute scenario"""
        agent = ContextAnalyzerAgent(mock_llm_service)
        
        # Set up commute scenario
        sample_analysis_request.calendar_events[0] = {
            "time": "09:00",
            "event": "Daily Standup",
            "location": "Office"
        }
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "context"
        assert insights[0].agent_name == "Context Analyzer"
        
    async def test_context_analyzer_priority_elevation(self, mock_llm_service, sample_analysis_request):
        """Test priority elevation for work commute"""
        agent = ContextAnalyzerAgent(mock_llm_service)
        
        # Set up work commute
        sample_analysis_request.calendar_events[0] = {
            "time": "09:00",
            "event": "Important meeting",
            "location": "Office"
        }
        
        insights = await agent.analyze(sample_analysis_request)
        
        # Priority should be elevated to high for commute
        assert insights[0].priority == "high"


@pytest.mark.asyncio
class TestWellnessAgent:
    """Test Wellness Intelligence Agent"""
    
    async def test_wellness_analysis(self, mock_llm_service, sample_analysis_request):
        """Test wellness agent analyzes sleep and fitness"""
        agent = WellnessIntelligenceAgent(mock_llm_service)
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "wellness"
        assert insights[0].agent_name == "Wellness Intelligence"
        
    async def test_wellness_poor_sleep_priority(self, mock_llm_service, sample_analysis_request):
        """Test priority elevation for poor sleep"""
        agent = WellnessIntelligenceAgent(mock_llm_service)
        
        # Set poor sleep quality
        sample_analysis_request.user_data["fitness_data"]["sleep"]["quality"] = "poor"
        
        insights = await agent.analyze(sample_analysis_request)
        
        # Should elevate to high priority
        assert insights[0].priority == "high"


@pytest.mark.asyncio
class TestProductivityAgent:
    """Test Productivity Intelligence Agent"""
    
    async def test_productivity_analysis(self, mock_llm_service, sample_analysis_request):
        """Test productivity agent provides insights"""
        agent = ProductivityIntelligenceAgent(mock_llm_service)
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "productivity"
        
    async def test_productivity_skip_on_weekend(self, mock_llm_service, sample_analysis_request):
        """Test that productivity agent skips weekend mode"""
        agent = ProductivityIntelligenceAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "weekend"
        
        insights = await agent.analyze(sample_analysis_request)
        
        # Should return empty list for weekend
        assert len(insights) == 0


@pytest.mark.asyncio
class TestSocialAgent:
    """Test Social Intelligence Agent"""
    
    async def test_social_analysis(self, mock_llm_service, sample_analysis_request):
        """Test social agent analyzes calendar events"""
        agent = SocialIntelligenceAgent(mock_llm_service)
        
        # Add social event
        sample_analysis_request.calendar_events.append({
            "time": "19:00",
            "event": "Drinks with friends",
            "location": "Local pub"
        })
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "social"


@pytest.mark.asyncio
class TestEmotionalAgent:
    """Test Emotional Intelligence Agent"""
    
    async def test_emotional_analysis(self, mock_llm_service, sample_analysis_request):
        """Test emotional agent analyzes sentiment"""
        agent = EmotionalIntelligenceAgent(mock_llm_service)
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "wellness"


@pytest.mark.asyncio
class TestFinancialAgent:
    """Test Financial Intelligence Agent"""
    
    async def test_financial_analysis(self, mock_llm_service, sample_analysis_request):
        """Test financial agent analyzes purchases"""
        agent = FinancialIntelligenceAgent(mock_llm_service)
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "ai"
        
    async def test_financial_shopping_mode(self, mock_llm_service, sample_analysis_request):
        """Test financial agent handles shopping mode"""
        agent = FinancialIntelligenceAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "shopping"
        
        # Add shopping event
        sample_analysis_request.calendar_events.insert(0, {
            "time": "10:00",
            "event": "Farmers Market",
            "location": "Local Market"
        })
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
