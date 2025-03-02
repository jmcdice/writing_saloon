#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p books exports logs templates static

# Copy templates
mkdir -p templates
cp *.html templates/

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the app
echo "Starting Flask application..."
python app.py
