"""
Integration tests for feedback system
Tests complete flow from HTTP request to database
"""
import pytest
from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


class TestFeedbackEndpoints:
    """Test feedback API integration"""
    
    def test_record_feedback_clicked(self):
        """Test successful feedback recording with clicked action"""
        payload = {
            "insight": {
                "agent_name": "Context Analyzer",
                "category": "context",
                "title": "Test Insight",
                "message": "Test message"
            },
            "action": "clicked"
        }
        
        response = client.post("/feedback", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "recorded"
        assert data["action"] == "clicked"
        assert data["category"] == "context"
        assert "average_score" in data
        assert data["average_score"] > 0
    
    def test_record_feedback_dismissed(self):
        """Test recording dismissed feedback"""
        payload = {
            "insight": {
                "agent_name": "Productivity Intelligence",
                "category": "productivity",
                "title": "Work Tip",
                "message": "Prepare early"
            },
            "action": "dismissed"
        }
        
        response = client.post("/feedback", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        assert data["action"] == "dismissed"
    
    def test_record_feedback_invalid_action(self):
        """Test feedback with invalid action"""
        payload = {
            "insight": {
                "agent_name": "Test",
                "category": "test",
                "title": "Test",
                "message": "Test"
            },
            "action": "invalid_action"
        }
        
        response = client.post("/feedback", json=payload)
        
        assert response.status_code == 400
        assert "Invalid action" in response.json()["detail"]
    
    def test_get_feedback_stats(self):
        """Test getting feedback statistics"""
        response = client.get("/feedback/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "feedback_count" in data
        assert data["status"] == "active"
        assert isinstance(data["feedback_count"], int)


class TestRAGEndpoints:
    """Test RAG-related endpoints"""
    
    def test_rag_stats(self):
        """Test RAG statistics endpoint"""
        response = client.get("/rag/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "indexed_items" in data
        assert "embedding_model" in data
        assert data["embedding_model"] == "all-MiniLM-L6-v2"
        assert "calendar_events" in data["indexed_items"]
        assert "locations" in data["indexed_items"]
    
    def test_rag_search_calendar(self):
        """Test RAG semantic search on calendar"""
        response = client.get(
            "/rag/search",
            params={"query": "standup meeting", "collection": "calendar_events"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "standup meeting"
        assert data["collection"] == "calendar_events"
        assert "results" in data
        assert isinstance(data["results"], list)
    
    def test_rag_search_invalid_collection(self):
        """Test RAG search with invalid collection"""
        response = client.get(
            "/rag/search",
            params={"query": "test", "collection": "invalid"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
