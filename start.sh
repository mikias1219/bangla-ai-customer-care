#!/bin/bash

# Bangla AI Platform - Quick Start Script

set -e

echo "=========================================="
echo "Bangla AI Platform - Quick Start"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed (V2 uses 'docker compose', V1 uses 'docker-compose')
if ! docker compose version &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

# Determine which Docker Compose command to use
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

echo "✓ Docker and Docker Compose are installed"
echo ""

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✓ .env file created"
        echo "⚠️  Please review and update .env with your configuration"
        echo ""
    else
        echo "❌ env.example not found"
        exit 1
    fi
else
    echo "✓ .env file exists"
    echo ""
fi

# Start services
echo "🚀 Starting services..."
$COMPOSE_CMD up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if backend is ready
echo "🔍 Checking backend health..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "✓ Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start. Check logs with: docker-compose logs backend"
        exit 1
    fi
    sleep 2
done

# Initialize database
echo ""
echo "📦 Initializing database..."
$COMPOSE_CMD exec -T backend python scripts/init_db.py

echo ""
echo "=========================================="
echo "✓ Bangla AI Platform is ready!"
echo "=========================================="
echo ""
echo "🌐 Access the services:"
echo "   Dashboard: http://localhost:5173"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔐 Default admin credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo "   ⚠️  CHANGE THIS IN PRODUCTION!"
echo ""
echo "📊 View logs:"
echo "   $COMPOSE_CMD logs -f"
echo ""
echo "🛑 Stop services:"
echo "   $COMPOSE_CMD down"
echo ""
echo "=========================================="

