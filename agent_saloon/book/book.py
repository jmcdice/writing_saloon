"""
Book class for managing the state and structure of a generated book.
"""
from typing import Dict, List, Any, Optional
import os
import json
from datetime import datetime

from .section import Section
from ..utils.logger import Logger


class Book:
    """
    Represents a book and manages its state during generation.
    
    This class serves as the central repository for all book state,
    including its title, table of contents, and section content.
    """
    
    def __init__(
        self,
        topic: str,
        title: Optional[str] = None,
        author: str = "AI Writing Team",
        logger: Optional[Logger] = None
    ):
        """
        Initialize a new book.
        
        Args:
            topic: The main topic of the book
            title: The book title (can be set later)
            author: The book author or authors
            logger: Logger instance for IRC-style logging
        """
        self.topic = topic
        self.title = title
        self.author = author
        self.logger = logger
        self.created_at = datetime.now()
        self.updated_at = self.created_at
        self.toc: List[Dict[str, Any]] = []
        self.sections: Dict[str, Section] = {}
        self.metadata: Dict[str, Any] = {
            "id": self._generate_id(),
            "status": "initialized"
        }
    
    def _generate_id(self) -> str:
        """
        Generate a unique identifier for the book.
        
        Returns:
            Unique identifier string
        """
        timestamp = int(datetime.now().timestamp())
        topic_slug = self.topic.lower().replace(" ", "-")[:30]
        return f"{topic_slug}-{timestamp}"
    
    def set_title(self, title: str):
        """
        Set the book title.
        
        Args:
            title: The book title
        """
        self.title = title
        self.updated_at = datetime.now()
        
        if self.logger:
            self.logger.success(f"Book title set: {title}")
    
    def set_toc(self, toc: List[Dict[str, Any]]):
        """
        Set the table of contents.
        
        Args:
            toc: Table of contents structure
        """
        self.toc = toc
        self.updated_at = datetime.now()
        
        # Initialize sections based on TOC
        self._initialize_sections()
        
        if self.logger:
            self.logger.success(f"Table of contents set with {len(toc)} chapters")
    
    def _initialize_sections(self):
        """Initialize section objects based on the table of contents."""
        section_number = 1
        
        for chapter_index, chapter in enumerate(self.toc):
            chapter_number = chapter_index + 1
            
            # Add chapter as a section
            chapter_id = f"{chapter_number}"
            if chapter_id not in self.sections:
                self.sections[chapter_id] = Section(
                    id=chapter_id,
                    title=chapter["title"],
                    level=1,
                    number=chapter_number
                )
            
            # Add sections within the chapter
            if "sections" in chapter:
                for section_index, section in enumerate(chapter["sections"]):
                    section_id = f"{chapter_number}.{section_index + 1}"
                    if section_id not in self.sections:
                        self.sections[section_id] = Section(
                            id=section_id,
                            title=section["title"],
                            level=2,
                            number=section_number
                        )
                        section_number += 1
                        
                        # Add subsections if any
                        if "subsections" in section:
                            for subsection_index, subsection in enumerate(section["subsections"]):
                                subsection_id = f"{section_id}.{subsection_index + 1}"
                                if subsection_id not in self.sections:
                                    self.sections[subsection_id] = Section(
                                        id=subsection_id,
                                        title=subsection["title"],
                                        level=3,
                                        number=section_number
                                    )
                                    section_number += 1
    
    def get_section(self, section_id: str) -> Optional[Section]:
        """
        Get a section by its ID.
        
        Args:
            section_id: Section identifier
            
        Returns:
            Section object, or None if not found
        """
        return self.sections.get(section_id)
    
    def update_section_content(self, section_id: str, content: str):
        """
        Update the content of a section.
        
        Args:
            section_id: Section identifier
            content: New section content
            
        Raises:
            ValueError: If section doesn't exist
        """
        if section_id not in self.sections:
            raise ValueError(f"Section {section_id} not found")
        
        self.sections[section_id].set_content(content)
        self.updated_at = datetime.now()
        
        if self.logger:
            self.logger.success(f"Updated content for section {section_id}")
    
    def get_progress(self) -> Dict[str, Any]:
        """
        Get the current progress of book generation.
        
        Returns:
            Dictionary with progress information
        """
        total_sections = len(self.sections)
        completed_sections = sum(1 for section in self.sections.values() if section.content)
        
        return {
            "total_sections": total_sections,
            "completed_sections": completed_sections,
            "progress_percentage": (completed_sections / total_sections * 100) if total_sections > 0 else 0,
            "has_title": bool(self.title),
            "has_toc": bool(self.toc)
        }
        
    def get_total_word_count(self) -> int:
        """
        Get the total word count across all sections.
        
        Returns:
            Total number of words in the book
        """
        return sum(section.get_word_count() for section in self.sections.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the book to a dictionary representation.
        
        Returns:
            Dictionary representation of the book
        """
        return {
            "id": self.metadata["id"],
            "topic": self.topic,
            "title": self.title,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "toc": self.toc,
            "sections": {id: section.to_dict() for id, section in self.sections.items()},
            "status": self.metadata["status"],
            "progress": self.get_progress(),
            "cover_image": self.metadata.get("cover_image", None)
        }
    
    def save(self, directory: str = "books"):
        """
        Save the book to disk.
        
        Args:
            directory: Base directory to save the book in
        """
        # Create book directory based on ID or title
        book_id = self.metadata["id"]
        book_dir = os.path.join(directory, book_id)
        os.makedirs(book_dir, exist_ok=True)
        
        # Save metadata
        metadata_path = os.path.join(book_dir, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        
        # Save title
        title_path = os.path.join(book_dir, "title.txt")
        with open(title_path, 'w', encoding='utf-8') as f:
            f.write(self.title or self.topic)
        
        # Save table of contents
        toc_path = os.path.join(book_dir, "table_of_contents.json")
        with open(toc_path, 'w', encoding='utf-8') as f:
            json.dump(self.toc, f, indent=2)
        
        # Create sections directory
        sections_dir = os.path.join(book_dir, "sections")
        os.makedirs(sections_dir, exist_ok=True)
        
        # Save each section
        for section_id, section in self.sections.items():
            section_path = os.path.join(sections_dir, f"{section_id}.txt")
            with open(section_path, 'w', encoding='utf-8') as f:
                f.write(section.content or f"# {section.title}\n\n[Content not yet generated]")
        
        if self.logger:
            self.logger.success(f"Book saved to {book_dir}")
        
        return book_dir
    
    @classmethod
    def load(cls, book_id: str, directory: str = "books", logger: Optional[Logger] = None) -> 'Book':
        """
        Load a book from disk.
        
        Args:
            book_id: Book identifier
            directory: Base directory where books are stored
            logger: Logger instance
            
        Returns:
            Loaded Book instance
            
        Raises:
            FileNotFoundError: If book doesn't exist
        """
        book_dir = os.path.join(directory, book_id)
        if not os.path.exists(book_dir):
            raise FileNotFoundError(f"Book directory not found: {book_dir}")
        
        # Load metadata
        metadata_path = os.path.join(book_dir, "metadata.json")
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        # Create book instance
        book = cls(
            topic=metadata["topic"],
            title=metadata["title"],
            author=metadata["author"],
            logger=logger
        )
        
        # Restore metadata
        book.metadata = {
            "id": metadata["id"],
            "status": metadata["status"]
        }
        book.created_at = datetime.fromisoformat(metadata["created_at"])
        book.updated_at = datetime.fromisoformat(metadata["updated_at"])
        
        # Load table of contents
        book.toc = metadata["toc"]
        
        # Initialize sections
        book._initialize_sections()
        
        # Load section content
        sections_dir = os.path.join(book_dir, "sections")
        if os.path.exists(sections_dir):
            for section_id, section in book.sections.items():
                section_path = os.path.join(sections_dir, f"{section_id}.txt")
                if os.path.exists(section_path):
                    with open(section_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        section.set_content(content)
        
        if logger:
            logger.success(f"Book loaded from {book_dir}")
        
        return book
