"""
Section class for representing a section within a book.
"""
from typing import Dict, Any, Optional
from datetime import datetime


class Section:
    """
    Represents a section within a book.
    
    A section can be a chapter, a subsection, or any other
    hierarchical unit within the book structure.
    """
    
    def __init__(
        self,
        id: str,
        title: str,
        level: int = 1,
        number: int = 1,
        content: Optional[str] = None
    ):
        """
        Initialize a new section.
        
        Args:
            id: Unique identifier for the section (e.g., "1.2.3")
            title: Section title
            level: Hierarchical level (1 = chapter, 2 = section, 3 = subsection)
            number: Section number for ordering
            content: Optional section content
        """
        self.id = id
        self.title = title
        self.level = level
        self.number = number
        self.content = content
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.metadata: Dict[str, Any] = {}
    
    def set_content(self, content: str):
        """
        Set the section content.
        
        Args:
            content: Section content text
        """
        self.content = content
        self.updated_at = datetime.now()
    
    def get_heading(self) -> str:
        """
        Get the section heading with appropriate Markdown formatting.
        
        Returns:
            Formatted heading string
        """
        # Create heading with the appropriate number of # symbols
        heading_level = "#" * self.level
        return f"{heading_level} {self.title}"
    
    def get_full_content(self) -> str:
        """
        Get the full section content including heading.
        
        Returns:
            Full formatted content
        """
        heading = self.get_heading()
        content = self.content or "[Content not yet generated]"
        return f"{heading}\n\n{content}"
    
    def get_word_count(self) -> int:
        """
        Get the word count for the section content.
        
        Returns:
            Number of words in the section
        """
        if not self.content:
            return 0
        
        # Simple word count by splitting on whitespace
        return len(self.content.split())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the section to a dictionary representation.
        
        Returns:
            Dictionary representation of the section
        """
        return {
            "id": self.id,
            "title": self.title,
            "level": self.level,
            "number": self.number,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "word_count": self.get_word_count(),
            "metadata": self.metadata
        }
    
    def __repr__(self) -> str:
        """String representation of the section."""
        content_preview = f"{self.content[:30]}..." if self.content else "[Empty]"
        return f"Section({self.id}: {self.title} - {content_preview})"
