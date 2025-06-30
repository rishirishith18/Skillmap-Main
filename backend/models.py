from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Challenge(Base):
    """Voice challenge model"""
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    role = Column(String(100), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    duration = Column(Integer, nullable=False)  # in seconds
    difficulty = Column(String(20), nullable=False)  # Easy, Medium, Hard
    icon = Column(String(10), nullable=True)
    category = Column(String(50), nullable=True)  # Technical, Non-Technical, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    submissions = relationship("ChallengeSubmission", back_populates="challenge")

class Candidate(Base):
    """Candidate model"""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    role_interest = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=True)  # Optional for backward compatibility
    
    # Profile information
    experience_years = Column(Integer, nullable=True)
    current_role = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    
    # Relationships
    submissions = relationship("ChallengeSubmission", back_populates="candidate")

class ChallengeSubmission(Base):
    """Challenge submission model"""
    __tablename__ = "challenge_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    
    # Audio file information
    audio_file_path = Column(String(500), nullable=True)
    audio_duration = Column(Float, nullable=True)  # actual recording duration
    audio_format = Column(String(10), nullable=True)
    audio_size = Column(Integer, nullable=True)  # file size in bytes
    
    # Transcription
    transcription = Column(Text, nullable=True)
    transcription_confidence = Column(Float, nullable=True)
    
    # AI Scoring
    overall_score = Column(Float, nullable=True)
    fluency_score = Column(Float, nullable=True)
    confidence_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    clarity_score = Column(Float, nullable=True)
    tone_score = Column(Float, nullable=True)
    
    # Detailed analysis
    ai_analysis = Column(JSON, nullable=True)  # Store detailed AI analysis
    linguistic_features = Column(JSON, nullable=True)  # spaCy analysis results
    
    # Metadata
    submission_status = Column(String(20), default="pending")  # pending, processing, completed, failed
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="submissions")
    challenge = relationship("Challenge", back_populates="submissions")

class Recruiter(Base):
    """Recruiter/HR user model"""
    __tablename__ = "recruiters"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    company = Column(String(100), nullable=True)
    role = Column(String(100), nullable=True)
    
    # Authentication
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

class VoiceAnalytics(Base):
    """Voice analytics and metrics"""
    __tablename__ = "voice_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("challenge_submissions.id"), nullable=False)
    
    # Voice characteristics
    speaking_rate = Column(Float, nullable=True)  # words per minute
    pause_frequency = Column(Float, nullable=True)
    volume_variation = Column(Float, nullable=True)
    pitch_variation = Column(Float, nullable=True)
    
    # Speech patterns
    filler_words_count = Column(Integer, default=0)
    word_count = Column(Integer, nullable=True)
    unique_words_count = Column(Integer, nullable=True)
    sentence_count = Column(Integer, nullable=True)
    
    # Quality metrics
    audio_quality_score = Column(Float, nullable=True)
    background_noise_level = Column(Float, nullable=True)
    
    # Emotional analysis
    emotion_scores = Column(JSON, nullable=True)  # happiness, confidence, stress, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class APIUsage(Base):
    """Track API usage for monitoring and billing"""
    __tablename__ = "api_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(50), nullable=False)  # openai, google, omnidimension
    endpoint = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=True)
    cost_estimate = Column(Float, nullable=True)
    response_time = Column(Float, nullable=True)  # in seconds
    success = Column(Boolean, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Request metadata
    request_id = Column(String(100), nullable=True)
    user_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 