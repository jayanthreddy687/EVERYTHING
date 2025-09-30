#!/bin/bash

set -e

echo "Starting up the AI agent system..."
echo ""

# check if docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker not found. Please install it first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose not found. Please install it first."
    exit 1
fi

# check for .env file
if [ ! -f .env ]; then
    echo "No .env file found."
    read -p "Do you have a Gemini API key? (y/n): " has_key
    
    if [ "$has_key" = "y" ]; then
        read -p "Enter your API key: " api_key
        echo "GEMINI_API_KEY=$api_key" > .env
        echo "Saved to .env"
    else
        echo "GEMINI_API_KEY=" > .env
        echo "No worries, running in fallback mode"
    fi
    echo ""
fi

echo "Building containers..."
docker-compose up -d --build

echo ""
echo "Waiting for services..."
sleep 3

# wait for backend
attempt=0
while [ $attempt -lt 30 ]; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend ready"
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

if [ $attempt -eq 30 ]; then
    echo "Backend took too long to start. Check logs with: docker-compose logs backend"
    exit 1
fi

# wait for frontend
attempt=0
while [ $attempt -lt 30 ]; do
    if curl -s http://localhost:5173 > /dev/null 2>&1; then
        echo "Frontend ready"
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

if [ $attempt -eq 30 ]; then
    echo "Frontend took too long to start. Check logs with: docker-compose logs frontend"
    exit 1
fi

echo ""
echo "All set! System is running."
echo ""
echo "Open these URLs:"
echo "  http://localhost:5173 - main app"
echo "  http://localhost:8000/docs - api documentation"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop: docker-compose down"
echo ""