"""
Advanced example of creating a book with Agent Saloon.

This example demonstrates more advanced features:
- Custom title
- Predefined table of contents
- Selective section generation
- Exporting to different formats
"""
import os
import sys
import time

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_saloon.book.manager import BookManager
from agent_saloon.book.exporter import BookExporter
from agent_saloon.utils.logger import Logger


def main():
    """Generate an advanced book with custom settings."""
    # Create a logger
    logger = Logger(use_colors=True, log_to_file=True, verbose=True)
    logger.system_message("Starting advanced book generation example")
    
    # Create a book manager
    book_manager = BookManager(logger=logger, output_dir="books", save_intermediate=True)
    
    # Define a custom table of contents
    custom_toc = [
        {
            "title": "Introduction to Machine Learning",
            "sections": [
                {
                    "title": "What is Machine Learning?",
                    "subsections": []
                },
                {
                    "title": "Historical Development",
                    "subsections": []
                },
                {
                    "title": "Key Concepts and Terminology",
                    "subsections": []
                }
            ]
        },
        {
            "title": "Supervised Learning",
            "sections": [
                {
                    "title": "Regression Algorithms",
                    "subsections": [
                        {"title": "Linear Regression"},
                        {"title": "Polynomial Regression"}
                    ]
                },
                {
                    "title": "Classification Algorithms",
                    "subsections": [
                        {"title": "Logistic Regression"},
                        {"title": "Decision Trees"}
                    ]
                }
            ]
        },
        {
            "title": "Unsupervised Learning",
            "sections": [
                {
                    "title": "Clustering Algorithms",
                    "subsections": [
                        {"title": "K-Means Clustering"},
                        {"title": "Hierarchical Clustering"}
                    ]
                },
                {
                    "title": "Dimensionality Reduction",
                    "subsections": [
                        {"title": "Principal Component Analysis (PCA)"},
                        {"title": "t-SNE"}
                    ]
                }
            ]
        }
    ]
    
    # Set a custom title
    custom_title = "Modern Machine Learning: A Comprehensive Guide"
    
    # Generate the book with custom settings
    start_time = time.time()
    
    book = book_manager.generate_book(
        topic="Machine Learning",
        title=custom_title,
        toc=custom_toc,
        min_words_per_section=800,
        max_words_per_section=1500,
        # Only generate specific sections - first chapter only
        section_ids=["1", "1.1", "1.2", "1.3"]  
    )
    
    generation_time = time.time() - start_time
    logger.system_message(f"Initial generation completed in {generation_time:.2f} seconds")
    
    # Continue generating more sections
    logger.system_message("Continuing with additional sections...")
    
    book = book_manager.continue_book_generation(
        book_id=book.metadata["id"],
        section_ids=["2", "2.1"],  # Add chapter 2 and first section
        min_words_per_section=800,
        max_words_per_section=1500
    )
    
    # Export the book to different formats
    logger.system_message("Exporting book to different formats...")
    
    exporter = BookExporter(logger=logger)
    
    # Create export directory
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)
    
    # Export to different formats
    markdown_path = exporter.export_markdown(
        book, 
        os.path.join(export_dir, f"{book.metadata['id']}.md")
    )
    
    html_path = exporter.export_html(
        book, 
        os.path.join(export_dir, f"{book.metadata['id']}.html")
    )
    
    text_path = exporter.export_plaintext(
        book, 
        os.path.join(export_dir, f"{book.metadata['id']}.txt")
    )
    
    # Print book statistics
    progress = book.get_progress()
    logger.system_message(f"Book statistics:")
    logger.system_message(f"- Title: {book.title}")
    logger.system_message(f"- Chapters: {len(book.toc)}")
    logger.system_message(f"- Total sections: {progress['total_sections']}")
    logger.system_message(f"- Completed sections: {progress['completed_sections']}")
    logger.system_message(f"- Progress: {progress['progress_percentage']:.2f}%")
    
    logger.success(f"Book generation and export complete!")
    logger.system_message(f"Book saved to: {os.path.join('books', book.metadata['id'])}")
    logger.system_message(f"Exports saved to:")
    logger.system_message(f"- Markdown: {markdown_path}")
    logger.system_message(f"- HTML: {html_path}")
    logger.system_message(f"- Text: {text_path}")
    
    return book


if __name__ == "__main__":
    main()
