"""
Base agent class that defines the interface for all agents in the system.
"""
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system.
    
    An agent represents an AI assistant with a specific personality and role
    in the collaborative writing process.
    """
    
    def __init__(
        self,
        name: str,
        instructions: str,
        model: str = "gpt-4",
        functions: Optional[List[Callable]] = None,
        tool_choice: Optional[str] = None,
        provider: str = "openai"
    ):
        """
        Initialize a new agent.
        
        Args:
            name: Unique identifier for the agent
            instructions: System prompt/personality for the agent
            model: The LLM model to use (default: "gpt-4")
            functions: List of callable functions available to the agent
            tool_choice: Optional tool selection parameter
            provider: AI provider to use ("openai" or "anthropic")
        """
        self.name = name
        self.instructions = instructions
        self.model = model
        self.functions = functions or []
        self.tool_choice = tool_choice
        self.provider = provider
    
    @abstractmethod
    def process_response(self, content: str) -> Dict[str, Any]:
        """
        Process the raw response from the agent.
        
        This method should extract structured information from the agent's
        response, such as consensus markers, content, and any other
        relevant metadata.
        
        Args:
            content: Raw response from the agent
            
        Returns:
            Dictionary containing structured information from the response
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert agent to a dictionary representation.
        
        Returns:
            Dictionary representation of the agent
        """
        return {
            "name": self.name,
            "instructions": self.instructions,
            "model": self.model,
            "functions": [f.__name__ for f in self.functions] if self.functions else [],
            "tool_choice": self.tool_choice,
            "provider": self.provider
        }
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.name} Agent (model: {self.model}, provider: {self.provider})"
