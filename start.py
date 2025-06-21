#!/usr/bin/env python3
"""
Startup script for AI Doctor Assistant
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        "fastapi",
        "uvicorn",
        "openai",
        "google.generativeai",
        "whisper"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} not found")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    
    return True

def check_environment():
    """Check if required environment variables are set."""
    required_vars = ["OPENAI_API_KEY", "GOOGLE_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"❌ {var} not set")
        else:
            print(f"✅ {var} configured")
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set them in your .env file or environment")
        print("You can copy env.example to .env and fill in your API keys")
        return False
    
    return True

def create_directories():
    """Create necessary directories."""
    directories = ["logs", "prompts"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def start_server():
    """Start the FastAPI server."""
    print("\n🚀 Starting AI Doctor Assistant...")
    print("=" * 50)
    
    try:
        # Start the server
        subprocess.run([
            sys.executable, "-m", "uvicorn",
            "main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main startup function."""
    print("🏥 AI Doctor Assistant Startup")
    print("=" * 30)
    
    # Run checks
    checks = [
        check_python_version,
        check_dependencies,
        check_environment,
        create_directories
    ]
    
    for check in checks:
        if not check():
            print("\n❌ Startup checks failed. Please fix the issues above.")
            sys.exit(1)
    
    print("\n✅ All checks passed!")
    
    # Start server
    start_server()

if __name__ == "__main__":
    main() 