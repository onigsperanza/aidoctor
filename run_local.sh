#!/bin/bash

# AI Doctor Assistant - Local Development Script
# This script sets up and runs the AI Doctor Assistant locally

set -e

echo "🏥 AI Doctor Assistant - Local Development Setup"
echo "================================================"

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
    
    echo "✅ All requirements met!"
}

# Setup environment
setup_environment() {
    echo "🔧 Setting up environment..."
    
    # Check if .env file exists in functions directory
    if [ ! -f "functions/.env" ]; then
        echo "⚠️  functions/.env file not found!"
        echo "📝 Please create functions/.env from functions/env.example"
        echo "   cd functions && cp env.example .env"
        echo "   Then edit .env with your API keys:"
        echo "   - OPENAI_API_KEY"
        echo "   - GOOGLE_API_KEY" 
        echo "   - MLFLOW_TRACKING_URI"
        echo "   - MedCAT and SNOMED configuration"
        exit 1
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
    
    echo "✅ Dependencies installed!"
}

# Start services
start_services() {
    echo "🚀 Starting services..."
    
    # Start Firebase emulator in background
    echo "   Starting Firebase emulator..."
    firebase emulators:start --only functions,firestore &
    FIREBASE_PID=$!
    
    # Wait for emulator to start
    echo "   Waiting for emulator to start..."
    sleep 10
    
    # Start frontend
    echo "   Starting React frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started!"
    echo ""
    echo "🌐 Frontend: http://localhost:5173"
    echo "🔧 Firebase Functions: http://localhost:5001"
    echo "📊 Firebase Emulator UI: http://localhost:4000"
    echo ""
    echo "🧪 Available test scripts:"
    echo "   • python test_api.py          - Comprehensive API tests"
    echo "   • python demo_ner_snomed.py   - NER & SNOMED validation demo"
    echo ""
    echo "🛑 To stop services: Ctrl+C"
    
    # Wait for user to stop
    wait $FIREBASE_PID $FRONTEND_PID
}

# Main execution
main() {
    check_requirements
    setup_environment
    install_dependencies
    start_services
}

# Run main function
main "$@" 