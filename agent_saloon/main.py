"""
Main entry point for the Agent Saloon application.
"""
import argparse
import sys
import os
import json
from typing import Dict, List, Any, Optional

from .book.manager import BookManager
from .book.exporter import BookExporter
from .book.book import Book
from .utils.logger import Logger
from .config.settings import settings
from .agents.factory import AgentFactory


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Agent Saloon - Collaborative AI book writing system")
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Create a book
    create_parser = subparsers.add_parser("create", help="Create a new book")
    create_parser.add_argument("topic", help="Book topic")
    create_parser.add_argument("--title", help="Book title (will be generated if not provided)")
    create_parser.add_argument("--min-chapters", type=int, default=5, help="Minimum number of chapters")
    create_parser.add_argument("--max-chapters", type=int, default=10, help="Maximum number of chapters")
    create_parser.add_argument("--min-words", type=int, default=500, help="Minimum words per section")
    create_parser.add_argument("--max-words", type=int, default=2000, help="Maximum words per section")
    create_parser.add_argument("--output-dir", default="books", help="Output directory for the book")
    create_parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    create_parser.add_argument("--no-log-file", action="store_true", help="Disable logging to file")
    create_parser.add_argument("--agents", default="zero,gustave", 
                             help="Comma-separated list of agents to use (e.g., 'zero,gustave,camille')")
    create_parser.add_argument("--providers", default=None,
                             help="Comma-separated list of providers to use (e.g., 'openai,anthropic')")
    
    # Continue a book
    continue_parser = subparsers.add_parser("continue", help="Continue generating a book")
    continue_parser.add_argument("book_id", help="Book ID to continue")
    continue_parser.add_argument("--sections", help="Comma-separated list of section IDs to generate")
    continue_parser.add_argument("--min-words", type=int, default=500, help="Minimum words per section")
    continue_parser.add_argument("--max-words", type=int, default=2000, help="Maximum words per section")
    continue_parser.add_argument("--output-dir", default="books", help="Output directory for the book")
    continue_parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    continue_parser.add_argument("--no-log-file", action="store_true", help="Disable logging to file")
    continue_parser.add_argument("--agents", default="zero,gustave", 
                              help="Comma-separated list of agents to use (e.g., 'zero,gustave,camille')")
    continue_parser.add_argument("--providers", default=None,
                              help="Comma-separated list of providers to use (e.g., 'openai,anthropic')")
    
    # Export a book
    export_parser = subparsers.add_parser("export", help="Export a book to different formats")
    export_parser.add_argument("book_id", help="Book ID to export")
    export_parser.add_argument("--format", choices=["markdown", "html", "text", "all"], default="all", help="Export format")
    export_parser.add_argument("--output-dir", default="exports", help="Output directory for exports")
    export_parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    
    # List books
    list_parser = subparsers.add_parser("list", help="List available books")
    list_parser.add_argument("--output-dir", default="books", help="Directory containing books")
    list_parser.add_argument("--no-color", action="store_true", help="Disable colored output")
    
    # Configuration
    config_parser = subparsers.add_parser("config", help="View or update configuration")
    config_parser.add_argument("--view", action="store_true", help="View current configuration")
    config_parser.add_argument("--set", nargs=2, metavar=("KEY", "VALUE"), help="Set a configuration value")
    config_parser.add_argument("--reset", action="store_true", help="Reset configuration to defaults")
    
    # List available agents and providers
    agents_parser = subparsers.add_parser("agents", help="List available agents and providers")
    
    return parser.parse_args()


def get_agent_list(args):
    """
    Get the list of agents to use from arguments.
    
    Args:
        args: Command line arguments
        
    Returns:
        List of agent names
    """
    if not args.agents:
        return ["zero", "gustave"]
    
    return [a.strip().lower() for a in args.agents.split(",")]


def get_provider_mapping(args, agent_list):
    """
    Get the mapping of agents to providers.
    
    Args:
        args: Command line arguments
        agent_list: List of agent names
        
    Returns:
        Dictionary mapping agent names to providers
    """
    # Default provider mapping
    default_mapping = {
        "zero": "openai",
        "gustave": "openai",
        "camille": "anthropic"
    }
    
    # If no providers specified, use defaults
    if not args.providers:
        return {agent: default_mapping.get(agent, "openai") for agent in agent_list}
    
    # Parse provider list
    providers = [p.strip().lower() for p in args.providers.split(",")]
    
    # If only one provider specified, use it for all agents
    if len(providers) == 1:
        return {agent: providers[0] for agent in agent_list}
    
    # If multiple providers, map them to agents
    if len(providers) < len(agent_list):
        # Cycle through providers if there are fewer providers than agents
        return {agent: providers[i % len(providers)] for i, agent in enumerate(agent_list)}
    else:
        # Map providers directly to agents
        return {agent: providers[i] for i, agent in enumerate(agent_list)}


