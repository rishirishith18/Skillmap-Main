#!/usr/bin/env python3
"""
SkillSnap Backend Server Runner
Simple script to start the FastAPI server with appropriate settings
"""

import uvicorn
import os
import sys
from pathlib import Path

def main():
    """Run the FastAPI server"""
    # Ensure we're in the correct directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("💡 Run 'python setup.py' first to create configuration")
        sys.exit(1)
    
    # Check if database exists (for SQLite)
    if not Path("skillsnap.db").exists():
        print("⚠️  Database not found. It will be created on first request.")
    
    print("🚀 Starting SkillSnap Backend Server...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("⏹️  Press Ctrl+C to stop")
    
    # Start the server
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main() 