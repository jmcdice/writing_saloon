"""
Camille agent implementation - the balanced and insightful reviewer.
"""
from typing import Dict, Any, List, Callable, Optional
import re

from .base import BaseAgent


class CamilleAgent(BaseAgent):
    """
    Camille is the balanced and insightful reviewer, providing nuanced feedback.
    
    Camille is characterized by balance, insight, and clarity. This agent offers
    thoughtful analysis of both structure and content, often finding middle ground
    between creativity and refinement. Ideal for evaluating proposals from multiple angles.
    """
    
    def __init__(
        self,
        instructions: str,
        functions: Optional[List[Callable]] = None,
        model: str = "claude-3-opus-20240229",
        tool_choice: Optional[str] = None,
        provider: str = "anthropic"
    ):
        """
        Initialize Camille agent.
        
        Args:
            instructions: System prompt/personality
            functions: List of callable functions
            model: The LLM model to use
            tool_choice: Optional tool selection parameter
            provider: The provider to use ("anthropic")
        """
        super().__init__(
            name="Camille",
            instructions=instructions,
            model=model,
            functions=functions,
            tool_choice=tool_choice,
            provider=provider
        )
    
    def process_response(self, content: str) -> Dict[str, Any]:
        """
        Process Camille's response to extract consensus and content.
        
        Looks for consensus markers and specific content patterns in Camille's
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
            "agent": "Camille"
        }
