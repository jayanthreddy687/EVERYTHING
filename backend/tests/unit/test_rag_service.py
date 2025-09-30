"""
Unit tests for RAG Service
Tests vector storage, retrieval, and feedback functionality
"""
import pytest
from services.rag_service import RAGService


class TestRAGService:
    """Test RAG service functionality"""
    
    @pytest.fixture
    def rag_service(self):
        """Create a fresh RAG service instance for each test with in-memory storage"""
        service = RAGService(use_persistent=False)
        # Delete and recreate collections to ensure clean state
        try:
            service.client.delete_collection("calendar_events")
            service.client.delete_collection("location_history")
            service.client.delete_collection("insight_feedback")
            # Recreate them
            service.calendar_collection = service.client.create_collection(
                name="calendar_events",
                embedding_function=service.embedding_fn,
                metadata={"description": "Historical calendar events"}
            )
            service.location_collection = service.client.create_collection(
                name="location_history",
                embedding_function=service.embedding_fn,
                metadata={"description": "Location history"}
            )
            service.feedback_collection = service.client.create_collection(
                name="insight_feedback",
                embedding_function=service.embedding_fn,
                metadata={"description": "User feedback on insights"}
            )
            service.feedback_scores = {}
        except:
            pass
        return service
    
    @pytest.fixture
    def sample_calendar_events(self):
        """Sample calendar data for testing"""
        return [
            {
                "date": "2024-05-16",
                "time": "09:00",
                "event": "Team Standup",
                "location": "Tech Hub",
                "duration": "1"
            },
            {
                "date": "2024-05-16",
                "time": "11:00",
                "event": "Code Review",
                "location": "Tech Hub",
                "duration": "2"
            },
            {
                "date": "2024-05-17",
                "time": "14:00",
                "event": "Planning Meeting",
                "location": "Office",
                "duration": "1"
            }
        ]
    
    @pytest.fixture
    def sample_locations(self):
        """Sample location data for testing"""
        return [
            {
                "timestamp": "2024-05-16T08:30:00",
                "location": "Home",
                "latitude": 51.5074,
                "longitude": -0.1278
            },
            {
                "timestamp": "2024-05-16T09:00:00",
                "location": "Tech Hub",
                "latitude": 51.5144,
                "longitude": -0.0931
            }
        ]
    
    def test_rag_service_initialization(self, rag_service):
        """Test RAG service initializes correctly"""
        assert rag_service.client is not None
        assert rag_service.calendar_collection is not None
        assert rag_service.location_collection is not None
        assert rag_service.feedback_collection is not None
        assert rag_service.feedback_scores == {}
    
    def test_index_calendar_events(self, rag_service, sample_calendar_events):
        """Test indexing calendar events into vector store"""
        rag_service.index_calendar_events(sample_calendar_events)
        
        # Verify events were indexed
        stats = rag_service.get_stats()
        assert stats["calendar_events"] == 3
    
    def test_index_empty_calendar(self, rag_service):
        """Test indexing empty calendar events"""
        rag_service.index_calendar_events([])
        
        stats = rag_service.get_stats()
        assert stats["calendar_events"] == 0
    
    def test_index_location_history(self, rag_service, sample_locations):
        """Test indexing location history"""
        rag_service.index_location_history(sample_locations)
        
        stats = rag_service.get_stats()
        assert stats["locations"] == 2
    
    def test_retrieve_similar_events(self, rag_service, sample_calendar_events):
        """Test semantic search for similar events"""
        # Index events first
        rag_service.index_calendar_events(sample_calendar_events)
        
        # Search for similar events
        results = rag_service.retrieve_similar_events("standup meeting", top_k=2)
        
        assert len(results) <= 2
        assert len(results) > 0
        # Check structure
        assert "event" in results[0]
        assert "location" in results[0]
    
    def test_retrieve_with_no_data(self, rag_service):
        """Test retrieval when no data indexed"""
        results = rag_service.retrieve_similar_events("any query")
        assert results == []
    
    def test_record_feedback(self, rag_service):
        """Test recording user feedback"""
        insight_data = {
            "agent_name": "Context Analyzer",
            "category": "context",
            "title": "Test Insight",
            "message": "Test message"
        }
        
        rag_service.record_feedback(insight_data, "clicked")
        
        # Verify feedback was recorded
        stats = rag_service.get_stats()
        assert stats["feedback_items"] == 1
        
        # Check in-memory scores updated
        score = rag_service.get_feedback_score("context", "Context Analyzer")
        assert score == 1.0  # Clicked = +1.0
    
    def test_feedback_scoring(self, rag_service):
        """Test feedback score calculation"""
        insight = {
            "agent_name": "Test Agent",
            "category": "test",
            "title": "Test",
            "message": "Test"
        }
        
        # Record mixed feedback
        rag_service.record_feedback(insight, "clicked")    # +1.0
        rag_service.record_feedback(insight, "clicked")    # +1.0
        rag_service.record_feedback(insight, "dismissed")  # -0.5
        
        # Average should be (1.0 + 1.0 - 0.5) / 3 = 0.5
        score = rag_service.get_feedback_score("test", "Test Agent")
        assert abs(score - 0.5) < 0.01  # Allow small floating point error
    
    def test_feedback_enhanced_retrieval(self, rag_service, sample_calendar_events):
        """Test that feedback enhances retrieval"""
        # Index events
        rag_service.index_calendar_events(sample_calendar_events)
        
        # Record positive feedback for standup-related insight
        rag_service.record_feedback({
            "agent_name": "Context Analyzer",
            "category": "context",
            "title": "Standup Preparation",
            "message": "Prepare for team standup"
        }, "clicked")
        
        # Retrieve with feedback enhancement
        results = rag_service.retrieve_similar_events_with_feedback(
            "team standup meeting",
            category="context",
            top_k=2
        )
        
        assert len(results) > 0
    
    def test_get_stats(self, rag_service, sample_calendar_events, sample_locations):
        """Test getting statistics about indexed data"""
        rag_service.index_calendar_events(sample_calendar_events)
        rag_service.index_location_history(sample_locations)
        
        stats = rag_service.get_stats()
        
        assert stats["calendar_events"] == 3
        assert stats["locations"] == 2
        assert stats["feedback_items"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
