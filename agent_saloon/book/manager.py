"""
Book manager for coordinating the entire book generation process.
"""
from typing import Dict, List, Any, Optional
import os
import time
import json
import requests
from urllib.parse import urlparse

from ..agents.base import BaseAgent
from ..agents.factory import AgentFactory
from ..generators.title import TitleGenerator
from ..generators.toc import TableOfContentsGenerator
from ..generators.section import SectionGenerator
from ..prompts.title_prompts import ZERO_TITLE_PROMPT, GUSTAVE_TITLE_PROMPT, CAMILLE_TITLE_PROMPT
from ..prompts.toc_prompts import ZERO_TOC_PROMPT, GUSTAVE_TOC_PROMPT, CAMILLE_TOC_PROMPT
from ..prompts.section_prompts import ZERO_SECTION_PROMPT, GUSTAVE_SECTION_PROMPT, CAMILLE_SECTION_PROMPT
from ..providers.openai_provider import OpenAIProvider
from .book import Book
from ..utils.logger import Logger


class BookManager:
    """
    Manager for coordinating the entire book generation process.
    
    This class ties together all the components needed to generate a complete
    book, from title to table of contents to section content.
    """
    
    # Maps agent types to prompt types
    PROMPT_MAPPING = {
        "zero": {
            "title": ZERO_TITLE_PROMPT,
            "toc": ZERO_TOC_PROMPT,
            "section": ZERO_SECTION_PROMPT
        },
        "gustave": {
            "title": GUSTAVE_TITLE_PROMPT,
            "toc": GUSTAVE_TOC_PROMPT,
            "section": GUSTAVE_SECTION_PROMPT
        },
        "camille": {
            "title": CAMILLE_TITLE_PROMPT,
            "toc": CAMILLE_TOC_PROMPT,
            "section": CAMILLE_SECTION_PROMPT
        }
    }
    
    def __init__(
        self,
        logger: Optional[Logger] = None,
        output_dir: str = "books",
        save_intermediate: bool = True,
        agent_list: Optional[List[str]] = None,
        provider_mapping: Optional[Dict[str, str]] = None,
        openai_api_key: Optional[str] = None,
        anthropic_api_key: Optional[str] = None
    ):
        """
        Initialize a book manager.
        
        Args:
            logger: Logger instance for IRC-style logging
            output_dir: Directory to save generated books
            save_intermediate: Whether to save intermediate results
            agent_list: List of agent types to use (defaults to ["zero", "gustave"])
            provider_mapping: Mapping of agent types to providers
            openai_api_key: OpenAI API key
            anthropic_api_key: Anthropic API key
        """
        self.logger = logger
        self.output_dir = output_dir
        self.save_intermediate = save_intermediate
        self.agent_list = agent_list or ["zero", "gustave"]
        self.provider_mapping = provider_mapping or {
            "zero": "openai",
            "gustave": "openai",
            "camille": "anthropic"
        }
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Validate agent list
        for agent_type in self.agent_list:
            if agent_type not in self.PROMPT_MAPPING:
                if self.logger:
                    self.logger.warning(f"Unknown agent type: {agent_type}")
    
    def create_agents(self, agent_types: List[str], prompt_type: str) -> List[BaseAgent]:
        """
        Create the agents used for book generation.
        
        Args:
            agent_types: List of agent types to create
            prompt_type: Type of prompt to use ("title", "toc", or "section")
            
        Returns:
            List of agent instances
        """
        agents = []
        
        for agent_type in agent_types:
            if agent_type not in self.PROMPT_MAPPING:
                if self.logger:
                    self.logger.warning(f"Skipping unknown agent type: {agent_type}")
                continue
            
            prompt = self.PROMPT_MAPPING[agent_type][prompt_type]
            provider = self.provider_mapping.get(agent_type)
            
            agent = AgentFactory.create(
                agent_type=agent_type,
                instructions=prompt,
                provider=provider
            )
            
            agents.append(agent)
        
        return agents
    
    def generate_book(
        self,
        topic: str,
        title: Optional[str] = None,
        toc: Optional[List[Dict[str, Any]]] = None,
        min_chapters: int = 5,
        max_chapters: int = 10,
        min_words_per_section: int = 500,
        max_words_per_section: int = 2000,
        section_ids: Optional[List[str]] = None
    ) -> Book:
        """
        Generate a complete book on the given topic.
        
        Args:
            topic: The main topic of the book
            title: Optional title (will be generated if None)
            toc: Optional table of contents (will be generated if None)
            min_chapters: Minimum number of chapters for TOC generation
            max_chapters: Maximum number of chapters for TOC generation
            min_words_per_section: Minimum words per section
            max_words_per_section: Maximum words per section
            section_ids: Specific section IDs to generate (all if None)
            
        Returns:
            The generated book
        """
        start_time = time.time()
        
        # Create the book object
        book = Book(topic=topic, title=title, logger=self.logger)
        
        if self.logger:
            self.logger.system_message(f"Starting book generation for topic: {topic}")
            self.logger.system_message(f"Using agents: {', '.join(self.agent_list)}")
        
        # Step 1: Generate title if not provided
        if not title:
            if self.logger:
                self.logger.system_message("Step 1: Generating book title")
            
            title_agents = self.create_agents(self.agent_list, "title")
            
            title_generator = TitleGenerator(
                agents=title_agents,
                logger=self.logger
            )
            
            title_result = title_generator.generate_title(topic)
            book.set_title(title_result["title"])
            
            if self.save_intermediate:
                book.save(self.output_dir)
        
        # Step 2: Generate table of contents if not provided
        if not toc:
            if self.logger:
                self.logger.system_message("Step 2: Generating table of contents")
            
            toc_agents = self.create_agents(self.agent_list, "toc")
            
            toc_generator = TableOfContentsGenerator(
                agents=toc_agents,
                logger=self.logger
            )
            
            toc_result = toc_generator.generate_toc(
                title=book.title,
                topic=topic,
                min_chapters=min_chapters,
                max_chapters=max_chapters
            )
            
            book.set_toc(toc_result["toc"])
            
            if self.save_intermediate:
                book.save(self.output_dir)
        
        # Step 3: Generate section content
        if self.logger:
            self.logger.system_message("Step 3: Generating section content")
        
        section_agents = self.create_agents(self.agent_list, "section")
        
        section_generator = SectionGenerator(
            agents=section_agents,
            logger=self.logger
        )
        
        # Determine which sections to generate
        if section_ids:
            sections_to_generate = [s for s in book.sections.values() if s.id in section_ids]
        else:
            sections_to_generate = list(book.sections.values())
        
        # Generate content for each section
        for section in sections_to_generate:
            if self.logger:
                self.logger.system_message(f"Generating content for section {section.id}: {section.title}")
            
            # Get parent title if applicable
            parent_id = ".".join(section.id.split(".")[:-1]) if "." in section.id else None
            parent_title = book.sections[parent_id].title if parent_id and parent_id in book.sections else None
            
            # Get previous section titles for context
            section_id_parts = section.id.split(".")
            if len(section_id_parts) > 1:
                # For sections within chapters, get previous sections in the same chapter
                chapter_id = section_id_parts[0]
                section_num = int(section_id_parts[1]) if len(section_id_parts) > 1 else 0
                
                previous_sections = [
                    s for s in book.sections.values()
                    if s.id.startswith(f"{chapter_id}.") and
                    len(s.id.split(".")) == 2 and
                    int(s.id.split(".")[1]) < section_num
                ]
                
                previous_titles = [s.title for s in previous_sections]
            else:
                # For chapters, no previous context
                previous_titles = None
            
            # Generate the section content
            content_result = section_generator.generate_section_content(
                book_title=book.title,
                section_id=section.id,
                section_title=section.title,
                previous_section_titles=previous_titles,
                parent_title=parent_title,
                min_words=min_words_per_section,
                max_words=max_words_per_section
            )
            
            # Update the section with the generated content
            book.update_section_content(section.id, content_result["content"])
            
            if self.save_intermediate:
                book.save(self.output_dir)
        
        # Save the final book
        book_dir = book.save(self.output_dir)
        
        end_time = time.time()
        duration = end_time - start_time
        
        if self.logger:
            self.logger.success(f"Book generation completed in {duration:.2f} seconds")
            self.logger.success(f"Book saved to {book_dir}")
        
        return book
    
    def continue_book_generation(
        self,
        book_id: str,
        section_ids: Optional[List[str]] = None,
        min_words_per_section: int = 500,
        max_words_per_section: int = 2000
    ) -> Book:
        """
        Continue generating content for an existing book.
        
        Args:
            book_id: ID of the book to continue
            section_ids: Specific section IDs to generate (all missing if None)
            min_words_per_section: Minimum words per section
            max_words_per_section: Maximum words per section
            
        Returns:
            The updated book
        """
        # Load the existing book
        book = Book.load(book_id, directory=self.output_dir, logger=self.logger)
        
        # Determine which sections to generate
        if section_ids:
            sections_to_generate = [s for s in book.sections.values() if s.id in section_ids]
        else:
            # Generate all sections that don't have content yet
            sections_to_generate = [s for s in book.sections.values() if not s.content]
        
        if not sections_to_generate:
            if self.logger:
                self.logger.success("All sections already have content")
            return book
        
        # Create agents for section generation
        section_agents = self.create_agents(self.agent_list, "section")
        
        # Create section generator
        section_generator = SectionGenerator(
            agents=section_agents,
            logger=self.logger
        )
        
        # Generate content for each section
        for section in sections_to_generate:
            if self.logger:
                self.logger.system_message(f"Generating content for section {section.id}: {section.title}")
            
            # Get parent title if applicable
            parent_id = ".".join(section.id.split(".")[:-1]) if "." in section.id else None
            parent_title = book.sections[parent_id].title if parent_id and parent_id in book.sections else None
            
            # Get previous section titles for context
            section_id_parts = section.id.split(".")
            if len(section_id_parts) > 1:
                # For sections within chapters, get previous sections in the same chapter
                chapter_id = section_id_parts[0]
                section_num = int(section_id_parts[1]) if len(section_id_parts) > 1 else 0
                
                previous_sections = [
                    s for s in book.sections.values()
                    if s.id.startswith(f"{chapter_id}.") and
                    len(s.id.split(".")) == 2 and
                    int(s.id.split(".")[1]) < section_num
                ]
                
                previous_titles = [s.title for s in previous_sections]
            else:
                # For chapters, no previous context
                previous_titles = None
            
            # Generate the section content
            content_result = section_generator.generate_section_content(
                book_title=book.title,
                section_id=section.id,
                section_title=section.title,
                previous_section_titles=previous_titles,
                parent_title=parent_title,
                min_words=min_words_per_section,
                max_words=max_words_per_section
            )
            
            # Update the section with the generated content
            book.update_section_content(section.id, content_result["content"])
            
            if self.save_intermediate:
                book.save(self.output_dir)
        
        # Save the final book
        book_dir = book.save(self.output_dir)
        
        if self.logger:
            self.logger.success(f"Book content generation completed")
            self.logger.success(f"Book saved to {book_dir}")
        
        return book
        
    def generate_cover_image_prompt(self, book: Book) -> str:
        """
        Generate a descriptive prompt for book cover image generation.
        
        Args:
            book: The book to generate a cover for
            
        Returns:
            A detailed prompt for image generation
        """
        if self.logger:
            self.logger.system_message(f"Generating cover image prompt for book: {book.title}")
        
        # Create a provider to generate the image prompt
        openai_provider = OpenAIProvider(api_key=self.openai_api_key)
        
        # Create a prompt for the AI to generate a cover image description
        prompt_instructions = """
        You are a professional book cover designer. Create a vivid, detailed description for a book cover
        based on the book's title and table of contents. The description should be specific, visual,
        and evocative, focusing on imagery, colors, and style that would make an attractive and
        relevant book cover.
        
        Follow these guidelines:
        1. Focus on strong imagery that represents the book's themes
        2. Suggest a color palette that fits the book's tone
        3. Describe a visual style (e.g., minimalist, illustrated, photographic)
        4. Be specific about layout (e.g., central image, typography)
        5. Keep your description to a single paragraph of 3-5 sentences
        6. DO NOT include text elements like title or author in your description
        7. Focus only on the visual elements
        """
        
        # Create a message with book details
        toc_text = ""
        for chapter in book.toc:
            toc_text += f"- {chapter['title']}\n"
            if "sections" in chapter:
                for section in chapter["sections"]:
                    toc_text += f"  * {section['title']}\n"
        
        message = f"""
        Book Title: {book.title}
        Book Topic: {book.topic}
        
        Table of Contents:
        {toc_text}
        
        Please create a detailed, visual description for a book cover based on this information.
        """
        
        # Generate the image prompt
        response = openai_provider.generate_response(
            instructions=prompt_instructions,
            messages=[{"role": "user", "content": message}],
            temperature=0.7,
            model="gpt-4"
        )
        
        image_prompt = response["content"].strip()
        
        # Add a standard prefix to help DALL-E generate a book cover
        final_prompt = f"A professional book cover design: {image_prompt} The image should look like a book cover with appropriate composition but WITHOUT any visible text."
        
        if self.logger:
            self.logger.success(f"Generated cover image prompt: {final_prompt}")
        
        return final_prompt
    
    def generate_cover_image(self, book: Book) -> Dict[str, Any]:
        """
        Generate a cover image for a book using DALL-E.
        
        Args:
            book: The book to generate a cover for
            
        Returns:
            Dictionary with image URL and metadata
        """
        if self.logger:
            self.logger.system_message(f"Generating cover image for book: {book.title}")
        
        # Generate the image prompt
        image_prompt = self.generate_cover_image_prompt(book)
        
        # Create a provider to generate the image
        openai_provider = OpenAIProvider(api_key=self.openai_api_key)
        
        # Generate the image
        image_result = openai_provider.generate_image(
            prompt=image_prompt,
            size="1024x1024",
            model="dall-e-3",
            quality="standard",
            style="vivid"
        )
        
        # Download and save the image file
        image_url = image_result["url"]
        
        # Create images directory for the book
        book_id = book.metadata["id"]
        book_dir = os.path.join(self.output_dir, book_id)
        images_dir = os.path.join(book_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        
        # Generate a filename from the URL
        filename = f"cover.jpg"
        image_path = os.path.join(images_dir, filename)
        
        # Download the image
        if self.logger:
            self.logger.system_message(f"Downloading cover image from {image_url}")
        
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            # Generate a relative path for use in templates
            relative_path = f"/books/{book_id}/images/{filename}"
            
            # Update book metadata with both URL and local path
            book.metadata["cover_image"] = image_url
            book.metadata["cover_image_path"] = relative_path
            book.metadata["cover_image_prompt"] = image_prompt
            book.metadata["cover_image_revised_prompt"] = image_result.get("revised_prompt", image_prompt)
            
            if self.logger:
                self.logger.success(f"Added cover image URL: {image_url}")
                self.logger.success(f"Added cover image path: {relative_path}")
            
            if self.logger:
                self.logger.success(f"Cover image saved to {image_path}")
        else:
            if self.logger:
                self.logger.error(f"Failed to download image: {response.status_code}")
            # Still save the URL even if download failed
            book.metadata["cover_image"] = image_url
            book.metadata["cover_image_prompt"] = image_prompt
            book.metadata["cover_image_revised_prompt"] = image_result.get("revised_prompt", image_prompt)
        
        # Save the book with the updated cover image
        book.save(self.output_dir)
        
        if self.logger:
            self.logger.success(f"Generated cover image for book: {book.title}")
        
        return image_result

