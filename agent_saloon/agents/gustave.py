"""
Gustave agent implementation - the refined and eloquent editor.
"""
from typing import Dict, Any, List, Callable, Optional
import re

from .base import BaseAgent


class GustaveAgent(BaseAgent):
    """
    Gustave is the refined and eloquent editor, improving and polishing content.
    
    Gustave is characterized by sophistication, attention to detail, and a focus
    on refinement. This agent typically reviews and improves upon initial proposals
    from Zero, bringing a polished and elevated perspective.
    """
    
    def __init__(
        self,
        instructions: str,
        functions: Optional[List[Callable]] = None,
        model: str = "gpt-4",
        tool_choice: Optional[str] = None,
        provider: str = "openai"
    ):
        """
        Initialize Gustave agent.
        
        Args:
            instructions: System prompt/personality
            functions: List of callable functions
            model: The LLM model to use
            tool_choice: Optional tool selection parameter
            provider: The LLM provider to use (default: openai)
        """
        super().__init__(
            name="Gustave",
            instructions=instructions,
            model=model,
            functions=functions,
            tool_choice=tool_choice,
            provider=provider
        )
    
    def process_response(self, content: str) -> Dict[str, Any]:
        """
        Process Gustave's response to extract consensus and content.
        
        Looks for consensus markers and specific content patterns in Gustave's
        responses, extracting the refined content from the agent's output.
        
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
        
        # Keep full content with handoff markers to enable proper discussions
        # This ensures the complete discussion is visible for consensus detection
        return {
            "consensus": consensus,
            "content": content.strip(),
            "book_title": book_title,
            "raw_response": content,
            "agent": "Gustave"
        }