def create_book(args):
    """
    Create a new book.
    
    Args:
        args: Command line arguments
    """
    # Set up logger
    logger = Logger(
        use_colors=not args.no_color,
        log_to_file=not args.no_log_file,
        verbose=True
    )
    
    # Get agent list and provider mapping
    agent_list = get_agent_list(args)
    provider_mapping = get_provider_mapping(args, agent_list)
    
    logger.system_message(f"Creating book: {args.topic}")
    logger.system_message(f"Using agents: {', '.join(agent_list)}")
    
    # Create book manager with specified agents
    book_manager = BookManager(
        logger=logger,
        output_dir=args.output_dir,
        save_intermediate=True,
        agent_list=agent_list,
        provider_mapping=provider_mapping
    )
    
    # Generate the book
    book = book_manager.generate_book(
        topic=args.topic,
        title=args.title,
        min_chapters=args.min_chapters,
        max_chapters=args.max_chapters,
        min_words_per_section=args.min_words,
        max_words_per_section=args.max_words
    )
    
    logger.success(f"Book '{book.title}' created successfully!")
    logger.success(f"Book ID: {book.metadata['id']}")
    
    # Print book statistics
    progress = book.get_progress()
    logger.system_message(f"Book summary:")
    logger.system_message(f"- Title: {book.title}")
    logger.system_message(f"- Chapters: {len(book.toc)}")
    logger.system_message(f"- Total sections: {progress['total_sections']}")
    logger.system_message(f"- Completed sections: {progress['completed_sections']}")
    logger.system_message(f"- Progress: {progress['progress_percentage']:.2f}%")

    # Create book manager with specified agents
    book_manager = BookManager(
        logger=logger,
        output_dir=args.output_dir,
        save_intermediate=True,
        agent_list=agent_list,
        provider_mapping=provider_mapping
    )
    
    # Generate the book
    book = book_manager.generate_book(
        topic=args.topic,
        title=args.title,
        min_chapters=args.min_chapters,
        max_chapters=args.max_chapters,
        min_words_per_section=args.min_words,
        max_words_per_section=args.max_words
    )
    
    logger.success(f"Book '{book.title}' created successfully!")
    logger.success(f"Book ID: {book.metadata['id']}")
    logger.success(f"Book saved to: {os.path.join(args.output_dir, book.metadata['id'])}")
    
    # Print book statistics
    progress = book.get_progress()
    logger.system_message(f"Book statistics:")
    logger.system_message(f"- Title: {book.title}")
    logger.system_message(f"- Chapters: {len(book.toc)}")
    logger.system_message(f"- Total sections: {progress['total_sections']}")
    logger.system_message(f"- Completed sections: {progress['completed_sections']}")
    logger.system_message(f"- Progress: {progress['progress_percentage']:.2f}%")


def continue_book(args):
    """
    Continue generating a book.
    
    Args:
        args: Command line arguments
    """
    # Set up logger
    logger = Logger(
        use_colors=not args.no_color,
        log_to_file=not args.no_log_file,
        verbose=True
    )
    
    # Get agent list and provider mapping
    agent_list = get_agent_list(args)
    provider_mapping = get_provider_mapping(args, agent_list)
    
    logger.system_message(f"Continuing book generation for book ID: {args.book_id}")
    logger.system_message(f"Using agents: {', '.join(agent_list)}")
    logger.system_message(f"Provider mapping: {provider_mapping}")
    
    # Create book manager with specified agents
    book_manager = BookManager(
        logger=logger,
        output_dir=args.output_dir,
        save_intermediate=True,
        agent_list=agent_list,
        provider_mapping=provider_mapping
    )
    
    # Parse section IDs if provided
    section_ids = None
    if args.sections:
        section_ids = [s.strip() for s in args.sections.split(",")]
    
    # Continue generating the book
    try:
        book = book_manager.continue_book_generation(
            book_id=args.book_id,
            section_ids=section_ids,
            min_words_per_section=args.min_words,
            max_words_per_section=args.max_words
        )
        
        logger.success(f"Book '{book.title}' updated successfully!")
        logger.success(f"Book saved to: {os.path.join(args.output_dir, book.metadata['id'])}")
        
        # Print book statistics
        progress = book.get_progress()
        logger.system_message(f"Book statistics:")
        logger.system_message(f"- Title: {book.title}")
        logger.system_message(f"- Chapters: {len(book.toc)}")
        logger.system_message(f"- Total sections: {progress['total_sections']}")
        logger.system_message(f"- Completed sections: {progress['completed_sections']}")
        logger.system_message(f"- Progress: {progress['progress_percentage']:.2f}%")
    
    except FileNotFoundError:
        logger.error(f"Book with ID '{args.book_id}' not found in directory: {args.output_dir}")
        sys.exit(1)


