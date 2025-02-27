"""
IRC-style logger for agent conversations.
"""
import sys
import time
from typing import Optional, TextIO, Dict, Any
from datetime import datetime
import os


class Logger:
    """
    Logger for agent conversations with IRC-style formatting.
    
    This logger provides an IRC-like interface for logging agent interactions,
    making it easy to follow the conversation between agents and the system.
    """
    
    # ANSI color codes
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "underline": "\033[4m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "gray": "\033[90m"
    }
    
    # Agent colors
    AGENT_COLORS = {
        "Zero": "cyan",
        "Gustave": "magenta",
        "User": "green",
        "System": "gray"
    }
    
    def __init__(
        self,
        output: Optional[TextIO] = None,
        use_colors: bool = True,
        log_to_file: bool = False,
        log_file: Optional[str] = None,
        verbose: bool = True
    ):
        """
        Initialize a logger.
        
        Args:
            output: Output stream (defaults to sys.stdout)
            use_colors: Whether to use ANSI color codes
            log_to_file: Whether to log to a file
            log_file: Path to log file (default: logs/YYYY-MM-DD_HH-MM-SS.log)
            verbose: Whether to print verbose output
        """
        self.output = output or sys.stdout
        self.use_colors = use_colors
        self.log_to_file = log_to_file
        self.verbose = verbose
        
        # Set up file logging if requested
        self.file = None
        if log_to_file:
            if not log_file:
                # Create logs directory if it doesn't exist
                os.makedirs("logs", exist_ok=True)
                
                # Generate a timestamp-based filename
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                log_file = f"logs/{timestamp}.log"
            
            self.file = open(log_file, "a", encoding="utf-8")
    
    def _color(self, text: str, color: str) -> str:
        """
        Apply color to text if colors are enabled.
        
        Args:
            text: Text to color
            color: Color to apply
            
        Returns:
            Colored text (or original text if colors disabled)
        """
        if not self.use_colors:
            return text
        
        color_code = self.COLORS.get(color, "")
        reset_code = self.COLORS["reset"]
        return f"{color_code}{text}{reset_code}"
    
    def _timestamp(self) -> str:
        """
        Get a formatted timestamp.
        
        Returns:
            Formatted timestamp string
        """
        return datetime.now().strftime("%H:%M:%S")
    
    def _log(self, message: str):
        """
        Log a message to the output stream and file.
        
        Args:
            message: Message to log
        """
        # Print to output stream
        print(message, file=self.output)
        self.output.flush()
        
        # Write to file if enabled (without ANSI codes)
        if self.log_to_file and self.file:
            # Strip ANSI codes for file output
            cleaned_message = self._strip_ansi(message)
            self.file.write(f"{cleaned_message}\n")
            self.file.flush()
    
    def _strip_ansi(self, text: str) -> str:
        """
        Strip ANSI color codes from text.
        
        Args:
            text: Text with ANSI codes
            
        Returns:
            Text without ANSI codes
        """
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    def system_message(self, message: str):
        """
        Log a system message.
        
        Args:
            message: Message text
        """
        timestamp = self._timestamp()
        formatted = self._color(f"[{timestamp}] ", "gray") + self._color("*** ", "bold") + message
        self._log(formatted)
    
    def agent_message(self, agent: str, message: str):
        """
        Log an agent message.
        
        Args:
            agent: Agent name
            message: Message text
        """
        timestamp = self._timestamp()
        agent_color = self.AGENT_COLORS.get(agent, "white")
        
        # Format agent name with brackets and color
        agent_formatted = self._color(f"<{agent}>", agent_color)
        
        # Build the full message
        formatted = self._color(f"[{timestamp}] ", "gray") + f"{agent_formatted} {message}"
        self._log(formatted)
    
    def user_message(self, message: str):
        """
        Log a user message.
        
        Args:
            message: Message text
        """
        timestamp = self._timestamp()
        user_formatted = self._color("<User>", "green")
        formatted = self._color(f"[{timestamp}] ", "gray") + f"{user_formatted} {message}"
        self._log(formatted)
    
    def success(self, message: str):
        """
        Log a success message.
        
        Args:
            message: Message text
        """
        timestamp = self._timestamp()
        formatted = self._color(f"[{timestamp}] ", "gray") + self._color("✓ ", "green") + message
        self._log(formatted)
    
    def warning(self, message: str):
        """
        Log a warning message.
        
        Args:
            message: Message text
        """
        timestamp = self._timestamp()
        formatted = self._color(f"[{timestamp}] ", "gray") + self._color("⚠ ", "yellow") + message
        self._log(formatted)
    
    def error(self, message: str):
        """
        Log an error message.
        
        Args:
            message: Message text
        """
        timestamp = self._timestamp()
        formatted = self._color(f"[{timestamp}] ", "gray") + self._color("✗ ", "red") + message
        self._log(formatted)
    
    def debug(self, message: str):
        """
        Log a debug message (only if verbose).
        
        Args:
            message: Message text
        """
        if not self.verbose:
            return
        
        timestamp = self._timestamp()
        formatted = self._color(f"[{timestamp}] ", "gray") + self._color("# ", "blue") + message
        self._log(formatted)
    
    def log_dict(self, data: Dict[str, Any], title: Optional[str] = None):
        """
        Log a dictionary with formatting.
        
        Args:
            data: Dictionary to log
            title: Optional title for the log
        """
        if not self.verbose:
            return
        
        if title:
            self.debug(title)
        
        timestamp = self._timestamp()
        prefix = self._color(f"[{timestamp}] ", "gray") + self._color("# ", "blue")
        
        for key, value in data.items():
            key_formatted = self._color(f"{key}: ", "bold")
            self._log(f"{prefix}{key_formatted}{value}")
    
    def close(self):
        """Close the log file if open."""
        if self.log_to_file and self.file:
            self.file.close()
            self.file = None
    
    def __del__(self):
        """Ensure log file is closed on deletion."""
        self.close()
