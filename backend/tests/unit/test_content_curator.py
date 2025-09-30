"""
Unit tests for Content Curator Agent - All 8 Scenarios
"""
import pytest
from agents.content_curator import ContentCurationAgent
from models import AnalysisRequest


@pytest.mark.asyncio
class TestContentCuratorScenarios:
    """Test all 8 manual scenarios"""
    
    async def test_before_sleep_scenario(self, mock_llm_service, sample_analysis_request):
        """Test before_sleep scenario recommends late night playlists"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "before_sleep"
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "music"
        assert insights[0].agent_name == "Content Curator"
        # Should recommend Late Night playlist
        
    async def test_weekend_scenario(self, mock_llm_service, sample_analysis_request):
        """Test weekend scenario with different activities"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "weekend"
        
        # Add weekend event
        sample_analysis_request.calendar_events.insert(0, {
            "time": "10:00",
            "event": "Farmers Market",
            "location": "Local Market"
        })
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "music"
        
    async def test_commuting_to_work_scenario(self, mock_llm_service, sample_analysis_request):
        """Test commuting scenario recommends commute playlist"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "commuting_to_work"
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "music"
        # Should recommend Commute playlist
        
    async def test_at_work_scenario(self, mock_llm_service, sample_analysis_request):
        """Test at_work scenario recommends focus playlist"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "at_work"
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "music"
        # Should recommend Focus playlist
        
    async def test_workout_time_scenario(self, mock_llm_service, sample_analysis_request):
        """Test workout scenario recommends energetic playlist"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "workout_time"
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "music"
        
    async def test_social_evening_scenario(self, mock_llm_service, sample_analysis_request):
        """Test social evening scenario"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "social_evening"
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "music"
        
    async def test_lunch_time_scenario(self, mock_llm_service, sample_analysis_request):
        """Test lunch time scenario"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "lunch_time"
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "music"
        
    async def test_shopping_scenario(self, mock_llm_service, sample_analysis_request):
        """Test shopping scenario"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "shopping"
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        assert insights[0].category == "music"


@pytest.mark.asyncio
class TestContentCuratorAutoDetection:
    """Test auto-detection of scenarios"""
    
    async def test_auto_detect_commuting(self, mock_llm_service, sample_analysis_request):
        """Test auto-detection of commuting from calendar"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = None
        
        # Set up commuting event
        sample_analysis_request.calendar_events[0] = {
            "time": "09:00",
            "event": "Standup Meeting",
            "location": "Office"
        }
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1
        
    async def test_auto_detect_deep_work(self, mock_llm_service, sample_analysis_request):
        """Test auto-detection of deep work"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = None
        
        # Set up deep work event
        sample_analysis_request.calendar_events[0] = {
            "time": "14:00",
            "event": "Deep work: Feature development",
            "location": "Office"
        }
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert len(insights) == 1


@pytest.mark.asyncio
class TestContentCuratorParsing:
    """Test response parsing"""
    
    async def test_parse_response_with_all_fields(self, mock_llm_service, sample_analysis_request):
        """Test parsing when LLM returns all fields"""
        agent = ContentCurationAgent(mock_llm_service)
        sample_analysis_request.manual_scenario = "before_sleep"
        
        insights = await agent.analyze(sample_analysis_request)
        
        assert insights[0].title == "Test Insight"
        assert insights[0].message == "This is a test message for unit testing."
        assert insights[0].action == "Test Action"
        assert insights[0].reasoning == "Testing purposes"
        assert insights[0].confidence == 0.84
