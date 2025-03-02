FROM python:3.10-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Install the package with all dependencies
RUN pip install --no-cache-dir -e .

# Create necessary directories
RUN mkdir -p /app/books /app/exports /app/logs

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=agent_saloon.web.app

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "agent_saloon.web.app:app"]

