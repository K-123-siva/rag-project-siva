#!/bin/bash

# NeuroQuery Deployment Script

echo "🚀 Starting NeuroQuery deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p db logs

# Build and start the application
echo "🔨 Building Docker image..."
docker-compose build

echo "🚀 Starting NeuroQuery..."
docker-compose up -d

echo "✅ NeuroQuery is now running!"
echo "📱 Access your application at: http://localhost:8501"
echo "📊 View logs with: docker-compose logs -f"
echo "🛑 Stop with: docker-compose down"