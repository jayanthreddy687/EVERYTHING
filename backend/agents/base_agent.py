"""
Base agent class that all agents inherit from
"""
from abc import ABC, abstractmethod
from typing import List
from models import AgentInsight, AnalysisRequest
from services import LLMService


class BaseAgent(ABC):
    """Base class for all AI agents"""
    
    def __init__(self, llm: LLMService, name: str):
        self.llm = llm
        self.name = name
    
    @abstractmethod
    async def analyze(self, request: AnalysisRequest) -> List[AgentInsight]:
        """
        Analyze the request and return insights
        Must be implemented by all agents
        """
        pass
