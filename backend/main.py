from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import os
from datetime import datetime, timedelta
import json

from routers import challenges, candidates, voice, scoring, auth
from services.voice_service import VoiceInteractionService
from services.scoring_service import ScoringService
from services.whisper_service import WhisperService
from config import settings
from database import connect_db, disconnect_db

# Initialize FastAPI app
app = FastAPI(
    title="SkillSnap Voice Challenge API",
    description="AI-powered voice challenge platform for hiring",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Include routers
app.include_router(auth.router, prefix="/api/v1", tags=["authentication"])
app.include_router(challenges.router, prefix="/api/v1", tags=["challenges"])
app.include_router(candidates.router, prefix="/api/v1", tags=["candidates"])
app.include_router(voice.router, prefix="/api/v1", tags=["voice"])
app.include_router(scoring.router, prefix="/api/v1", tags=["scoring"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "SkillSnap Voice Challenge API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "active"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "whisper_api": "available",
            "openai_api": "available",
            "voice_service": "ready"
        }
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await connect_db()
    print("🚀 SkillSnap API started successfully!")
    print(f"📚 API Documentation: http://localhost:8000/docs")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await disconnect_db()
    print("👋 SkillSnap API shutdown complete")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 