"""
Unit tests for Response Parser
"""
import pytest
from utils.response_parser import ResponseParser


class TestResponseParser:
    """Test LLM response parsing"""
    
    def test_parse_complete_response(self):
        """Test parsing response with all fields"""
        llm_response = """TITLE: Test Title
MESSAGE: This is a test message
ACTION: Test Action
PRIORITY: high
REASONING: Test reasoning"""
        
        insight = ResponseParser.parse_llm_response(
            llm_response, "Test Agent", "test_category", "medium", 0.85
        )
        
        assert insight.title == "Test Title"
        assert insight.message == "This is a test message"
        assert insight.action == "Test Action"
        assert insight.priority == "high"
        assert insight.reasoning == "Test reasoning"
        assert insight.agent_name == "Test Agent"
        assert insight.category == "test_category"
        assert insight.confidence == 0.85
        
    def test_parse_partial_response(self):
        """Test parsing response with missing fields uses defaults"""
        llm_response = """TITLE: Partial Response
MESSAGE: Only has title and message"""
        
        insight = ResponseParser.parse_llm_response(
            llm_response, "Test Agent", "test", "low", 0.5
        )
        
        assert insight.title == "Partial Response"
        assert insight.message == "Only has title and message"
        assert insight.action == "View Details"  # Default
        assert insight.priority == "low"
        assert insight.reasoning is not None
        
    def test_parse_malformed_response(self):
        """Test parsing completely malformed response"""
        llm_response = "This is just random text without any structure"
        
        insight = ResponseParser.parse_llm_response(
            llm_response, "Test Agent", "test", "medium", 0.7
        )
        
        # Should still create insight with defaults
        assert insight.agent_name == "Test Agent"
        assert insight.priority == "medium"
        assert insight.confidence == 0.7
        
    def test_parse_with_colon_in_message(self):
        """Test parsing when message contains colons"""
        llm_response = """TITLE: Complex Message
MESSAGE: This message has: multiple: colons: in it
ACTION: Do Something"""
        
        insight = ResponseParser.parse_llm_response(
            llm_response, "Test Agent", "test", "medium", 0.8
        )
        
        # Should keep everything after first MESS AGE:
        assert "multiple: colons: in it" in insight.message
