"""
Zero agent implementation - the enthusiastic creative writer.
"""
from typing import Dict, Any, List, Callable, Optional
import re

from .base import BaseAgent


class ZeroAgent(BaseAgent):
    """
    Zero is the enthusiastic and creative writer, making initial proposals.
    
    Zero is characterized by creativity, enthusiasm, and a propensity
    for bold initial ideas. This agent typically starts the collaborative
    process with fresh, creative proposals.
    """
    
    def __init__(
        self,
        instructions: str,
        functions: Optional[List[Callable]] = None,
        model: str = "gpt-4",
        tool_choice: Optional[str] = None,
        provider: str = "openai"  # Add provider parameter with default
    ):
        """
        Initialize Zero agent.
        
        Args:
            instructions: System prompt/personality
            functions: List of callable functions
            model: The LLM model to use
            tool_choice: Optional tool selection parameter
            provider: AI provider to use ("openai" or "anthropic")
        """
        super().__init__(
            name="Zero",
            instructions=instructions,
            model=model,
            functions=functions,
            tool_choice=tool_choice,
            provider=provider  # Pass provider to BaseAgent
        )
    
    def process_response(self, content: str) -> Dict[str, Any]:
        """
        Process Zero's response to extract consensus and content.
        
        Looks for consensus markers and specific content patterns in Zero's
        responses, extracting the actual content from the agent's output.
        
        Args:
            content: Raw response from the agent
            
        Returns:
            Dictionary with processed information:
            {
                "consensus": True/False,
                "content": Extracted content,
                "raw_response": Original response
            }
        """
        # Extract consensus marker if present
        consensus = False
        if "Consensus: True" in content:
            consensus = True
        
        # Extract book title if present (for title generation)
        book_title = None
        title_match = re.search(r"Book Title: (.*?)(?:\n|$)", content)
        if title_match:
            book_title = title_match.group(1).strip()
        
        # Clean up the content to remove system markers
        clean_content = content
        # Remove any function call indicators
        clean_content = re.sub(r"HANDOFF: .*?(?:\n|$)", "", clean_content, flags=re.MULTILINE)
        
        return {
            "consensus": consensus,
            "content": clean_content.strip(),
            "book_title": book_title,
            "raw_response": content,
            "agent": "Zero"
        }
