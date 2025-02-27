"""
Exporter for converting books to various formats.
"""
from typing import Dict, List, Any, Optional
import os
import shutil
import json
import re

from .book import Book
from ..utils.logger import Logger


class BookExporter:
    """
    Exporter for converting books to various formats.
    
    This class provides functionality to export books to different
    file formats, such as plaintext, Markdown, and HTML.
    """
    
    def __init__(
        self,
        logger: Optional[Logger] = None
    ):
        """
        Initialize a book exporter.
        
        Args:
            logger: Logger instance for IRC-style logging
        """
        self.logger = logger
    
    def export_markdown(self, book: Book, output_path: str) -> str:
        """
        Export a book to a single Markdown file.
        
        Args:
            book: Book object to export
            output_path: Path to save the exported file
            
        Returns:
            Path to the exported file
        """
        if self.logger:
            self.logger.system_message(f"Exporting book '{book.title}' to Markdown")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate frontmatter
        frontmatter = f"""---
title: "{book.title}"
author: "{book.author}"
date: "{book.created_at.strftime('%Y-%m-%d')}"
---

"""
        
        # Generate the book content
        content = f"# {book.title}\n\n"
        content += f"By {book.author}\n\n"
        
        # Add table of contents
        content += "## Table of Contents\n\n"
        
        for chapter_index, chapter in enumerate(book.toc):
            chapter_number = chapter_index + 1
            content += f"{chapter_number}. {chapter['title']}\n"
            
            if "sections" in chapter:
                for section_index, section in enumerate(chapter["sections"]):
                    section_number = section_index + 1
                    content += f"   {chapter_number}.{section_number}. {section['title']}\n"
                    
                    if "subsections" in section:
                        for subsection_index, subsection in enumerate(section["subsections"]):
                            subsection_number = subsection_index + 1
                            content += f"      {chapter_number}.{section_number}.{subsection_number}. {subsection['title']}\n"
        
        content += "\n\n"
        
        # Sort sections by ID for proper ordering
        sorted_sections = sorted(
            book.sections.items(),
            key=lambda x: [int(n) if n.isdigit() else n for n in x[0].split(".")]
        )
        
        # Add section content
        for section_id, section in sorted_sections:
            if section.content:
                content += f"{'#' * section.level} {section.title}\n\n"
                content += f"{section.content}\n\n"
        
        # Write the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(frontmatter + content)
        
        if self.logger:
            self.logger.success(f"Book exported to {output_path}")
        
        return output_path
    
    def export_html(self, book: Book, output_path: str) -> str:
        """
        Export a book to HTML.
        
        Args:
            book: Book object to export
            output_path: Path to save the exported file
            
        Returns:
            Path to the exported file
        """
        if self.logger:
            self.logger.system_message(f"Exporting book '{book.title}' to HTML")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Basic HTML template
        html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3, h4, h5, h6 {{
            color: #444;
            margin-top: 1.5em;
        }}
        a {{
            color: #0066cc;
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        .toc {{
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            padding: 20px;
            margin: 20px 0;
        }}
        .toc ul {{
            list-style-type: none;
        }}
        .toc li {{
            margin-bottom: 5px;
        }}
        .section {{
            margin-top: 2em;
            border-top: 1px solid #eee;
            padding-top: 1em;
        }}
        .chapter {{
            margin-top: 3em;
            border-top: 2px solid #ddd;
            padding-top: 1.5em;
        }}
        .metadata {{
            color: #777;
            font-size: 0.9em;
            margin-bottom: 2em;
        }}
    </style>
</head>
<body>
    <h1>{title}</h1>
    
    <div class="metadata">
        <p>By {author}<br>
        Created: {date}</p>
    </div>
    
    <div class="toc">
        <h2>Table of Contents</h2>
        {toc_html}
    </div>
    
    <div class="content">
        {content_html}
    </div>
</body>
</html>
"""
        
        # Generate table of contents HTML
        toc_html = "<ul>"
        
        for chapter_index, chapter in enumerate(book.toc):
            chapter_number = chapter_index + 1
            chapter_id = f"chapter-{chapter_number}"
            toc_html += f'<li><a href="#{chapter_id}">{chapter_number}. {chapter["title"]}</a>'
            
            if "sections" in chapter:
                toc_html += "<ul>"
                for section_index, section in enumerate(chapter["sections"]):
                    section_number = section_index + 1
                    section_id = f"section-{chapter_number}-{section_number}"
                    toc_html += f'<li><a href="#{section_id}">{chapter_number}.{section_number}. {section["title"]}</a>'
                    
                    if "subsections" in section:
                        toc_html += "<ul>"
                        for subsection_index, subsection in enumerate(section["subsections"]):
                            subsection_number = subsection_index + 1
                            subsection_id = f"subsection-{chapter_number}-{section_number}-{subsection_number}"
                            toc_html += f'<li><a href="#{subsection_id}">{chapter_number}.{section_number}.{subsection_number}. {subsection["title"]}</a></li>'
                        toc_html += "</ul>"
                    
                    toc_html += '</li>'
                toc_html += "</ul>"
            
            toc_html += '</li>'
        
        toc_html += "</ul>"
        
        # Generate content HTML
        content_html = ""
        
        # Sort sections by ID for proper ordering
        sorted_sections = sorted(
            book.sections.items(),
            key=lambda x: [int(n) if n.isdigit() else n for n in x[0].split(".")]
        )
        
        # Add section content
        for section_id, section in sorted_sections:
            if not section.content:
                continue
                
            # Generate appropriate HTML ID
            id_parts = section_id.split(".")
            if len(id_parts) == 1:
                # Chapter
                html_id = f"chapter-{id_parts[0]}"
                section_class = "chapter"
                heading_tag = "h2"
            elif len(id_parts) == 2:
                # Section
                html_id = f"section-{id_parts[0]}-{id_parts[1]}"
                section_class = "section"
                heading_tag = "h3"
            else:
                # Subsection
                html_id = f"subsection-{'-'.join(id_parts)}"
                section_class = "subsection"
                heading_tag = "h4"
            
            # Convert markdown to basic HTML
            section_content = section.content
            # Convert headers
            for i in range(6, 0, -1):
                pattern = r'^#{' + str(i) + r'}\s+(.+?)$'
                section_content = re.sub(pattern, r'<h' + str(i + section.level) + r'>\1</h' + str(i + section.level) + r'>', section_content, flags=re.MULTILINE)
            
            # Convert basic markdown formatting
            section_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', section_content)
            section_content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', section_content)
            section_content = re.sub(r'`(.*?)`', r'<code>\1</code>', section_content)
            
            # Convert paragraphs
            section_content = re.sub(r'\n\n', r'</p>\n\n<p>', section_content)
            section_content = f"<p>{section_content}</p>"
            
            # Add to HTML
            content_html += f'<div id="{html_id}" class="{section_class}">'
            content_html += f'<{heading_tag}>{section.title}</{heading_tag}>'
            content_html += section_content
            content_html += '</div>'
        
        # Fill in the template
        html_content = html_template.format(
            title=book.title,
            author=book.author,
            date=book.created_at.strftime('%Y-%m-%d'),
            toc_html=toc_html,
            content_html=content_html
        )
        
        # Write the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        if self.logger:
            self.logger.success(f"Book exported to {output_path}")
        
        return output_path
    
    def export_plaintext(self, book: Book, output_path: str) -> str:
        """
        Export a book to plaintext.
        
        Args:
            book: Book object to export
            output_path: Path to save the exported file
            
        Returns:
            Path to the exported file
        """
        if self.logger:
            self.logger.system_message(f"Exporting book '{book.title}' to plaintext")
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate the book content
        content = f"{book.title.upper()}\n"
        content += "=" * len(book.title) + "\n\n"
        content += f"By {book.author}\n\n"
        
        # Add table of contents
        content += "TABLE OF CONTENTS\n"
        content += "=" * 16 + "\n\n"
        
        for chapter_index, chapter in enumerate(book.toc):
            chapter_number = chapter_index + 1
            content += f"{chapter_number}. {chapter['title']}\n"
            
            if "sections" in chapter:
                for section_index, section in enumerate(chapter["sections"]):
                    section_number = section_index + 1
                    content += f"   {chapter_number}.{section_number}. {section['title']}\n"
                    
                    if "subsections" in section:
                        for subsection_index, subsection in enumerate(section["subsections"]):
                            subsection_number = subsection_index + 1
                            content += f"      {chapter_number}.{section_number}.{subsection_number}. {subsection['title']}\n"
        
        content += "\n\n"
        
        # Sort sections by ID for proper ordering
        sorted_sections = sorted(
            book.sections.items(),
            key=lambda x: [int(n) if n.isdigit() else n for n in x[0].split(".")]
        )
        
        # Add section content
        for section_id, section in sorted_sections:
            if section.content:
                # Format the heading
                heading = section.title
                if section.level == 1:
                    # Chapter
                    content += f"\n\n{heading.upper()}\n"
                    content += "=" * len(heading) + "\n\n"
                elif section.level == 2:
                    # Section
                    content += f"\n\n{heading}\n"
                    content += "-" * len(heading) + "\n\n"
                else:
                    # Subsection
                    content += f"\n\n{heading}\n\n"
                
                # Clean formatting from content
                clean_content = re.sub(r'#{1,6}\s+(.+?)$', r'\1', section.content, flags=re.MULTILINE)
                clean_content = re.sub(r'\*\*(.*?)\*\*', r'\1', clean_content)
                clean_content = re.sub(r'\*(.*?)\*', r'\1', clean_content)
                clean_content = re.sub(r'`(.*?)`', r'\1', clean_content)
                
                content += clean_content + "\n\n"
        
        # Write the file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        if self.logger:
            self.logger.success(f"Book exported to {output_path}")
        
        return output_path
    
    def export_all_formats(self, book: Book, output_dir: str) -> Dict[str, str]:
        """
        Export a book to all supported formats.
        
        Args:
            book: Book object to export
            output_dir: Directory to save the exported files
            
        Returns:
            Dictionary mapping format names to export paths
        """
        # Generate a slug for the book title
        title_slug = book.title.lower().replace(" ", "_")
        
        # Create output directory
        book_output_dir = os.path.join(output_dir, title_slug)
        os.makedirs(book_output_dir, exist_ok=True)
        
        # Export to different formats
        markdown_path = os.path.join(book_output_dir, f"{title_slug}.md")
        html_path = os.path.join(book_output_dir, f"{title_slug}.html")
        text_path = os.path.join(book_output_dir, f"{title_slug}.txt")
        
        markdown_export = self.export_markdown(book, markdown_path)
        html_export = self.export_html(book, html_path)
        text_export = self.export_plaintext(book, text_path)
        
        return {
            "markdown": markdown_export,
            "html": html_export,
            "text": text_export
        }
