#!/bin/bash

# Installation script for ROFL Trading Bot

set -e

echo "📦 Installing ROFL Trading Bot..."

# Install Python dependencies
pip install -r requirements.txt

# Create necessary directories
mkdir -p logs data configs

echo "✓ Installation complete"
echo "Run 'python -m src.main' to start the bot"