"""
Section content generator for collaborative book section writing.
"""
from typing import Dict, List, Any, Optional
import re

from ..agents.base import BaseAgent
from .base_generator import BaseGenerator
from ..utils.logger import Logger


class SectionGenerator(BaseGenerator):
    """
    Generator for creating section content through agent collaboration.
    
    This generator uses collaboration between agents to create
    detailed and refined content for individual book sections.
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        max_attempts: int = 10,
        force_consensus: bool = True,
        logger: Optional[Logger] = None
    ):
        """
        Initialize a section content generator.
        
        Args:
            agents: List of agents to use for generation
            max_attempts: Maximum number of collaboration attempts
            force_consensus: Whether to force consensus after max attempts
            logger: Logger instance for IRC-style logging
        """
        super().__init__(agents, max_attempts, force_consensus, logger)
    
    def generate_section_content(
        self,
        book_title: str,
        section_id: str,
        section_title: str,
        previous_section_titles: Optional[List[str]] = None,
        parent_title: Optional[str] = None,
        min_words: int = 500,
        max_words: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate content for a book section.
        
        Args:
            book_title: Title of the book
            section_id: Section identifier (e.g., "1.2")
            section_title: Title of the section
            previous_section_titles: Titles of previous sections for context
            parent_title: Title of the parent chapter/section
            min_words: Minimum word count
            max_words: Maximum word count
            
        Returns:
            Dictionary containing:
            {
                "content": The generated section content
                "success": Whether generation was successful
                "consensus": Whether consensus was reached
                "forced_consensus": Whether consensus was forced
                "attempts": Number of attempts made
                "word_count": Word count of the generated content
            }
        """
        if self.logger:
            self.logger.system_message(f"Generating content for section: {section_title}")
        
        # Create context string for previous sections
        context_str = ""
        if previous_section_titles:
            context_str = "Previous sections in this chapter:\n- "
            context_str += "\n- ".join(previous_section_titles)
        
        # Create a prompt for generating the section content
        prompt = (
            f"Let's collaborate on writing the content for section '{section_title}' "
            f"(section {section_id}) of the book '{book_title}'. "
        )
        
        if parent_title:
            prompt += f"This section is part of the chapter '{parent_title}'. "
        
        prompt += (
            f"The content should be between {min_words} and {max_words} words, "
            f"well-structured, informative, and engaging. "
            f"Focus on providing valuable content for the reader. "
        )
        
        if context_str:
            prompt += f"\n\n{context_str}"
        
        context_variables = {
            "book_title": book_title,
            "section_id": section_id,
            "section_title": section_title,
            "parent_title": parent_title,
            "min_words": min_words,
            "max_words": max_words,
            "previous_section_titles": previous_section_titles
        }
        
        result = self.generate(prompt, context_variables)
        
        # Clean the content
        content = self._clean_content(result["content"])
        
        # Calculate word count
        word_count = len(content.split())
        
        if self.logger:
            self.logger.success(f"Generated section content with {word_count} words")
        
        return {
            "content": content,
            "success": result["success"],
            "consensus": result["consensus"],
            "forced_consensus": result["forced_consensus"],
            "attempts": result["attempts"],
            "word_count": word_count,
            "messages": result["messages"],
            "duration": result["duration"]
        }

    def _clean_content(self, content: str) -> str:
        """
        Clean the generated content by extracting only content within <content> tags.
        
        Args:
            content: Raw generated content
            
        Returns:
            Cleaned content
        """
        # Store the current section title for potential heading insertion
        section_title = getattr(self, 'current_section_title', None)
        
        # Extract content from <content> tags
        content_match = re.search(r'<content>(.*?)</content>', content, re.DOTALL | re.IGNORECASE)
        if content_match:
            content = content_match.group(1).strip()
        else:
            # Fallback: clean content the traditional way if no content tags found
            # Remove agent commentary
            for agent in ["zero", "gustave", "camille"]:
                pattern = f"<{agent}>.*?</{agent}>"
                content = re.sub(pattern, "", content, flags=re.DOTALL | re.IGNORECASE)
            
            # Remove consensus markers
            content = re.sub(r'(?i)Consensus:\s*(?:true|false).*?(?=\n|$)', '', content)
            
            # Remove handoff markers
            content = re.sub(r'(?i)HANDOFF:.*?(?=\n|$)', '', content)
            
            # Remove book title markers
            content = re.sub(r'(?i)Book Title:.*?(?=\n|$)', '', content)
            
            # Log a warning about missing content tags
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning(f"No <content> tags found in response. Using fallback cleaning method.")
        
        # Remove unnecessary whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Strip leading/trailing whitespace
        content = content.strip()
        
        # If the content doesn't start with a heading and we know the section title, add it
        if content and not content.startswith('#') and section_title:
            content = f"# {section_title}\n\n{content}"
        
        return content
    
    def _process_generation_result(self, result: Dict[str, Any]) -> str:
        """
        Process the raw generation result into clean section content.
        
        Args:
            result: Raw generation result from generate()
            
        Returns:
            Cleaned section content
        """
        return self._clean_content(result["content"])
    
    def execute(
        self,
        book_title: str,
        section_id: str,
        section_title: str,
        previous_section_titles: Optional[List[str]] = None,
        parent_title: Optional[str] = None,
        min_words: int = 500,
        max_words: int = 2000,
        context_variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Execute the section content generation process and return the content.
        
        Args:
            book_title: Title of the book
            section_id: Section identifier (e.g., "1.2")
            section_title: Title of the section
            previous_section_titles: Titles of previous sections for context
            parent_title: Title of the parent chapter/section
            min_words: Minimum word count
            max_words: Maximum word count
            context_variables: Optional context variables
            
        Returns:
            The generated section content
        """
        # Store current section title for heading insertion if needed
        self.current_section_title = section_title
        
        # Create a prompt for generating the section content
        prompt = (
            f"Let's collaborate on writing the content for section '{section_title}' "
            f"(section {section_id}) of the book '{book_title}'. "
        )
        
        if parent_title:
            prompt += f"This section is part of the chapter '{parent_title}'. "
        
        prompt += (
            f"The content should be between {min_words} and {max_words} words, "
            f"well-structured, informative, and engaging. "
            f"Focus on providing valuable content for the reader. "
        )
        
        # Create context string for previous sections
        if previous_section_titles:
            context_str = "Previous sections in this chapter:\n- "
            context_str += "\n- ".join(previous_section_titles)
            prompt += f"\n\n{context_str}"
        
        # Prepare context variables
        context = {
            "book_title": book_title,
            "section_id": section_id,
            "section_title": section_title,
            "parent_title": parent_title,
            "min_words": min_words,
            "max_words": max_words,
            "previous_section_titles": previous_section_titles
        }
        
        if context_variables:
            context.update(context_variables)
        
        result = self.generate(prompt, context)
        return self._process_generation_result(result)
