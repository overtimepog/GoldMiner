#!/bin/bash

# GoldMiner All-in-One Startup Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 GoldMiner AI Startup Validator${NC}"
echo "=================================="

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Docker installation
if ! command_exists docker; then
    echo -e "${RED}❌ Docker is not installed!${NC}"
    echo "Please install Docker from: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check Docker Compose installation
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is not installed!${NC}"
    echo "Please install Docker Compose from: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}📝 Please edit .env file and add your OpenRouter API key${NC}"
        echo "   Get your free API key at: https://openrouter.ai/"
        echo ""
        read -p "Press Enter after adding your API key to .env file..."
    else
        echo -e "${RED}❌ .env.example file not found!${NC}"
        exit 1
    fi
fi

# Check if API key is set
if grep -q "OPENROUTER_API_KEY=your_openrouter_api_key_here" .env || grep -q "OPENROUTER_API_KEY=$" .env; then
    echo -e "${RED}❌ OpenRouter API key not set in .env file!${NC}"
    echo "Please edit .env file and add your API key"
    exit 1
fi

# Create necessary directories
echo -e "${GREEN}📁 Creating directories...${NC}"
mkdir -p data logs

# Stop any existing containers
echo -e "${GREEN}🛑 Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Build the Docker image
echo -e "${GREEN}🔨 Building Docker image...${NC}"
docker-compose build

# Start the services
echo -e "${GREEN}🚀 Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo -e "${GREEN}⏳ Waiting for services to start...${NC}"
sleep 10

# Check if services are running
if curl -s http://localhost:8000/health > /dev/null; then
    echo -e "${GREEN}✅ API is running!${NC}"
else
    echo -e "${RED}❌ API failed to start. Check logs with: docker-compose logs${NC}"
    exit 1
fi

# Display success message
echo ""
echo -e "${GREEN}✨ GoldMiner 2.0 Enhanced is running!${NC}"
echo "=================================="
echo -e "🌐 Enhanced Web UI: ${GREEN}http://localhost:8501${NC}"
echo -e "📡 API: ${GREEN}http://localhost:8000${NC}"
echo -e "📚 API Docs: ${GREEN}http://localhost:8000/docs${NC}"
echo -e "🔌 WebSocket: ${GREEN}ws://localhost:8000/ws${NC}"
echo ""
echo -e "${GREEN}🆕 New Features:${NC}"
echo "  • Real-time goldmining progress with stop/pause"
echo "  • Full idea management (edit, delete, validate)"
echo "  • Kanban board view with status columns"
echo "  • Advanced filtering and sorting"
echo "  • Export to CSV, JSON, and Markdown"
echo ""
echo -e "${YELLOW}Commands:${NC}"
echo "  View logs:    docker-compose logs -f"
echo "  Stop:         docker-compose down"
echo "  Restart:      docker-compose restart"
echo ""
echo -e "${GREEN}Press Ctrl+C to stop viewing logs...${NC}"

# Show logs
docker-compose logs -f