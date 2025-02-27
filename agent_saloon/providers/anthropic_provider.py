"""
Anthropic provider implementation.
"""
from typing import Dict, List, Any, Optional, Callable
import os
import json

import anthropic

from .base import BaseProvider


class AnthropicProvider(BaseProvider):
    """
    Anthropic provider implementation.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Anthropic provider.
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or pass it directly.")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def generate_response(
        self,
        instructions: str,
        messages: List[Dict[str, str]],
        functions: Optional[List[Callable]] = None,
        temperature: float = 0.7,
        context_variables: Optional[Dict[str, Any]] = None,
        model: str = "claude-3-5-sonnet-20241022",
        max_tokens: int = 2048  # Increased for TOC
    ) -> Dict[str, Any]:
        """
        Generate a response using the Anthropic API.
        """
        system = instructions
        
        anthropic_messages = []
        for msg in messages:
            if msg["role"] == "user":
                anthropic_messages.append({"role": "user", "content": msg["content"].strip()})
            elif msg["role"] == "assistant":
                anthropic_messages.append({"role": "assistant", "content": msg["content"].strip()})
        
        if not anthropic_messages or all(msg["role"] == "assistant" for msg in anthropic_messages):
            user_content = "Let's begin the task."
            if context_variables:
                user_content = f"Let's begin with this context: {json.dumps(context_variables)}"
            anthropic_messages.insert(0, {"role": "user", "content": user_content.strip()})
        
        # Debug logging
        print(f"DEBUG: Anthropic request - system: {system}")
        print(f"DEBUG: Anthropic request - messages: {json.dumps(anthropic_messages, indent=2)}")
        
        response = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=anthropic_messages,
            temperature=temperature,
        )
        
        print(f"DEBUG: Anthropic response.content = {response.content}")
        
        content = "No response generated by Anthropic model." if not response.content else response.content[0].text
        
        return {
            "content": content,
            "raw_response": response,
            "provider": "anthropic",
            "model": model
        }
    
    @property
    def provider_name(self) -> str:
        """Get the name of this provider."""
        return "anthropic"
    
    @property
    def available_models(self) -> List[str]:
        """Get a list of available models from this provider."""
        return [
            "claude-3-5-sonnet",  # Latest
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ]
