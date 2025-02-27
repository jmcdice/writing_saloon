"""
Simple example of creating a book with Agent Saloon.

This example demonstrates creating a book with default settings.
"""
import os
import sys

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agent_saloon.book.manager import BookManager
from agent_saloon.utils.logger import Logger


def main():
    """Generate a simple book about Python programming."""
    # Create a logger
    logger = Logger(use_colors=True, log_to_file=True, verbose=True)
    logger.system_message("Starting simple book generation example")
    
    # Create a book manager
    book_manager = BookManager(logger=logger, output_dir="books", save_intermediate=True)
    
    # Generate a book
    book = book_manager.generate_book(
        topic="Python Programming for Beginners",
        # Using default settings for chapters and word counts
    )
    
    # Print book statistics
    progress = book.get_progress()
    logger.system_message(f"Book statistics:")
    logger.system_message(f"- Title: {book.title}")
    logger.system_message(f"- Chapters: {len(book.toc)}")
    logger.system_message(f"- Total sections: {progress['total_sections']}")
    logger.system_message(f"- Completed sections: {progress['completed_sections']}")
    logger.system_message(f"- Progress: {progress['progress_percentage']:.2f}%")
    
    logger.success(f"Book generation complete! Book ID: {book.metadata['id']}")
    logger.system_message(f"Book saved to: {os.path.join('books', book.metadata['id'])}")
    
    return book


if __name__ == "__main__":
    main()

