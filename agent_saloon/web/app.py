"""
Web UI for Agent Saloon - Collaborative AI Book Writing System
"""
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
import os
import json
import logging
from datetime import datetime
import time
import threading
import pathlib

# Import from parent package
from agent_saloon.book.manager import BookManager
from agent_saloon.book.exporter import BookExporter
from agent_saloon.book.book import Book
from agent_saloon.utils.logger import Logger
from agent_saloon.agents.factory import AgentFactory

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'agent_saloon_secret_key')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Directory settings - relative to package root
APP_ROOT = pathlib.Path(__file__).parent.parent.parent.absolute()
BOOKS_DIR = os.path.join(APP_ROOT, "books")
EXPORTS_DIR = os.path.join(APP_ROOT, "exports")
LOGS_DIR = os.path.join(APP_ROOT, "logs")

# Ensure directories exist
os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(EXPORTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# Active book generation tasks
active_tasks = {}

# Web logger that stores logs in memory for the UI
class WebLogger(Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.log_entries = []
        
    def _log(self, message):
        super()._log(message)
        # Store clean version of message for web display
        clean_message = self._strip_ansi(message)
        self.log_entries.append({
            "time": datetime.now().isoformat(),
            "message": clean_message
        })
        # Keep only the last 100 messages
        if len(self.log_entries) > 100:
            self.log_entries = self.log_entries[-100:]


def generate_book_task(task_id, topic, title, min_chapters, max_chapters, min_words, max_words, 
                      agent_list, provider_mapping, custom_toc=None, section_ids=None):
    """Background task for book generation"""
    try:
        # Create logger
        web_logger = WebLogger(use_colors=True, log_to_file=True, verbose=True)
        
        # Update task status
        active_tasks[task_id]["status"] = "running"
        active_tasks[task_id]["logger"] = web_logger
        active_tasks[task_id]["start_time"] = time.time()
        
        # Create book manager
        book_manager = BookManager(
            logger=web_logger,
            output_dir=BOOKS_DIR,
            save_intermediate=True,
            agent_list=agent_list,
            provider_mapping=provider_mapping
        )
        
        # Generate book
        if custom_toc:
            book = book_manager.generate_book(
                topic=topic,
                title=title,
                toc=custom_toc,
                min_chapters=min_chapters,
                max_chapters=max_chapters,
                min_words_per_section=min_words,
                max_words_per_section=max_words,
                section_ids=section_ids
            )
        else:
            book = book_manager.generate_book(
                topic=topic,
                title=title,
                min_chapters=min_chapters,
                max_chapters=max_chapters,
                min_words_per_section=min_words,
                max_words_per_section=max_words,
                section_ids=section_ids
            )
        
        # Update task with book information
        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["end_time"] = time.time()
        active_tasks[task_id]["book_id"] = book.metadata["id"]
        active_tasks[task_id]["title"] = book.title
        active_tasks[task_id]["progress"] = book.get_progress()
        
        # Export book to all formats
        exporter = BookExporter(logger=web_logger)
        title_slug = book.title.lower().replace(" ", "_")
        book_export_dir = os.path.join(EXPORTS_DIR, title_slug)
        os.makedirs(book_export_dir, exist_ok=True)
        
        # Export to different formats
        export_paths = {}
        export_paths["markdown"] = exporter.export_markdown(
            book, os.path.join(book_export_dir, f"{title_slug}.md")
        )
        export_paths["html"] = exporter.export_html(
            book, os.path.join(book_export_dir, f"{title_slug}.html")
        )
        export_paths["text"] = exporter.export_plaintext(
            book, os.path.join(book_export_dir, f"{title_slug}.txt")
        )
        
        active_tasks[task_id]["exports"] = export_paths
        
    except Exception as e:
        logger.error(f"Error in book generation: {str(e)}")
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)
        active_tasks[task_id]["end_time"] = time.time()


def continue_book_task(task_id, book_id, section_ids, min_words, max_words, agent_list, provider_mapping):
    """Background task for continuing book generation"""
    try:
        # Create logger
        web_logger = WebLogger(use_colors=True, log_to_file=True, verbose=True)
        
        # Update task status
        active_tasks[task_id]["status"] = "running"
        active_tasks[task_id]["logger"] = web_logger
        active_tasks[task_id]["start_time"] = time.time()
        
        # Create book manager
        book_manager = BookManager(
            logger=web_logger,
            output_dir=BOOKS_DIR,
            save_intermediate=True,
            agent_list=agent_list,
            provider_mapping=provider_mapping
        )
        
        # Continue book generation
        book = book_manager.continue_book_generation(
            book_id=book_id,
            section_ids=section_ids,
            min_words_per_section=min_words,
            max_words_per_section=max_words
        )
        
        # Update task with book information
        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["end_time"] = time.time()
        active_tasks[task_id]["book_id"] = book.metadata["id"]
        active_tasks[task_id]["title"] = book.title
        active_tasks[task_id]["progress"] = book.get_progress()
        
        # Export book to all formats
        exporter = BookExporter(logger=web_logger)
        title_slug = book.title.lower().replace(" ", "_")
        book_export_dir = os.path.join(EXPORTS_DIR, title_slug)
        os.makedirs(book_export_dir, exist_ok=True)
        
        # Export to different formats
        export_paths = {}
        export_paths["markdown"] = exporter.export_markdown(
            book, os.path.join(book_export_dir, f"{title_slug}.md")
        )
        export_paths["html"] = exporter.export_html(
            book, os.path.join(book_export_dir, f"{title_slug}.html")
        )
        export_paths["text"] = exporter.export_plaintext(
            book, os.path.join(book_export_dir, f"{title_slug}.txt")
        )
        
        active_tasks[task_id]["exports"] = export_paths
        
    except Exception as e:
        logger.error(f"Error in book continuation: {str(e)}")
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)
        active_tasks[task_id]["end_time"] = time.time()


