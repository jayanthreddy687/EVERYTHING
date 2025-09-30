"""
Unit tests for Context Detector - All Scenario Detection
"""
import pytest
from datetime import datetime
from utils.context_detector import ContextDetector
from models import AnalysisRequest


class TestScenarioConfigs:
    """Test scenario configuration retrieval"""
    
    def test_get_commuting_to_work_config(self):
        """Test commuting scenario config"""
        config = ContextDetector.get_scenario_config("commuting_to_work")
        
        assert config["type"] == "commuting_to_work"
        assert config["confidence"] == 1.0
        assert "context" in config["triggers"]
        assert "content" in config["triggers"]
        assert "productivity" in config["triggers"]
        
    def test_get_before_sleep_config(self):
        """Test before sleep scenario config"""
        config = ContextDetector.get_scenario_config("before_sleep")
        
        assert config["type"] == "before_sleep"
        assert "wellness" in config["triggers"]
        assert "content" in config["triggers"]
        
    def test_get_weekend_config(self):
        """Test weekend scenario config"""
        config = ContextDetector.get_scenario_config("weekend")
        
        assert config["type"] == "weekend"
        assert "social" in config["triggers"]
        assert "wellness" in config["triggers"]
        assert "content" in config["triggers"]
        
    def test_get_shopping_config(self):
        """Test shopping scenario config"""
        config = ContextDetector.get_scenario_config("shopping")
        
        assert config["type"] == "shopping"
        assert "financial" in config["triggers"]
        assert "context" in config["triggers"]
        
    def test_all_8_scenarios_exist(self):
        """Test that all 8 scenarios are defined"""
        scenarios = [
            "commuting_to_work",
            "at_work",
            "before_sleep",
            "lunch_time",
            "social_evening",
            "weekend",
            "workout_time",
            "shopping"
        ]
        
        for scenario in scenarios:
            config = ContextDetector.get_scenario_config(scenario)
            assert config["type"] == scenario
            assert "triggers" in config
            assert len(config["triggers"]) > 0


class TestManualScenarioOverride:
    """Test manual scenario selection"""
    
    def test_manual_scenario_override(self, sample_analysis_request):
        """Test that manual scenario overrides auto-detection"""
        sample_analysis_request.manual_scenario = "before_sleep"
        
        scenario = ContextDetector.detect_scenario(sample_analysis_request)
        
        assert scenario["type"] == "before_sleep"
        assert scenario.get("manual") == True
        assert scenario["confidence"] == 1.0
        
    def test_all_manual_scenarios(self, sample_analysis_request):
        """Test all 8 manual scenarios can be selected"""
        scenarios = [
            "before_sleep", "weekend", "commuting_to_work", "at_work",
            "workout_time", "social_evening", "lunch_time", "shopping"
        ]
        
        for scenario_type in scenarios:
            sample_analysis_request.manual_scenario = scenario_type
            result = ContextDetector.detect_scenario(sample_analysis_request)
            
            assert result["type"] == scenario_type
            assert result.get("manual") == True


class TestAutoScenarioDetection:
    """Test automatic scenario detection"""
    
    def test_detect_shopping_from_calendar(self, sample_analysis_request):
        """Test shopping detection from farmers market event"""
        sample_analysis_request.manual_scenario = None
        sample_analysis_request.calendar_events.insert(0, {
            "time": "10:00",
            "event": "Farmers Market",
            "location": "Local Market"
        })
        
        scenario = ContextDetector.detect_scenario(sample_analysis_request)
        
        assert scenario["type"] == "shopping"
        
    def test_detect_commuting_morning_at_home(self, sample_analysis_request):
        """Test commuting detection: morning, at home, work event soon"""
        sample_analysis_request.manual_scenario = None
        sample_analysis_request.current_context["time"] = "2024-01-15T08:30:00Z"
        sample_analysis_request.current_context["location"] = {
            "name": "Home",
            "latitude": 51.5285,
            "longitude": -0.1005
        }
        sample_analysis_request.calendar_events[0] = {
            "time": "09:00",
            "event": "Daily Standup",
            "location": "Office"
        }
        
        scenario = ContextDetector.detect_scenario(sample_analysis_request)
        
        assert scenario["type"] == "commuting_to_work"
        
    def test_detect_before_sleep_late_night(self, sample_analysis_request):
        """Test before sleep detection at 22:00"""
        sample_analysis_request.manual_scenario = None
        sample_analysis_request.current_context["time"] = "2024-01-15T22:30:00Z"
        
        scenario = ContextDetector.detect_scenario(sample_analysis_request)
        
        assert scenario["type"] == "before_sleep"
        
    def test_detect_lunch_time(self, sample_analysis_request):
        """Test lunch time detection with lunch event"""
        sample_analysis_request.manual_scenario = None
        sample_analysis_request.current_context["time"] = "2024-01-15T13:00:00Z"
        # Make sure we're NOT at work location (otherwise it detects as at_work)
        sample_analysis_request.current_context["location"] = {
            "name": "Restaurant",
            "latitude": 51.5050,
            "longitude": -0.0900
        }
        # Add a lunch event to trigger lunch_time detection
        sample_analysis_request.calendar_events.insert(0, {
            "time": "13:00",
            "event": "Grab lunch sandwich",
            "location": "Cafe"
        })
        
        scenario = ContextDetector.detect_scenario(sample_analysis_request)
        
        assert scenario["type"] == "lunch_time"
        
    def test_detect_social_evening(self, sample_analysis_request):
        """Test social evening detection from pub quiz event"""
        sample_analysis_request.manual_scenario = None
        sample_analysis_request.current_context["time"] = "2024-01-15T19:00:00Z"
        sample_analysis_request.calendar_events.insert(0, {
            "time": "19:30",
            "event": "Pub quiz with mates",
            "location": "The Eagle"
        })
        
        scenario = ContextDetector.detect_scenario(sample_analysis_request)
        
        assert scenario["type"] == "social_evening"
        
    def test_detect_workout_time(self, sample_analysis_request):
        """Test workout detection from morning run event"""
        sample_analysis_request.manual_scenario = None
        sample_analysis_request.current_context["time"] = "2024-01-15T07:00:00Z"
        sample_analysis_request.calendar_events.insert(0, {
            "time": "07:15",
            "event": "Morning run",
            "location": "Park"
        })
        
        scenario = ContextDetector.detect_scenario(sample_analysis_request)
        
        assert scenario["type"] == "workout_time"


class TestScenarioTriggers:
    """Test that correct agents are triggered for each scenario"""
    
    def test_commuting_triggers_correct_agents(self):
        """Commuting should trigger: context, content, productivity"""
        config = ContextDetector.get_scenario_config("commuting_to_work")
        
        assert set(config["triggers"]) == {"context", "content", "productivity"}
        
    def test_weekend_triggers_correct_agents(self):
        """Weekend should trigger: social, wellness, content"""
        config = ContextDetector.get_scenario_config("weekend")
        
        assert set(config["triggers"]) == {"social", "wellness", "content"}
        
    def test_shopping_triggers_correct_agents(self):
        """Shopping should trigger: financial, context"""
        config = ContextDetector.get_scenario_config("shopping")
        
        assert set(config["triggers"]) == {"financial", "context"}
