#!/bin/bash

echo "🚀 Starting LoopPhones Backend Setup..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Copy .env if not exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your configuration"
fi

# Check if PostgreSQL is running
echo "🔍 Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL client found"
else
    echo "⚠️  PostgreSQL client not found. Install PostgreSQL or use Docker."
fi

# Check if Redis is running
echo "🔍 Checking Redis..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        echo "✅ Redis is running"
    else
        echo "⚠️  Redis is not running. Start Redis or use Docker."
    fi
else
    echo "⚠️  Redis client not found. Install Redis or use Docker."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Update .env with your database credentials"
echo "2. Create PostgreSQL database: createdb loopphones"
echo "3. Start Redis if not running: redis-server"
echo "4. Run the backend: python main.py"
echo ""
echo "Or use Docker:"
echo "  docker-compose up"
echo ""
echo "📚 API Documentation will be available at:"
echo "  http://localhost:8000/docs"
