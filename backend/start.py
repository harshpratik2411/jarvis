#!/usr/bin/env python3
"""
JARVIS Backend Startup Script
Handles setup, dependency checks, and server startup
"""
import sys
import subprocess
import os
from pathlib import Path


def check_python_version():
    """Check Python version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")


def install_dependencies():
    """Install required packages"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✓ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)


def check_ollama():
    """Check if Ollama is installed and running"""
    print("\n🤖 Checking Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✓ Ollama running with {len(models)} models")
            
            # Check for llama2
            model_names = [m.get("name", "") for m in models]
            if "llama2" not in model_names:
                print("⚠️  llama2 model not found. Install with: ollama pull llama2")
            else:
                print("✓ llama2 model available")
        else:
            print("⚠️  Ollama not responding correctly")
    except Exception as e:
        print(f"⚠️  Ollama not running or not installed")
        print("   Install from: https://ollama.ai")
        print("   Then run: ollama run llama2")


def download_whisper_model():
    """Download Whisper model"""
    print("\n🎤 Setting up Whisper...")
    try:
        import whisper
        print("Downloading Whisper base model (this may take a minute)...")
        whisper.load_model("base")
        print("✓ Whisper model ready")
    except Exception as e:
        print(f"⚠️  Could not download Whisper model: {e}")


def create_directories():
    """Create necessary directories"""
    dirs = ["logs", "temp", "audio_cache"]
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
    print("✓ Directories created")


def main():
    """Main startup function"""
    print("=" * 50)
    print("🚀 J.A.R.V.I.S. Backend Setup")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Check if in correct directory
    if not Path("requirements.txt").exists():
        print("\n❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Check Ollama
    check_ollama()
    
    # Download Whisper model
    download_whisper_model()
    
    print("\n" + "=" * 50)
    print("✅ Setup complete!")
    print("=" * 50)
    print("\nTo start JARVIS:")
    print("  1. Make sure Ollama is running: ollama run llama2")
    print("  2. Start the server: python main.py")
    print("\nThe API will be available at: http://localhost:8000")
    print("WebSocket endpoint: ws://localhost:8000/ws")
    print("\nPress Enter to start the server now...")
    
    input()
    
    # Start the server
    print("\n🚀 Starting JARVIS Backend...")
    subprocess.call([sys.executable, "main.py"])


if __name__ == "__main__":
    main()
