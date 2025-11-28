#!/bin/bash

# Launch script for test.py
# Usage: ./run_tests.sh

set -e

echo "🚀 Launching AI DIAL Simple Agent Test Suite"
echo "=============================================="

# Navigate to project directory
cd "$(dirname "$0")" || exit 1

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if DIAL_API_KEY is set
if [ -z "$DIAL_API_KEY" ]; then
    echo "⚠️  DIAL_API_KEY not set. Using default from test.py"
    echo "   To set: export DIAL_API_KEY='your-key-here'"
else
    echo "✅ DIAL_API_KEY is set"
fi

# Check if Docker services are running
echo "🐳 Checking Docker services..."
if docker compose ps | grep -q "Up"; then
    echo "✅ Docker services are running"
else
    echo "⚠️  Docker services may not be running"
    echo "   Starting Docker services..."
    docker compose up -d
    echo "   Waiting 10 seconds for services to initialize..."
    sleep 10
fi

# Check User Service health
echo "🏥 Checking User Service health..."
if curl -s http://localhost:8041/health > /dev/null 2>&1; then
    echo "✅ User Service is healthy"
else
    echo "⚠️  User Service may not be ready yet"
    echo "   Waiting additional 10 seconds..."
    sleep 10
fi

# Run tests
echo ""
echo "🧪 Running test suite..."
echo "=============================================="
python test.py

echo ""
echo "✅ Test suite completed!"

