#!/bin/bash

# AI Doctor Assistant - Local Firebase Emulation Setup
# This script sets up and runs the AI Doctor Assistant locally using Firebase emulation

set -e

echo "🏥 AI Doctor Assistant - Local Firebase Emulation Setup"
echo "========================================================"

# Check if required tools are installed
check_requirements() {
    echo "🔍 Checking requirements..."
    
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js is not installed. Please install Node.js 18+"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo "❌ npm is not installed. Please install npm"
        exit 1
    fi
    
    if ! command -v firebase &> /dev/null; then
        echo "❌ Firebase CLI is not installed. Please install it with: npm install -g firebase-tools"
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is not installed. Please install Python 3.9+"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        echo "❌ Docker is not installed. Please install Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "❌ Docker Compose is not installed. Please install Docker Compose"
        exit 1
    fi
    
    echo "✅ All requirements met!"
}

# Setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    # Check if .env file exists in functions directory
    if [ ! -f "functions/.env" ]; then
        echo "⚠️  functions/.env file not found!"
        echo "📝 Creating functions/.env from functions/env.example"
        cp functions/env.example functions/.env
        echo "🔑 Please edit functions/.env with your API keys:"
        echo "   - OPENAI_API_KEY"
        echo "   - GOOGLE_API_KEY"
        echo "   - PYTHON_SERVICE_URL=http://localhost:8000"
    fi
    
    # Check if .env file exists in root directory for Docker Compose
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env for Docker Compose"
        cat > .env << EOF
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Google AI Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Python Microservice URL (for local development)
PYTHON_SERVICE_URL=http://localhost:8000
EOF
        echo "🔑 Please edit .env with your API keys"
    fi
    
    echo "✅ Environment setup complete!"
}

# Install dependencies
install_dependencies() {
    echo "📦 Installing dependencies..."
    
    # Install frontend dependencies
    echo "   Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    # Install functions dependencies
    echo "   Installing functions dependencies..."
    cd functions
    npm install
    cd ..
    
    # Install Python microservice dependencies
    echo "   Installing Python microservice dependencies..."
    cd python-service
    pip install -r requirements.txt
    cd ..
    
    echo "✅ Dependencies installed!"
}

# Start services with Docker Compose
start_services() {
    echo "🚀 Starting services with Docker Compose..."
    
    # Build and start all services
    docker-compose up --build -d
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    echo "✅ Services started!"
    echo ""
    echo "🌐 Frontend: http://localhost:5173"
    echo "🔧 Firebase Functions: http://localhost:5001"
    echo "🐍 Python Microservice: http://localhost:8000"
    echo "📊 MLflow: http://localhost:5000"
    echo "🔥 Firebase Emulator UI: http://localhost:4000"
    echo ""
    echo "🧪 Available test endpoints:"
    echo "   • http://localhost:5001/health          - Health check"
    echo "   • http://localhost:8000/health          - Python service health"
    echo "   • http://localhost:5001/process         - Process text"
    echo "   • http://localhost:5001/transcribe      - Transcribe audio"
    echo "   • http://localhost:5001/processAudio    - Complete audio processing"
    echo "   • http://localhost:5001/saveMemory      - Save to memory"
    echo "   • http://localhost:5001/queryMemory     - Query memory"
    echo ""
    echo "🛑 To stop services: docker-compose down"
    echo "📋 To view logs: docker-compose logs -f"
    
    # Keep the script running
    echo ""
    echo "🔄 Services are running. Press Ctrl+C to stop."
    docker-compose logs -f
}

# Stop services
stop_services() {
    echo "🛑 Stopping services..."
    docker-compose down
    echo "✅ Services stopped!"
}

# Test the setup
test_setup() {
    echo "🧪 Testing setup..."
    
    # Test Python microservice
    echo "   Testing Python microservice..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Python microservice is running"
    else
        echo "   ❌ Python microservice is not responding"
    fi
    
    # Test Firebase Functions
    echo "   Testing Firebase Functions..."
    if curl -f http://localhost:5001/health > /dev/null 2>&1; then
        echo "   ✅ Firebase Functions are running"
    else
        echo "   ❌ Firebase Functions are not responding"
    fi
    
    # Test frontend
    echo "   Testing frontend..."
    if curl -f http://localhost:5173 > /dev/null 2>&1; then
        echo "   ✅ Frontend is running"
    else
        echo "   ❌ Frontend is not responding"
    fi
    
    echo "✅ Setup test complete!"
}

# Main execution
main() {
    case "${1:-start}" in
        "start")
            check_requirements
            setup_environment
            install_dependencies
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "test")
            test_setup
            ;;
        "restart")
            stop_services
            start_services
            ;;
        "logs")
            docker-compose logs -f
            ;;
        *)
            echo "Usage: $0 {start|stop|test|restart|logs}"
            echo ""
            echo "Commands:"
            echo "  start   - Start all services (default)"
            echo "  stop    - Stop all services"
            echo "  test    - Test if services are running"
            echo "  restart - Restart all services"
            echo "  logs    - View service logs"
            exit 1
            ;;
    esac
}

# Run main function
main "$@" 