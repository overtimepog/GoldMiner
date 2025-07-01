#!/bin/bash

# GoldMiner Setup Script

echo "🔧 Setting up GoldMiner development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📈 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Copy .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your OpenRouter API key"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To run GoldMiner:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Add your OpenRouter API key to .env file"
echo "3. Run the application: ./run.sh"