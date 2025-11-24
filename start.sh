#!/bin/bash

# D&D Character Generator Startup Script

echo "🎲 Starting D&D Character Generator..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if Ollama is running
echo "🤖 Checking Ollama service..."
if ! curl -s http://0.0.0.0:11434/api/tags > /dev/null; then
    echo "⚠️  Ollama is not running on 0.0.0.0:11434"
    echo "Please ensure Ollama is running on the remote server with models:"
    echo "  - llama3.1"
    echo "  - granite3.2-vision"
    echo "The app will still start but character descriptions won't work"
fi

# Check if ComfyUI is running
echo "🎨 Checking ComfyUI service..."
if ! curl -s http://0.0.0.0:8188 > /dev/null; then
    echo "⚠️  ComfyUI is not running on 0.0.0.0:8188"
    echo "Please ensure ComfyUI is running on the remote server"
    echo "The app will still start but image generation won't work"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads generated

# Start the Flask application
echo "🚀 Starting Flask application..."
echo "Access the app at: http://localhost:5000"
echo "Press Ctrl+C to stop"
echo "=========================================="

python app.py
