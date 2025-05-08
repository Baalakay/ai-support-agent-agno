"""
Configuration module for the AI Support Agent.

This module handles loading and accessing configuration settings from environment variables.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional

# Base configuration
config: Dict[str, Any] = {
    # API Configuration
    "api": {
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "8000")),
        "debug": os.getenv("DEBUG", "False").lower() in ("true", "1", "t"),
    },
    
    # Path Configuration
    "paths": {
        "data_dir": os.getenv("DATA_DIR", "./data"),
        "pdf_dir": os.getenv("PDF_DIR", "./data/pdf"),
        "diagram_dir": os.getenv("DIAGRAM_DIR", "./data/diagrams"),
        "processed_dir": os.getenv("PROCESSED_DIR", "./data/processed"),
    },
    
    # Logging
    "logging": {
        "log_level": os.getenv("LOG_LEVEL", "INFO"),
    },
}

def get_config() -> Dict[str, Any]:
    """
    Get the configuration settings from environment variables.
    
    Returns:
        Dict[str, Any]: A dictionary containing the configuration settings.
    """
    return config

def ensure_directories_exist() -> None:
    """
    Ensure that the necessary directories exist.
    
    Creates all required directories if they don't exist.
    """
    config = get_config()
    paths = config["paths"]
    
    # Create all directories if they don't exist
    for dir_path in paths.values():
        path = Path(dir_path)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True) 