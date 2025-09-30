"""Parses LLM text responses into structured insight objects"""
from models import AgentInsight


class ResponseParser:
    """Parses LLM responses into structured data"""
    
    @staticmethod
    def parse_llm_response(
        llm_response: str,
        agent_name: str,
        category: str,
        default_priority: str = "medium",
        default_confidence: float = 0.85
    ) -> AgentInsight:
        """Parse LLM response into structured insight"""
        
        lines = llm_response.strip().split('\n')
        title = "AI Insight"
        message = llm_response[:200]
        action = "View Details"
        reasoning = "AI analysis"
        priority = default_priority
        confidence = default_confidence
        
        for line in lines:
            line = line.strip()
            
            if "TITLE:" in line:
                title = line.split("TITLE:")[-1].strip()
            elif "MESSAGE:" in line:
                message = line.split("MESSAGE:")[-1].strip()
            elif "ACTION:" in line:
                action = line.split("ACTION:")[-1].strip()
            elif "REASONING:" in line:
                reasoning = line.split("REASONING:")[-1].strip()
            elif "PRIORITY:" in line:
                priority = line.split("PRIORITY:")[-1].strip().lower()
                if priority not in ["critical", "high", "medium", "low"]:
                    priority = default_priority
        
        return AgentInsight(
            agent_name=agent_name,
            title=title,
            message=message,
            action=action,
            category=category,
            priority=priority,
            confidence=confidence,
            reasoning=reasoning
        )
