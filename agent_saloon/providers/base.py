"""
Base provider interface for different AI providers.
"""
from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """
    Abstract base class for AI providers (OpenAI, Anthropic, etc.)
    
    This class defines the interface that all provider implementations
    must follow, ensuring compatibility across different AI APIs.
    """
    
    @abstractmethod
    def generate_response(
        self,
        instructions: str,
        messages: List[Dict[str, str]],
        functions: Optional[List[Callable]] = None,
        temperature: float = 0.7,
        context_variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a response from the AI provider.
        
        Args:
            instructions: System prompt/instructions
            messages: List of message objects with role and content
            functions: Optional list of functions the model can call
            temperature: Sampling temperature
            context_variables: Optional context to pass to the model
            
        Returns:
            Dictionary containing the response content and metadata
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get the name of this provider."""
        pass
    
    @property
    @abstractmethod
    def available_models(self) -> List[str]:
        """Get a list of available models from this provider."""
        pass
