# AI Doctor Assistant - Firebase Local Setup Script (PowerShell)
# This script sets up the project for local development using Firebase emulator

Write-Host "🚀 Setting up AI Doctor Assistant for Firebase Local Development" -ForegroundColor Green

# Check if Node.js is installed
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js version: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js is not installed. Please install Node.js from https://nodejs.org/" -ForegroundColor Red
    Write-Host "   After installing Node.js, run this script again." -ForegroundColor Yellow
    exit 1
}

# Check if npm is installed
try {
    $npmVersion = npm --version
    Write-Host "✅ npm version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ npm is not installed. Please install npm." -ForegroundColor Red
    exit 1
}

# Install Firebase CLI globally
Write-Host "📦 Installing Firebase CLI..." -ForegroundColor Yellow
npm install -g firebase-tools

# Install function dependencies
Write-Host "📦 Installing function dependencies..." -ForegroundColor Yellow
Set-Location functions
npm install
Set-Location ..

# Create .env file from example
Write-Host "🔧 Setting up environment variables..." -ForegroundColor Yellow
if (-not (Test-Path "functions/.env")) {
    Copy-Item "functions/env.example" "functions/.env"
    Write-Host "✅ Created functions/.env from template" -ForegroundColor Green
    Write-Host "⚠️  Please edit functions/.env and add your API keys:" -ForegroundColor Yellow
    Write-Host "   - OPENAI_API_KEY" -ForegroundColor Cyan
    Write-Host "   - GOOGLE_API_KEY (optional, for Gemini)" -ForegroundColor Cyan
} else {
    Write-Host "✅ functions/.env already exists" -ForegroundColor Green
}

# Initialize Firebase project (if not already done)
if (-not (Test-Path ".firebaserc")) {
    Write-Host "🔥 Initializing Firebase project..." -ForegroundColor Yellow
    firebase init emulators --project demo-aidoctor
} else {
    Write-Host "✅ Firebase project already initialized" -ForegroundColor Green
}

Write-Host ""
Write-Host "🎉 Setup complete! Next steps:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Edit functions/.env and add your API keys:" -ForegroundColor White
Write-Host "   - OPENAI_API_KEY=your_openai_api_key_here" -ForegroundColor Cyan
Write-Host "   - GOOGLE_API_KEY=your_google_api_key_here (optional)" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Start the Firebase emulator:" -ForegroundColor White
Write-Host "   firebase emulators:start" -ForegroundColor Cyan
Write-Host ""
Write-Host "3. The emulator will be available at:" -ForegroundColor White
Write-Host "   - Functions: http://localhost:5001" -ForegroundColor Cyan
Write-Host "   - Emulator UI: http://localhost:4000" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Test the API endpoints using the test script:" -ForegroundColor White
Write-Host "   python test_api.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "5. For frontend development, run:" -ForegroundColor White
Write-Host "   cd frontend && npm install && npm run dev" -ForegroundColor Cyan 