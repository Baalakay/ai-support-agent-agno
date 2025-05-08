#!/usr/bin/env python3
"""
Run script for the AI Support Agent.

This script runs the FastAPI application for the AI Support Agent.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def run_app():
    """Run the FastAPI application."""
    try:
        import uvicorn
        from ai_support_agent.config import get_config
        
        # Get configuration
        config = get_config()
        host = config["api"]["host"]
        port = config["api"]["port"]
        
        # Run the application
        print(f"Starting AI Support Agent on http://{host}:{port}")
        uvicorn.run(
            "ai_support_agent.main:app",
            host=host,
            port=port,
            reload=config["api"]["debug"]
        )
    except ImportError as e:
        print(f"Error: {e}")
        print("Please make sure all dependencies are installed.")
        print("Run: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Add src directory to Python path
    src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
    if os.path.exists(src_dir):
        sys.path.insert(0, src_dir)
    
    # Run the application
    run_app() 