#!/bin/bash

echo "🚀 Starting NTDF Backend Server..."
echo "=================================="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Start server
echo ""
echo "Starting FastAPI server on port 8000..."
echo "=================================="
echo "API: http://0.0.0.0:8000"
echo "Docs: http://0.0.0.0:8000/docs"
echo "Health: http://0.0.0.0:8000/health"
echo "=================================="
echo ""

uvicorn simple_main:app --host 0.0.0.0 --port 8000 --reload
