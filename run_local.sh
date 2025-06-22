#!/bin/bash

# AI Doctor Assistant - Firebase Local Development Script

echo "🏥 AI Doctor Assistant - Firebase Local Development"
echo "==================================================="

# Function to check if a command exists
command_exists () {
    type "$1" &> /dev/null ;
}

# 1. Check for prerequisites
echo "🔎 Checking prerequisites..."

if ! command_exists firebase; then
    echo "❌ Firebase CLI not found. Please install it: npm install -g firebase-tools"
    exit 1
fi
echo "✅ Firebase CLI is installed."

if ! command_exists node; then
    echo "❌ Node.js not found. Please install it."
    exit 1
fi
echo "✅ Node.js is installed."

# 2. Check for Firebase project initialization
if [ ! -f "firebase.json" ]; then
    echo "⚠️ firebase.json not found. You might need to run 'firebase init' first."
    # For this project, firebase.json should already be in the repo.
fi

# 3. Backend (Firebase Functions) Setup
echo "🚀 Setting up Backend (Firebase Functions)..."
cd functions

if [ ! -f ".env" ]; then
    echo "⚠️ '.env' file not found in 'functions' directory."
    echo "Please create it with your API keys by copying 'env.example'."
    echo "Example 'functions/.env' content:"
    echo "OPENAI_API_KEY=your_openai_api_key_here"
    echo "GOOGLE_API_KEY=your_google_api_key_here"
    # cp env.example .env
    # echo "Then edit .env with your actual keys."
    # exit 1 # Exit because keys are required for the backend to run.
fi

echo "📦 Installing backend dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install backend dependencies."
    exit 1
fi
echo "✅ Backend dependencies installed."
cd ..


# 4. Frontend (React App) Setup
echo "🎨 Setting up Frontend (React App)..."
cd frontend

if [ ! -f ".env.local" ]; then
    echo "   Creating .env.local for frontend..."
    # The functions emulator runs on port 5001 by default
    echo "VITE_API_URL=http://127.0.0.1:5001/aidoctor-dev/us-central1" > .env.local
fi


echo "📦 Installing frontend dependencies..."
npm install
if [ $? -ne 0 ]; then
    echo "❌ Failed to install frontend dependencies."
    exit 1
fi
echo "✅ Frontend dependencies installed."

echo "启动前端开发服务器..."
npm run dev &
FRONTEND_PID=$!
cd ..

# 5. Start Firebase Emulators
echo "🔥 Starting Firebase Emulators (Functions & Firestore)..."
firebase emulators:start --only functions,firestore --project aidoctor-dev

# When emulators are stopped (Ctrl+C), stop the frontend server too
kill $FRONTEND_PID

echo "🛑 Services stopped."
echo "👋 Goodbye!" 