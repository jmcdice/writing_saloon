"""
Agent factory for creating different types of agents.
"""
from typing import Callable, List, Optional, Dict, Any

from .base import BaseAgent
from .zero import ZeroAgent
from .gustave import GustaveAgent
from .camille import CamilleAgent


class AgentFactory:
    """
    Factory class for creating different types of agents.
    """
    
    # Updated model mappings for 2025
    DEFAULT_MODELS = {
        "openai": {
            "primary": "gpt-4",  # Could upgrade to gpt-4-turbo if available
            "fallback": "gpt-3.5-turbo"
        },
        "anthropic": {
            "primary": "claude-3-5-sonnet-20241022",  # Latest as of Feb 25, 2025
            "fallback": "claude-3-sonnet-20240229"
        }
    }
    
    @staticmethod
    def create(
        agent_type: str,
        instructions: str,
        functions: Optional[List[Callable]] = None,
        model: Optional[str] = None,
        tool_choice: Optional[str] = None,
        provider: Optional[str] = None
    ) -> BaseAgent:
        """
        Create an agent of the specified type.
        """
        agent_type = agent_type.lower()
        
        if provider is None:
            provider = "anthropic" if agent_type == "camille" else "openai"
        
        if model is None:
            model = AgentFactory.DEFAULT_MODELS[provider]["primary"]
        
        if agent_type == "zero":
            return ZeroAgent(
                instructions=instructions,
                functions=functions,
                model=model,
                tool_choice=tool_choice,
                provider=provider
            )
        elif agent_type == "gustave":
            return GustaveAgent(
                instructions=instructions,
                functions=functions,
                model=model,
                tool_choice=tool_choice,
                provider=provider
            )
        elif agent_type == "camille":
            return CamilleAgent(
                instructions=instructions,
                functions=functions,
                model=model,
                tool_choice=tool_choice,
                provider=provider
            )
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")
    
    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> BaseAgent:
        """
        Create an agent from a configuration dictionary.
        """
        if "type" not in config or "instructions" not in config:
            raise ValueError("Agent config missing 'type' or 'instructions' field")
        
        return AgentFactory.create(
            agent_type=config["type"],
            instructions=config["instructions"],
            functions=config.get("functions"),
            model=config.get("model"),
            tool_choice=config.get("tool_choice"),
            provider=config.get("provider")
        )

