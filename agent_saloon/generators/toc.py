"""
Table of contents generator for collaborative book structure creation.
"""
from typing import Dict, List, Any, Optional
import re
import json

from ..agents.base import BaseAgent
from .base_generator import BaseGenerator
from ..utils.logger import Logger


class TableOfContentsGenerator(BaseGenerator):
    """
    Generator for creating book table of contents through agent collaboration.
    
    This generator uses collaboration between agents to create a structured
    and cohesive table of contents based on a book title and topic.
    """
    
    def __init__(
        self,
        agents: List[BaseAgent],
        max_attempts: int = 10,
        force_consensus: bool = True,
        logger: Optional[Logger] = None
    ):
        """
        Initialize a table of contents generator.
        
        Args:
            agents: List of agents to use for generation
            max_attempts: Maximum number of collaboration attempts
            force_consensus: Whether to force consensus after max attempts
            logger: Logger instance for IRC-style logging
        """
        super().__init__(agents, max_attempts, force_consensus, logger)
    
    def generate_toc(
        self,
        title: str,
        topic: str,
        min_chapters: int = 5,
        max_chapters: int = 10
    ) -> Dict[str, Any]:
        """
        Generate a table of contents for the given book title and topic.
        
        Args:
            title: Book title
            topic: Book topic
            min_chapters: Minimum number of chapters
            max_chapters: Maximum number of chapters
            
        Returns:
            Dictionary containing:
            {
                "toc": The generated table of contents
                "success": Whether generation was successful
                "consensus": Whether consensus was reached
                "forced_consensus": Whether consensus was forced
                "attempts": Number of attempts made
            }
        """
        if self.logger:
            self.logger.system_message(f"Generating table of contents for: {title}")
        
        prompt = (
            f"Let's collaborate on a detailed table of contents for a book titled '{title}' "
            f"about {topic}. The book should have between {min_chapters} and {max_chapters} "
            f"chapters, each with 2-5 sections. Structure the TOC in a clear format that "
            f"can be parsed as JSON, with chapters and sections."
        )
        
        context_variables = {
            "book_title": title,
            "book_topic": topic,
            "min_chapters": min_chapters,
            "max_chapters": max_chapters
        }
        
        result = self.generate(prompt, context_variables)
        
        # Extract the TOC from the result
        toc = self._extract_toc(result["content"])
        
        # Validate and fix TOC if needed
        if not toc or len(toc) < min_chapters:
            if self.logger:
                self.logger.warning(f"Invalid TOC extracted, attempting to fix")
            toc = self._fix_toc(result["content"], min_chapters, max_chapters)
        
        if self.logger:
            self.logger.success(f"Generated table of contents with {len(toc)} chapters")
        
        return {
            "toc": toc,
            "success": result["success"],
            "consensus": result["consensus"],
            "forced_consensus": result["forced_consensus"],
            "attempts": result["attempts"],
            "messages": result["messages"],
            "duration": result["duration"]
        }

    def _extract_toc(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract the table of contents from the generated content.
        
        Args:
            content: Generated content from agent collaboration
            
        Returns:
            Structured table of contents as a list of chapter dictionaries
        """
        # First try to extract from <content> tags
        content_match = re.search(r'<content>(.*?)</content>', content, re.DOTALL | re.IGNORECASE)
        if content_match:
            clean_content = content_match.group(1).strip()
            
            # Try to parse as JSON
            try:
                data = json.loads(clean_content)
                # Check if this looks like a TOC (list of chapters)
                if isinstance(data, list) and all(isinstance(item, dict) and "title" in item for item in data):
                    return data
                # Check if this looks like a TOC with a 'chapters' key
                elif isinstance(data, dict) and "chapters" in data and isinstance(data["chapters"], list):
                    return data["chapters"]
            except json.JSONDecodeError:
                # If JSON parsing fails, continue with other extraction methods
                pass
        
        # If no content tags or JSON parsing failed, try to find JSON blocks in the content
        json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
        json_matches = re.findall(json_pattern, content)
        
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                # Check if this looks like a TOC (list of chapters)
                if isinstance(data, list) and all(isinstance(item, dict) and "title" in item for item in data):
                    return data
                # Check if this looks like a TOC with a 'chapters' key
                elif isinstance(data, dict) and "chapters" in data and isinstance(data["chapters"], list):
                    return data["chapters"]
            except json.JSONDecodeError:
                continue
        
        # If no JSON blocks found, try to parse the structure from text
        return self._parse_text_toc(content)
    
    def _parse_text_toc(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse a table of contents from text format.
        
        Args:
            content: Text content to parse
            
        Returns:
            Structured table of contents
        """
        lines = content.strip().split('\n')
        toc = []
        current_chapter = None
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check for chapter pattern (Chapter 1: Title or 1. Title)
            chapter_match = re.search(r'^(?:Chapter\s+)?(\d+)[:.]\s+(.*)', line)
            if chapter_match:
                # Start a new chapter
                if current_chapter:
                    toc.append(current_chapter)
                
                current_chapter = {
                    "title": chapter_match.group(2).strip(),
                    "sections": []
                }
                current_section = None
                continue
            
            # Check for section pattern (1.1 Title)
            section_match = re.search(r'^(\d+\.\d+)[:.]\s+(.*)', line)
            if section_match and current_chapter:
                # Start a new section
                current_section = {
                    "title": section_match.group(2).strip(),
                    "subsections": []
                }
                current_chapter["sections"].append(current_section)
                continue
            
            # Check for subsection pattern (1.1.1 Title)
            subsection_match = re.search(r'^(\d+\.\d+\.\d+)[:.]\s+(.*)', line)
            if subsection_match and current_section:
                # Add a subsection
                current_section["subsections"].append({
                    "title": subsection_match.group(2).strip()
                })
        
        # Add the last chapter if there is one
        if current_chapter:
            toc.append(current_chapter)
        
        return toc
    
    def _fix_toc(
        self,
        content: str,
        min_chapters: int,
        max_chapters: int
    ) -> List[Dict[str, Any]]:
        """
        Attempt to fix an invalid or missing TOC.
        
        Args:
            content: Original content
            min_chapters: Minimum number of chapters
            max_chapters: Maximum number of chapters
            
        Returns:
            Fixed table of contents
        """
        # First try to parse any structure from the text
        toc = self._parse_text_toc(content)
        
        # If still invalid, create a basic structure
        if not toc or len(toc) < min_chapters:
            # Generate chapter titles from the content if possible
            titles = re.findall(r'"([^"]+)"', content)
            titles = [title for title in titles if len(title.split()) < 10]
            
            # Use the found titles or generate generic ones
            toc = []
            for i in range(min(max_chapters, max(min_chapters, len(titles)))):
                title = titles[i] if i < len(titles) else f"Chapter {i+1}"
                toc.append({
                    "title": title,
                    "sections": [
                        {"title": f"Section {j+1}", "subsections": []}
                        for j in range(3)  # 3 sections per chapter
                    ]
                })
        
        return toc
    
    def _process_generation_result(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process the raw generation result into a table of contents.
        
        Args:
            result: Raw generation result from generate()
            
        Returns:
            Structured table of contents
        """
        return self._extract_toc(result["content"])
    
    def execute(
        self,
        title: str,
        topic: str,
        min_chapters: int = 5,
        max_chapters: int = 10,
        context_variables: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute the TOC generation process and return the TOC.
        
        Args:
            title: Book title
            topic: Book topic
            min_chapters: Minimum number of chapters
            max_chapters: Maximum number of chapters
            context_variables: Optional context variables
            
        Returns:
            The generated table of contents
        """
        prompt = (
            f"Let's collaborate on a detailed table of contents for a book titled '{title}' "
            f"about {topic}. The book should have between {min_chapters} and {max_chapters} "
            f"chapters, each with 2-5 sections. Structure the TOC in a clear format that "
            f"can be parsed as JSON, with chapters and sections."
        )
        
        context = {
            "book_title": title,
            "book_topic": topic,
            "min_chapters": min_chapters,
            "max_chapters": max_chapters
        }
        
        if context_variables:
            context.update(context_variables)
        
        result = self.generate(prompt, context)
        return self._process_generation_result(result)
