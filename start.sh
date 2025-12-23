#!/bin/bash

# Start script for Life is a Joke application
# This script can be used to start the application in production

set -e

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Set default port if not set
export PORT=${PORT:-5000}

# Check if .env file exists, if not create from example
if [ ! -f ".env" ]; then
    echo ".env file not found. Creating from .env.example..."
    cp .env.example .env
fi

# Load environment variables
if [ -f ".env" ]; then
    set -a
    source .env
    set +a
fi

echo "Starting Life is a Joke application on port $PORT..."

# Start with Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 60 --access-logfile - --error-logfile - app:app
