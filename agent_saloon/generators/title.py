"""
Title generator for collaborative book title creation.
"""
from typing import Dict, List, Any, Optional
import re

from ..agents.base import BaseAgent
from .base_generator import BaseGenerator
from ..utils.logger import Logger


class TitleGenerator(BaseGenerator):
    """
    Generator for creating book titles through agent collaboration.
    
    This generator uses the collaboration between agents to create
    compelling and refined book titles based on a given topic.
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        max_attempts: int = 10,
        force_consensus: bool = True,
        logger: Optional[Logger] = None
    ):
        """
        Initialize a title generator.
        
        Args:
            agents: List of agents to use for generation
            max_attempts: Maximum number of collaboration attempts
            force_consensus: Whether to force consensus after max attempts
            logger: Logger instance for IRC-style logging
        """
        super().__init__(agents, max_attempts, force_consensus, logger)
    
    def generate_title(self, topic: str) -> Dict[str, Any]:
        """
        Generate a book title for the given topic.
        
        Args:
            topic: The topic for which to generate a title
            
        Returns:
            Dictionary containing:
            {
                "title": The generated title
                "success": Whether generation was successful
                "consensus": Whether consensus was reached
                "forced_consensus": Whether consensus was forced
                "attempts": Number of attempts made
            }
        """
        if self.logger:
            self.logger.system_message(f"Generating title for topic: {topic}")
        
        prompt = f"Let's collaborate on a title for a book about: {topic}"
        result = self.generate(prompt)
        
        # Extract the title from the result
        title = self._extract_title(result["content"])
        
        # Use topic as fallback if title extraction failed
        if not title:
            if self.logger:
                self.logger.warning("Failed to extract title, using topic as fallback")
            title = f"Book about {topic}"
        
        if self.logger:
            self.logger.success(f"Final book title: {title}")
        
        return {
            "title": title,
            "success": result["success"],
            "consensus": result["consensus"],
            "forced_consensus": result["forced_consensus"],
            "attempts": result["attempts"],
            "messages": result["messages"],
            "duration": result["duration"]
        }
    
    def _extract_title(self, content: str) -> Optional[str]:
        """
        Extract the book title from the generated content.
        
        Args:
            content: Generated content from agent collaboration
            
        Returns:
            Extracted book title, or None if not found
        """
        # Try to find explicit title markers
        title_match = re.search(r"Book Title:\s*(.*?)(?:\n|$)", content, re.IGNORECASE)
        if title_match:
            return title_match.group(1).strip()
        
        # If no explicit markers, look for quoted titles
        quoted_match = re.search(r'["\'](.*?)["\']', content)
        if quoted_match:
            return quoted_match.group(1).strip()
        
        # Look for lines that might contain a title
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            # Skip obvious non-title lines
            if not line or line.startswith(('I think', 'I suggest', 'Consensus', 'HANDOFF')):
                continue
            if len(line) < 100 and not line.endswith(('.', '?', '!')):
                return line
        
        # Check for title in metadata
        if "book_title" in self.coordinator.messages[-1].get("metadata", {}):
            return self.coordinator.messages[-1]["metadata"]["book_title"]
        
        return None
    
    def _process_generation_result(self, result: Dict[str, Any]) -> str:
        """
        Process the raw generation result into a title.
        
        Args:
            result: Raw generation result from generate()
            
        Returns:
            Extracted book title
        """
        title = self._extract_title(result["content"])
        
        # Use metadata if available and title extraction failed
        if not title and "book_title" in result.get("metadata", {}):
            title = result["metadata"]["book_title"]
        
        # Fallback
        if not title:
            title = "Untitled Book"
        
        return title
    
    def execute(
        self,
        topic: str,
        context_variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute the title generation process and return the title.
        
        Args:
            topic: The topic for which to generate a title
            context_variables: Optional context variables
            
        Returns:
            The generated book title
        """
        prompt = f"Let's collaborate on a title for a book about: {topic}"
        result = self.generate(prompt, context_variables)
        return self._process_generation_result(result)
