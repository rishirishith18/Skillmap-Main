from pydantic_settings import BaseSettings
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "SkillSnap Voice Challenge API"
    VERSION: str = "1.0.0"
    
    # Database
    DATABASE_URL: str = "postgresql://skillsnap_user:skillsnap_password@localhost:5432/skillsnap"
    # For SQLite development: "sqlite:///./skillsnap.db"
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"
    OPENAI_WHISPER_MODEL: str = "whisper-1"
    
    # Google Speech-to-Text (Alternative to Whisper)
    GOOGLE_CLOUD_PROJECT_ID: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    # Omnidimension SDK (Voice Interactions)
    OMNIDIMENSION_API_KEY: Optional[str] = None
    OMNIDIMENSION_BASE_URL: str = "https://api.omnidimension.com"
    
    # Voice Processing
    MAX_AUDIO_FILE_SIZE: int = 25 * 1024 * 1024  # 25MB
    SUPPORTED_AUDIO_FORMATS: list = ["mp3", "wav", "m4a", "webm"]
    MAX_RECORDING_DURATION: int = 300  # 5 minutes in seconds
    
    # Scoring Configuration
    SCORING_WEIGHTS: dict = {
        "fluency": 0.25,
        "confidence": 0.20,
        "relevance": 0.25,
        "clarity": 0.20,
        "tone": 0.10
    }
    
    # Security
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    AUDIO_DIR: str = "./uploads/audio"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Create upload directories
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path(settings.AUDIO_DIR).mkdir(exist_ok=True)

# API Key Sources and Instructions
API_KEY_SOURCES = {
    "OpenAI": {
        "url": "https://platform.openai.com/api-keys",
        "free_tier": "Yes - $5 free credit for new accounts",
        "description": "For GPT-based scoring and Whisper speech-to-text",
        "setup": [
            "1. Sign up at https://platform.openai.com/",
            "2. Go to API Keys section",
            "3. Create new secret key",
            "4. Add to .env file: OPENAI_API_KEY=your_key_here"
        ]
    },
    "Google Cloud Speech": {
        "url": "https://cloud.google.com/speech-to-text",
        "free_tier": "Yes - 60 minutes free per month",
        "description": "Alternative to OpenAI Whisper for speech-to-text",
        "setup": [
            "1. Create Google Cloud account",
            "2. Enable Speech-to-Text API",
            "3. Create service account and download JSON key",
            "4. Set GOOGLE_APPLICATION_CREDENTIALS=path/to/key.json"
        ]
    },
    "Omnidimension": {
        "url": "https://omnidimension.com/developers",
        "free_tier": "Check their pricing page",
        "description": "For advanced voice interaction features",
        "setup": [
            "1. Sign up at Omnidimension developer portal",
            "2. Get API key from dashboard",
            "3. Add to .env: OMNIDIMENSION_API_KEY=your_key_here"
        ]
    }
}

def print_api_setup_instructions():
    """Print setup instructions for all API services"""
    print("\n🔑 API Key Setup Instructions")
    print("=" * 50)
    
    for service, info in API_KEY_SOURCES.items():
        print(f"\n📌 {service}")
        print(f"   URL: {info['url']}")
        print(f"   Free Tier: {info['free_tier']}")
        print(f"   Purpose: {info['description']}")
        print("   Setup Steps:")
        for step in info['setup']:
            print(f"     {step}")
    
    print(f"\n📄 Create a .env file in your backend directory with:")
    print("OPENAI_API_KEY=your_openai_key_here")
    print("GOOGLE_APPLICATION_CREDENTIALS=path/to/google-key.json")
    print("OMNIDIMENSION_API_KEY=your_omnidimension_key_here")
    print("SECRET_KEY=your_secret_key_here")

if __name__ == "__main__":
    print_api_setup_instructions() 