def generate_cover_task(task_id, book_id):
    """Background task for generating a book cover image"""
    try:
        # Create logger
        web_logger = WebLogger(use_colors=True, log_to_file=True, verbose=True)
        
        # Update task status
        active_tasks[task_id]["status"] = "running"
        active_tasks[task_id]["logger"] = web_logger
        active_tasks[task_id]["start_time"] = time.time()
        
        # Create book manager
        book_manager = BookManager(
            logger=web_logger,
            output_dir=BOOKS_DIR,
            save_intermediate=True
        )
        
        # Load the book
        book = Book.load(book_id, directory=BOOKS_DIR, logger=web_logger)
        
        # Generate cover image
        image_result = book_manager.generate_cover_image(book)
        
        # Update task with book information
        active_tasks[task_id]["status"] = "completed"
        active_tasks[task_id]["end_time"] = time.time()
        active_tasks[task_id]["book_id"] = book.metadata["id"]
        active_tasks[task_id]["title"] = book.title
        active_tasks[task_id]["cover_image"] = book.metadata.get("cover_image_path", "")
        active_tasks[task_id]["cover_image_url"] = image_result["url"]
        active_tasks[task_id]["image_prompt"] = image_result.get("revised_prompt", "")
        
        web_logger.success(f"Cover image generated for book: {book.title}")
        
    except Exception as e:
        logger.error(f"Error in cover image generation: {str(e)}")
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)
        active_tasks[task_id]["end_time"] = time.time()


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard showing book generation progress and tasks"""
    # Get list of existing books
    books = []
    if os.path.exists(BOOKS_DIR):
        for item in os.listdir(BOOKS_DIR):
            item_path = os.path.join(BOOKS_DIR, item)
            metadata_path = os.path.join(item_path, "metadata.json")
            
            if os.path.isdir(item_path) and os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        books.append(metadata)
                except Exception as e:
                    logger.warning(f"Error loading metadata for {item}: {str(e)}")
    
    # Sort books by creation date, newest first
    books.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return render_template(
        'dashboard.html', 
        books=books, 
        active_tasks=active_tasks
    )


@app.route('/create', methods=['GET', 'POST'])
def create_book():
    """Create a new book"""
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic', '').strip()
        title = request.form.get('title', '').strip() or None
        min_chapters = int(request.form.get('min_chapters', 5))
        max_chapters = int(request.form.get('max_chapters', 10))
        min_words = int(request.form.get('min_words', 500))
        max_words = int(request.form.get('max_words', 2000))
        agents = request.form.get('agents', 'zero,gustave').strip()
        providers = request.form.get('providers', '')
        
        # Create task ID
        task_id = f"create_{int(time.time())}"
        
        # Parse agent list and provider mapping
        agent_list = [a.strip().lower() for a in agents.split(",")]
        
        # Default provider mapping
        default_mapping = {
            "zero": "openai",
            "gustave": "openai",
            "camille": "anthropic"
        }
        
        if providers:
            provider_list = [p.strip().lower() for p in providers.split(",")]
            if len(provider_list) == 1:
                provider_mapping = {agent: provider_list[0] for agent in agent_list}
            else:
                provider_mapping = {agent: provider_list[i % len(provider_list)] for i, agent in enumerate(agent_list)}
        else:
            provider_mapping = {agent: default_mapping.get(agent, "openai") for agent in agent_list}
        
        # Create task entry
        active_tasks[task_id] = {
            "type": "create",
            "topic": topic,
            "title": title,
            "status": "queued",
            "created_at": time.time(),
            "agent_list": agent_list,
            "provider_mapping": provider_mapping
        }
        
        # Start book generation in background thread
        thread = threading.Thread(
            target=generate_book_task,
            args=(
                task_id, topic, title, min_chapters, max_chapters, 
                min_words, max_words, agent_list, provider_mapping
            )
        )
        thread.daemon = True
        thread.start()
        
        flash(f"Book generation started for topic: {topic}", "success")
        return redirect(url_for('task_status', task_id=task_id))
    
    # GET request - show the creation form
    return render_template('create_book.html')


@app.route('/book/<book_id>')
def view_book(book_id):
    """View a specific book"""
    try:
        book = Book.load(book_id, directory=BOOKS_DIR)
        return render_template('view_book.html', book=book)
    except FileNotFoundError:
        flash(f"Book with ID '{book_id}' not found", "danger")
        return redirect(url_for('dashboard'))


@app.route('/book/<book_id>/continue', methods=['GET', 'POST'])
def continue_book(book_id):
    """Continue generating a book"""
    try:
        book = Book.load(book_id, directory=BOOKS_DIR)
        
        if request.method == 'POST':
            # Get form data
            section_ids_str = request.form.get('section_ids', '').strip()
            min_words = int(request.form.get('min_words', 500))
            max_words = int(request.form.get('max_words', 2000))
            agents = request.form.get('agents', 'zero,gustave').strip()
            providers = request.form.get('providers', '')
            
            # Parse section IDs
            section_ids = [s.strip() for s in section_ids_str.split(",")] if section_ids_str else None
            
            # Create task ID
            task_id = f"continue_{int(time.time())}"
            
            # Parse agent list and provider mapping
            agent_list = [a.strip().lower() for a in agents.split(",")]
            
            # Default provider mapping
            default_mapping = {
                "zero": "openai",
                "gustave": "openai",
                "camille": "anthropic"
            }
            
            if providers:
                provider_list = [p.strip().lower() for p in providers.split(",")]
                if len(provider_list) == 1:
                    provider_mapping = {agent: provider_list[0] for agent in agent_list}
                else:
                    provider_mapping = {agent: provider_list[i % len(provider_list)] for i, agent in enumerate(agent_list)}
            else:
                provider_mapping = {agent: default_mapping.get(agent, "openai") for agent in agent_list}
            
            # Create task entry
            active_tasks[task_id] = {
                "type": "continue",
                "book_id": book_id,
                "title": book.title,
                "status": "queued",
                "created_at": time.time(),
                "agent_list": agent_list,
                "provider_mapping": provider_mapping
            }
            
            # Start book continuation in background thread
            thread = threading.Thread(
                target=continue_book_task,
                args=(
                    task_id, book_id, section_ids, 
                    min_words, max_words, agent_list, provider_mapping
                )
            )
            thread.daemon = True
            thread.start()
            
            flash(f"Book continuation started for: {book.title}", "success")
            return redirect(url_for('task_status', task_id=task_id))
        
        # GET request - show the continue form
        # Identify incomplete sections
        incomplete_sections = []
        for section_id, section in book.sections.items():
            if not section.content:
                incomplete_sections.append({
                    "id": section_id,
                    "title": section.title
                })
        
        return render_template(
            'continue_book.html', 
            book=book,
            incomplete_sections=incomplete_sections
        )
    
    except FileNotFoundError:
        flash(f"Book with ID '{book_id}' not found", "danger")
        return redirect(url_for('dashboard'))


@app.route('/book/<book_id>/export')
def export_book(book_id):
    """Export a book to different formats"""
    try:
        book = Book.load(book_id, directory=BOOKS_DIR)
        
        # Create a logger
        web_logger = WebLogger(use_colors=True, log_to_file=False, verbose=True)
        
        # Create book exporter
        exporter = BookExporter(logger=web_logger)
        
        # Generate a slug for the book title
        title_slug = book.title.lower().replace(" ", "_")
        book_export_dir = os.path.join(EXPORTS_DIR, title_slug)
        os.makedirs(book_export_dir, exist_ok=True)
        
        # Export to different formats
        export_paths = {}
        export_paths["markdown"] = exporter.export_markdown(
            book, os.path.join(book_export_dir, f"{title_slug}.md")
        )
        export_paths["html"] = exporter.export_html(
            book, os.path.join(book_export_dir, f"{title_slug}.html")
        )
        export_paths["text"] = exporter.export_plaintext(
            book, os.path.join(book_export_dir, f"{title_slug}.txt")
        )
        
        flash(f"Book exported successfully", "success")
        
        return render_template(
            'export_book.html',
            book=book,
            export_paths=export_paths,
            title_slug=title_slug
        )
    
    except FileNotFoundError:
        flash(f"Book with ID '{book_id}' not found", "danger")
        return redirect(url_for('dashboard'))


@app.route('/book/<book_id>/generate-cover')
def generate_book_cover(book_id):
    """Generate a cover image for a book"""
    try:
        book = Book.load(book_id, directory=BOOKS_DIR)
        
        # Create a logger
        web_logger = WebLogger(use_colors=True, log_to_file=True, verbose=True)
        
        # Create task ID
        task_id = f"cover_{int(time.time())}"
        
        # Create task entry
        active_tasks[task_id] = {
            "type": "cover",
            "book_id": book_id,
            "title": book.title,
            "status": "queued",
            "created_at": time.time(),
            "logger": web_logger
        }
        
        # Start cover generation in background thread
        thread = threading.Thread(
            target=generate_cover_task,
            args=(task_id, book_id)
        )
        thread.daemon = True
        thread.start()
        
        flash(f"Cover image generation started for book: {book.title}", "success")
        return redirect(url_for('task_status', task_id=task_id))
    
    except FileNotFoundError:
        flash(f"Book with ID '{book_id}' not found", "danger")
        return redirect(url_for('dashboard'))


@app.route('/task/<task_id>')
def task_status(task_id):
    """View task status"""
    if task_id not in active_tasks:
        flash(f"Task with ID '{task_id}' not found", "danger")
        return redirect(url_for('dashboard'))
    
    return render_template('task_status.html', task_id=task_id, task=active_tasks[task_id])


@app.route('/api/task/<task_id>/status')
def api_task_status(task_id):
    """API endpoint for task status updates"""
    if task_id not in active_tasks:
        return jsonify({"error": "Task not found"}), 404
    
    task = active_tasks[task_id]
    
    # Get logs if available
    logs = []
    if "logger" in task and hasattr(task["logger"], "log_entries"):
        logs = task["logger"].log_entries
    
    response = {
        "status": task["status"],
        "logs": logs,
        "progress": task.get("progress", {}),
        "created_at": task.get("created_at"),
        "start_time": task.get("start_time"),
        "end_time": task.get("end_time"),
        "book_id": task.get("book_id"),
        "error": task.get("error")
    }
    
    return jsonify(response)


@app.route('/api/books')
def api_books():
    """API endpoint to list all books"""
    books = []
    if os.path.exists(BOOKS_DIR):
        for item in os.listdir(BOOKS_DIR):
            item_path = os.path.join(BOOKS_DIR, item)
            metadata_path = os.path.join(item_path, "metadata.json")
            
            if os.path.isdir(item_path) and os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r', encoding='utf-8') as f:
                        metadata = json.load(f)
                        
                        # Check if cover image exists but no path is provided
                        if "cover_image" in metadata and "cover_image_path" not in metadata:
                            # Check if image file exists
                            images_dir = os.path.join(item_path, "images")
                            cover_path = os.path.join(images_dir, "cover.jpg")
                            if os.path.exists(cover_path):
                                # Add the path to metadata
                                metadata["cover_image_path"] = f"/books/{item}/images/cover.jpg"
                        
                        books.append(metadata)
                except Exception as e:
                    logger.warning(f"Error loading metadata for {item}: {str(e)}")
    
    # Sort books by creation date, newest first
    books.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    return jsonify(books)


@app.route('/api/agents')
def api_agents():
    """API endpoint to list available agents and providers"""
    return jsonify({
        "agents": {
            "zero": "Enthusiastic and creative writer",
            "gustave": "Refined and eloquent editor",
            "camille": "Balanced and insightful reviewer"
        },
        "providers": {
            "openai": "OpenAI GPT models (default for Zero and Gustave)",
            "anthropic": "Anthropic Claude models (default for Camille)"
        },
        "default_models": {
            "openai": "gpt-4",
            "anthropic": "claude-3-opus-20240229"
        }
    })


@app.route('/download/<path:filename>')
def download_file(filename):
    """Download an exported book file"""
    return send_from_directory(EXPORTS_DIR, filename, as_attachment=True)


@app.route('/books/<book_id>/images/<filename>')
def book_image(book_id, filename):
    """Serve book images like cover art"""
    book_images_dir = os.path.join(BOOKS_DIR, book_id, "images")
    return send_from_directory(book_images_dir, filename)


@app.route('/sections/<book_id>')
def book_sections(book_id):
    """API endpoint to get a book's sections"""
    try:
        book = Book.load(book_id, directory=BOOKS_DIR)
        sections_data = {}
        
        for section_id, section in book.sections.items():
            sections_data[section_id] = {
                "id": section_id,
                "title": section.title,
                "level": section.level,
                "has_content": bool(section.content),
                "word_count": section.get_word_count()
            }
        
        return jsonify(sections_data)
    except FileNotFoundError:
        return jsonify({"error": "Book not found"}), 404


# Template filters
@app.template_filter('timestamp_to_time')
def timestamp_to_time(timestamp):
    """Convert timestamp to formatted time string"""
    if not timestamp:
        return "N/A"
    return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# Add enumerate function to template context
@app.context_processor
def utility_functions():
    """Make utility functions available to templates"""
    def enumerate_func(sequence, start=0):
        return enumerate(sequence, start)
    return {"enumerate": enumerate_func}


def create_app():
    """Create and configure the Flask application"""
    return app


if __name__ == '__main__':
    app.run(debug=True)
