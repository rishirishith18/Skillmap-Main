#!/usr/bin/env python3
"""
Test script to verify all imports work correctly
"""

def test_imports():
    """Test all major imports"""
    print("🧪 Testing imports...")
    
    try:
        # Test config
        from config import settings, print_api_setup_instructions
        print("✅ Config imports successful")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        # Test database
        from database import get_db, async_session_maker, create_tables
        print("✅ Database imports successful")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        # Test models
        from models import Challenge, Candidate, ChallengeSubmission
        print("✅ Models imports successful")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    try:
        # Test schemas
        from schemas import ChallengeCreate, CandidateCreate, APIResponse
        print("✅ Schemas imports successful")
    except Exception as e:
        print(f"❌ Schemas import failed: {e}")
        return False
    
    try:
        # Test services
        from services.whisper_service import WhisperService
        from services.scoring_service import ScoringService  
        from services.voice_service import VoiceInteractionService
        print("✅ Services imports successful")
    except Exception as e:
        print(f"❌ Services import failed: {e}")
        return False
    
    try:
        # Test routers
        from routers import challenges, candidates, voice, scoring
        print("✅ Routers imports successful")
    except Exception as e:
        print(f"❌ Routers import failed: {e}")
        return False
    
    try:
        # Test main app
        from main import app
        print("✅ Main app import successful")
    except Exception as e:
        print(f"❌ Main app import failed: {e}")
        return False
    
    print("🎉 All imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ Backend is ready to run!")
        print("Run: python run.py")
    else:
        print("\n❌ Please fix import errors first") 