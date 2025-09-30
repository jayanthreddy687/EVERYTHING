"""
Pytest configuration and shared fixtures
"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import AnalysisRequest, AgentInsight
from services import LLMService


@pytest.fixture
def mock_llm_service():
    """Mock LLM service for testing"""
    class MockLLM:
        async def analyze(self, prompt: str, max_tokens: int = 150) -> str:
            return """TITLE: Test Insight
MESSAGE: This is a test message for unit testing.
ACTION: Test Action
REASONING: Testing purposes"""
    
    return MockLLM()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "name": "Alex",
        "profession": "Software Engineer",
        "location": {
            "home": {
                "name": "Home",
                "coordinates": {"latitude": 51.5285, "longitude": -0.1005}
            },
            "work": {
                "name": "Office",
                "coordinates": {"latitude": 51.5320, "longitude": -0.0990}
            }
        },
        "spotify": {
            "playlists": [
                {
                    "name": "Morning Commute",
                    "tracks": ["Track 1", "Track 2", "Track 3"]
                },
                {
                    "name": "Focus Mode",
                    "tracks": ["Ambient 1", "Ambient 2"]
                },
                {
                    "name": "Late Night Vibes",
                    "tracks": ["Chill 1", "Chill 2", "Chill 3"]
                }
            ]
        },
        "fitness_data": {
            "sleep": {
                "last_night": "7.5h",
                "quality": "good"
            },
            "last_workout": {
                "type": "run",
                "felt": "energetic"
            },
            "steps_today": 8500
        },
        "app_usage": {
            "screen_time": "6h 30m"
        },
        "contacts": [
            {"name": "Mike Chen", "email": "mike.runner@email.com"},
            {"name": "Tom Walsh", "email": "tom@email.com"}
        ],
        "purchases": [
            {"item": "Coffee", "price": 3.50},
            {"item": "Lunch sandwich", "price": 7.00}
        ],
        "social_media": {
            "twitter": {
                "recent_posts": [
                    "Coffee is getting expensive these days... £4.50 for a latte!",
                    "Another 45-minute standup that could have been an email"
                ]
            }
        }
    }


@pytest.fixture
def sample_calendar_events():
    """Sample calendar events for testing"""
    return [
        {
            "time": "09:00",
            "event": "Daily Standup",
            "location": "Office",
            "duration": "30 min"
        },
        {
            "time": "13:00",
            "event": "Grab lunch at Borough Market",
            "location": "Borough Market",
            "duration": "1 hour"
        },
        {
            "time": "19:00",
            "event": "Pub quiz with mates",
            "location": "The Eagle",
            "duration": "2 hours"
        }
    ]


@pytest.fixture
def sample_analysis_request(sample_user_data, sample_calendar_events):
    """Complete analysis request for testing"""
    return AnalysisRequest(
        current_context={
            "location": {
                "name": "Home",
                "latitude": 51.5285,
                "longitude": -0.1005
            },
            "time": "2024-01-15T08:30:00Z",
            "context_type": "morning"
        },
        calendar_events=sample_calendar_events,
        user_data=sample_user_data,
        location_data=[
            {"name": "Home", "latitude": 51.5285, "longitude": -0.1005, "timestamp": "08:00"}
        ],
        manual_scenario=None
    )
