"""
Global settings and configuration.
"""
import os
from typing import Dict, Any
import json

# Default configuration
DEFAULT_CONFIG = {
    # OpenAI API settings
    "openai": {
        "api_key": None,  # Set via environment variable
        "default_model": "gpt-4"
    },
    
    # Book generation settings
    "book": {
        "title_generation": {
            "max_attempts": 10,
            "force_consensus": True
        },
        "toc_generation": {
            "max_attempts": 10,
            "force_consensus": True,
            "min_chapters": 5,
            "max_chapters": 10
        },
        "section_generation": {
            "max_attempts": 10,
            "force_consensus": True,
            "min_words": 500,
            "max_words": 2000
        },
        "default_output_dir": "books"
    },
    
    # Logging settings
    "logging": {
        "use_colors": True,
        "log_to_file": True,
        "verbose": True
    }
}


class Settings:
    """
    Settings manager for the application.
    
    This class handles loading, saving, and accessing configuration
    settings for the application.
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize settings.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        
        # Apply environment variables
        self._apply_env_vars()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file or use defaults.
        
        Returns:
            Configuration dictionary
        """
        # Start with default configuration
        config = DEFAULT_CONFIG.copy()
        
        # Try to load from file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    file_config = json.load(f)
                
                # Update defaults with file values
                self._update_nested_dict(config, file_config)
            except Exception as e:
                print(f"Error loading config file: {str(e)}")
        
        return config
    
    def _update_nested_dict(self, d: Dict[str, Any], u: Dict[str, Any]):
        """
        Update a nested dictionary with values from another dictionary.
        
        Args:
            d: Target dictionary to update
            u: Source dictionary with updates
        """
        for k, v in u.items():
            if isinstance(v, dict) and k in d and isinstance(d[k], dict):
                self._update_nested_dict(d[k], v)
            else:
                d[k] = v
    
    def _apply_env_vars(self):
        """Apply environment variables to the configuration."""
        # Apply OpenAI API key from environment
        if os.environ.get("OPENAI_API_KEY"):
            self.config["openai"]["api_key"] = os.environ["OPENAI_API_KEY"]
    
    def save(self):
        """Save the current configuration to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)
    
    def get(self, key_path: str, default=None) -> Any:
        """
        Get a configuration value by its key path.
        
        Args:
            key_path: Dot-separated path to the configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split(".")
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        Set a configuration value by its key path.
        
        Args:
            key_path: Dot-separated path to the configuration key
            value: Value to set
        """
        keys = key_path.split(".")
        config = self.config
        
        # Navigate to the correct dict
        for key in keys[:-1]:
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
    
    def __getitem__(self, key: str) -> Any:
        """
        Get a top-level configuration section.
        
        Args:
            key: Top-level configuration key
            
        Returns:
            Configuration section
        """
        return self.config.get(key, {})


# Global settings instance
settings = Settings()
