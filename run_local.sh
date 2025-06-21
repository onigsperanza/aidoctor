#!/bin/bash

echo "🏥 AI Doctor Assistant - Local Development"
echo "=========================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if dev.env exists
if [ ! -f "dev.env" ]; then
    echo "❌ dev.env file not found. Please create it with your API keys:"
    echo "   cp env.example dev.env"
    echo "   # Then edit dev.env with your OpenAI API key"
    exit 1
fi

echo "🚀 Starting backend..."
echo "   Building Docker image..."
docker build -t ai-backend . 

if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker image"
    exit 1
fi

echo "   Starting backend container..."
docker run -d --name ai-backend-container -p 8000:8000 --env-file dev.env ai-backend

if [ $? -ne 0 ]; then
    echo "❌ Failed to start backend container"
    exit 1
fi

echo "✅ Backend started on http://localhost:8000"
echo "   API docs: http://localhost:8000/docs"

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
sleep 10

# Check if backend is responding
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is ready!"
else
    echo "⚠️  Backend might still be starting up..."
fi

echo ""
echo "🎨 Starting frontend..."
echo "   Installing dependencies..."

cd frontend
if [ ! -f ".env.local" ]; then
    echo "   Creating .env.local..."
    echo "VITE_API_URL=http://localhost:8000" > .env.local
fi

npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies"
    exit 1
fi

echo "   Starting frontend development server..."
npm run dev &

if [ $? -ne 0 ]; then
    echo "❌ Failed to start frontend"
    exit 1
fi

echo "✅ Frontend started on http://localhost:5173"
echo ""
echo "🎉 AI Doctor Assistant is running!"
echo "=================================="
echo "Frontend: http://localhost:5173"
echo "Backend API: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "To stop the services:"
echo "  docker stop ai-backend-container"
echo "  docker rm ai-backend-container"
echo "  # Frontend will stop when you press Ctrl+C"
echo ""
echo "Happy coding! 🚀" 