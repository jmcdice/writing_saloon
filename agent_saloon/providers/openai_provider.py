"""
OpenAI provider implementation.
"""
from typing import Dict, List, Any, Optional, Callable
import os

from openai import OpenAI

from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    """
    OpenAI provider implementation.
    
    This class handles communication with the OpenAI API for
    generating responses using GPT models.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
        
        self.client = OpenAI(api_key=self.api_key)
    
    def generate_response(
        self,
        instructions: str,
        messages: List[Dict[str, str]],
        functions: Optional[List[Callable]] = None,
        temperature: float = 0.7,
        context_variables: Optional[Dict[str, Any]] = None,
        model: str = "gpt-4"  # Add model parameter with default
    ) -> Dict[str, Any]:
        """
        Generate a response using the OpenAI API.
        
        Args:
            instructions: System prompt/instructions
            messages: List of message objects with role and content
            functions: Optional list of functions the model can call
            temperature: Sampling temperature
            context_variables: Optional context to pass to the model
            model: The OpenAI model to use (defaults to gpt-4)
            
        Returns:
            Dictionary containing the response content and metadata
        """
        # Create a copy of messages to avoid modifying the original
        formatted_messages = [{"role": "system", "content": instructions}]
        formatted_messages.extend(messages)
        
        # Prepare the API call parameters
        api_params = {
            "model": model,  # Use the passed model
            "messages": formatted_messages,
            "temperature": temperature
        }
        
        # Only include functions if the list is non-empty
        if functions and len(functions) > 0:
            api_params["functions"] = functions
        
        # Make the API call
        response = self.client.chat.completions.create(**api_params)
        
        # Extract and return the response
        return {
            "content": response.choices[0].message.content,
            "raw_response": response,
            "provider": "openai",
            "model": model  # Return the actual model used
        }
    
    @property
    def provider_name(self) -> str:
        """Get the name of this provider."""
        return "openai"
    
    @property
    def available_models(self) -> List[str]:
        """Get a list of available models from this provider."""
        return ["gpt-4", "gpt-3.5-turbo"]

