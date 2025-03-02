#!/usr/bin/env python
"""
Run script for Agent Saloon Web UI.
"""

import os
import argparse
import logging
from agent_saloon.web.app import app

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run the Agent Saloon Web UI")
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind to")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind to")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()

def main():
    """Run the web application."""
    args = parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    
    # Print startup information
    print(f"Starting Agent Saloon Web UI on http://{args.host}:{args.port}")
    print("Press Ctrl+C to quit")
    
    # Run the application
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )

if __name__ == "__main__":
    main()