def export_book(args):
    """
    Export a book to different formats.
    
    Args:
        args: Command line arguments
    """
    # Set up logger
    logger = Logger(
        use_colors=not args.no_color,
        log_to_file=False,
        verbose=True
    )
    
    logger.system_message(f"Exporting book with ID: {args.book_id}")
    
    # Create book exporter
    exporter = BookExporter(logger=logger)
    
    # Try to load the book
    try:
        book = Book.load(args.book_id, directory=args.output_dir, logger=logger)
        
        # Ensure output directory exists
        os.makedirs(args.output_dir, exist_ok=True)
        
        # Generate a slug for the book title
        title_slug = book.title.lower().replace(" ", "_")
        book_output_dir = os.path.join(args.output_dir, title_slug)
        
        # Export the book in the requested formats
        if args.format == "markdown" or args.format == "all":
            markdown_path = os.path.join(book_output_dir, f"{title_slug}.md")
            exporter.export_markdown(book, markdown_path)
        
        if args.format == "html" or args.format == "all":
            html_path = os.path.join(book_output_dir, f"{title_slug}.html")
            exporter.export_html(book, html_path)
        
        if args.format == "text" or args.format == "all":
            text_path = os.path.join(book_output_dir, f"{title_slug}.txt")
            exporter.export_plaintext(book, text_path)
        
        logger.success(f"Book '{book.title}' exported successfully to {book_output_dir}!")
    
    except FileNotFoundError:
        logger.error(f"Book with ID '{args.book_id}' not found in directory: {args.output_dir}")
        sys.exit(1)


def list_books(args):
    """
    List available books.
    
    Args:
        args: Command line arguments
    """
    # Set up logger
    logger = Logger(
        use_colors=not args.no_color,
        log_to_file=False,
        verbose=True
    )
    
    logger.system_message(f"Listing books in directory: {args.output_dir}")
    
    # Check if the directory exists
    if not os.path.exists(args.output_dir):
        logger.error(f"Directory not found: {args.output_dir}")
        sys.exit(1)
    
    # Find book directories
    books = []
    for item in os.listdir(args.output_dir):
        item_path = os.path.join(args.output_dir, item)
        metadata_path = os.path.join(item_path, "metadata.json")
        
        if os.path.isdir(item_path) and os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    books.append(metadata)
            except Exception as e:
                logger.warning(f"Error loading metadata for {item}: {str(e)}")
    
    # Display books
    if not books:
        logger.system_message("No books found.")
        return
    
    logger.system_message(f"Found {len(books)} books:")
    
    for book in books:
        progress = book.get("progress", {})
        progress_pct = progress.get("progress_percentage", 0)
        
        logger.system_message(f"- ID: {book.get('id')}")
        logger.system_message(f"  Title: {book.get('title')}")
        logger.system_message(f"  Topic: {book.get('topic')}")
        logger.system_message(f"  Chapters: {len(book.get('toc', []))}")
        logger.system_message(f"  Progress: {progress_pct:.2f}%")
        logger.system_message(f"  Created: {book.get('created_at')}")
        logger.system_message("")


def config_command(args):
    """
    View or update configuration.
    
    Args:
        args: Command line arguments
    """
    if args.view:
        # Display current configuration
        print(json.dumps(settings.config, indent=2))
    
    elif args.set:
        # Set a configuration value
        key, value = args.set
        
        # Try to convert value to the appropriate type
        try:
            # Try as int
            value = int(value)
        except ValueError:
            try:
                # Try as float
                value = float(value)
            except ValueError:
                # Try as boolean
                if value.lower() in ["true", "yes", "1"]:
                    value = True
                elif value.lower() in ["false", "no", "0"]:
                    value = False
                # Otherwise keep as string
        
        settings.set(key, value)
        settings.save()
        print(f"Configuration updated: {key} = {value}")
    
    elif args.reset:
        # Reset to default configuration
        if os.path.exists(settings.config_path):
            os.remove(settings.config_path)
        
        # Reload settings
        settings.__init__(settings.config_path)
        print("Configuration reset to defaults.")


def list_agents():
    """List available agents and providers."""
    print("Available Agents:")
    print("  - zero:    Enthusiastic and creative writer")
    print("  - gustave: Refined and eloquent editor")
    print("  - camille: Balanced and insightful reviewer")
    print("\nAvailable Providers:")
    print("  - openai:    OpenAI GPT models (default for Zero and Gustave)")
    print("  - anthropic: Anthropic Claude models (default for Camille)")
    print("\nDefault Models:")
    print("  - OpenAI:    gpt-4")
    print("  - Anthropic: claude-3-opus-20240229")
    print("\nExample Usage:")
    print("  agent-saloon create \"AI History\" --agents zero,camille,gustave")
    print("  agent-saloon create \"AI History\" --agents zero,camille --providers openai,anthropic")


def main():
    """Main entry point for the application."""
    args = parse_args()
    
    # Execute the appropriate command
    if args.command == "create":
        create_book(args)
    elif args.command == "continue":
        continue_book(args)
    elif args.command == "export":
        export_book(args)
    elif args.command == "list":
        list_books(args)
    elif args.command == "config":
        config_command(args)
    elif args.command == "agents":
        list_agents()
    else:
        # Display help if no command is provided
        print("Please specify a command. Use --help for more information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
