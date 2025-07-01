#!/usr/bin/env python3
"""Start GoldMiner v2 with Enhanced UI"""

import subprocess
import time
import os
import sys

def main():
    print("🚀 Starting GoldMiner 2.0 - Enhanced UI Version...")
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("❌ .env file not found! Please copy .env.example and add your OpenRouter API key")
        sys.exit(1)
    
    # Start FastAPI
    print("🔧 Starting FastAPI backend...")
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"  # Enable auto-reload for development
    ])
    
    # Wait for API to start
    time.sleep(3)
    
    # Start Streamlit with v2 UI
    print("🎨 Starting Enhanced Streamlit frontend...")
    ui_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", 
        "run", "app/ui/main.py",
        "--server.port", "8501",
        "--server.address", "0.0.0.0",
        "--theme.base", "light"
    ])
    
    print("\n✅ GoldMiner 2.0 is running!")
    print("📡 API: http://localhost:8000")
    print("🌐 UI: http://localhost:8501")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n🆕 New Features:")
    print("  • Real-time goldmining progress")
    print("  • Edit and delete ideas")
    print("  • Kanban board view")
    print("  • Advanced filtering and sorting")
    print("  • Export functionality")
    print("\nPress Ctrl+C to stop all services...")
    
    try:
        # Wait for keyboard interrupt
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        api_process.terminate()
        ui_process.terminate()
        api_process.wait()
        ui_process.wait()
        print("Goodbye!")

if __name__ == "__main__":
    main()