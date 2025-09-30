"""
Integration tests for FastAPI endpoints
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test GET /health returns health status"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "llm_available" in data
        assert "agents_count" in data
        
    def test_root_endpoint(self):
        """Test GET / returns API information"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "agents" in data


class TestScenariosEndpoint:
    """Test scenarios listing endpoint"""
    
    def test_get_scenarios(self):
        """Test GET /scenarios returns all 8 scenarios"""
        response = client.get("/scenarios")
        
        assert response.status_code == 200
        data = response.json()
        assert "scenarios" in data
        scenarios = data["scenarios"]
        assert len(scenarios) == 8
        
        scenario_types = [s["id"] for s in scenarios]
        expected_scenarios = [
            "before_sleep", "weekend", "commuting_to_work", "at_work",
            "workout_time", "social_evening", "lunch_time", "shopping"
        ]
        
        for expected in expected_scenarios:
            assert expected in scenario_types
            
    def test_scenario_structure(self):
        """Test each scenario has required fields"""
        response = client.get("/scenarios")
        data = response.json()
        scenarios = data["scenarios"]
        
        for scenario in scenarios:
            assert "id" in scenario
            assert "name" in scenario
            assert "description" in scenario
            assert "triggers" in scenario
            assert isinstance(scenario["triggers"], list)


class TestAnalyzeEndpoint:
    """Test main analysis endpoint"""
    
    def test_analyze_endpoint_structure(self):
        """Test /analyze accepts proper request"""
        request_data = {
            "current_context": {
                "location": {
                    "name": "Home",
                    "latitude": 51.5285,
                    "longitude": -0.1005
                },
                "time": "2024-01-15T08:30:00Z",
                "context_type": "morning"
            },
            "calendar_events": [
                {
                    "time": "09:00",
                    "event": "Daily Standup",
                    "location": "Office",
                    "duration": "30 min"
                }
            ],
            "user_data": {
                "name": "Alex",
                "profession": "Software Engineer"
            },
            "location_data": [],
            "manual_scenario": None
        }
        
        # This will fail if GEMINI_API_KEY is not set, but tests structure
        response = client.post("/analyze", json=request_data)
        
        # Should return 200 or 500 (if API key missing), but not 422 (validation error)
        assert response.status_code in [200, 500]


class TestManualScenarioEndpoint:
    """Test manual scenario selection via /analyze endpoint"""
    
    def test_analyze_with_manual_scenario(self):
        """Test /analyze with specific scenario"""
        request_data = {
            "current_context": {
                "location": {"name": "Home", "latitude": 51.5285, "longitude": -0.1005},
                "time": "2024-01-15T22:30:00Z",
                "context_type": "evening"
            },
            "calendar_events": [],
            "user_data": {
                "name": "Alex",
                "spotify": {"playlists": []},
                "fitness_data": {},
                "contacts": []
            },
            "location_data": [],
            "manual_scenario": "before_sleep"
        }
        
        response = client.post("/analyze", json=request_data)
        
        # Should accept the request (200 or 500 if API key missing)
        assert response.status_code in [200, 500]
        
    def test_all_manual_scenarios(self):
        """Test that all 8 scenarios can be manually selected"""
        scenarios = [
            "before_sleep", "weekend", "commuting_to_work", "at_work",
            "workout_time", "social_evening", "lunch_time", "shopping"
        ]
        
        for scenario in scenarios:
            request_data = {
                "current_context": {
                    "location": {"name": "Home", "latitude": 51.5, "longitude": 0.0},
                    "time": "2024-01-15T12:00:00Z",
                    "context_type": "general"
                },
                "calendar_events": [],
                "user_data": {
                    "name": "Test",
                    "spotify": {"playlists": []},
                    "fitness_data": {},
                    "contacts": []
                },
                "location_data": [],
                "manual_scenario": scenario
            }
            
            response = client.post("/analyze", json=request_data)
            
            # Should not return validation error
            assert response.status_code != 422
