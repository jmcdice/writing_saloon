"""
Web UI for the Agent Saloon collaborative AI writing system.

This module provides a Flask-based web interface for interacting with
the Agent Saloon system, allowing users to create, view, and manage
AI-generated books through a browser.
"""

from .app import create_app, app

__all__ = ['create_app', 'app']

