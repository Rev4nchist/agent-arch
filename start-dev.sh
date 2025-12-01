#!/bin/bash
# Development startup script with reverse proxy (No CORS issues!)

echo "========================================"
echo "Agent Architecture Dev Environment"
echo "========================================"
echo

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running!"
    echo "Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"
echo

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo
    if [ -f .env.example ]; then
        echo "Creating .env from template..."
        cp .env.example .env
        echo "✅ Created .env file"
        echo
        echo "🔧 IMPORTANT: Edit .env with your Azure credentials before continuing!"
        echo
        read -p "Press Enter to edit .env file..."
        ${EDITOR:-nano} .env
    else
        echo "❌ .env.example not found. Please create .env manually."
        exit 1
    fi
fi

echo "✅ .env file exists"
echo

echo "Starting services with Docker Compose..."
echo
echo "📍 Frontend + Backend + Reverse Proxy"
echo "🌐 Access at: http://localhost:8080"
echo "📊 Backend API: http://localhost:8080/api"
echo
echo "Press Ctrl+C to stop all services"
echo

docker-compose up --build
