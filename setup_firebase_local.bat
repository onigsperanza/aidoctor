@echo off
echo 🚀 Setting up AI Doctor Assistant for Firebase Local Development
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js from https://nodejs.org/
    echo    After installing Node.js, run this script again.
    pause
    exit /b 1
)

echo ✅ Node.js version: 
node --version

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ npm is not installed. Please install npm.
    pause
    exit /b 1
)

echo ✅ npm version:
npm --version

REM Install Firebase CLI globally
echo 📦 Installing Firebase CLI...
npm install -g firebase-tools

REM Install function dependencies
echo 📦 Installing function dependencies...
cd functions
npm install
cd ..

REM Create .env file from example
echo 🔧 Setting up environment variables...
if not exist "functions\.env" (
    copy "functions\env.example" "functions\.env"
    echo ✅ Created functions\.env from template
    echo ⚠️  Please edit functions\.env and add your API keys:
    echo    - OPENAI_API_KEY
    echo    - GOOGLE_API_KEY (optional, for Gemini)
) else (
    echo ✅ functions\.env already exists
)

REM Initialize Firebase project (if not already done)
if not exist ".firebaserc" (
    echo 🔥 Initializing Firebase project...
    firebase init emulators --project demo-aidoctor
) else (
    echo ✅ Firebase project already initialized
)

echo.
echo 🎉 Setup complete! Next steps:
echo.
echo 1. Edit functions\.env and add your API keys:
echo    - OPENAI_API_KEY=your_openai_api_key_here
echo    - GOOGLE_API_KEY=your_google_api_key_here (optional)
echo.
echo 2. Start the Firebase emulator:
echo    firebase emulators:start
echo.
echo 3. The emulator will be available at:
echo    - Functions: http://localhost:5001
echo    - Emulator UI: http://localhost:4000
echo.
echo 4. Test the API endpoints using the test script:
echo    python test_firebase_emulator.py
echo.
echo 5. For frontend development, run:
echo    cd frontend ^&^& npm install ^&^& npm run dev
echo.
pause 