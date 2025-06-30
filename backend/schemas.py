from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Authentication Schemas
class CandidateLogin(BaseModel):
    email: EmailStr
    password: str

class CandidateAuthResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role_interest: Optional[str]
    phone: Optional[str]
    message: str

class DifficultyLevel(str, Enum):
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"

class SubmissionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

# Challenge Schemas
class ChallengeBase(BaseModel):
    role: str
    prompt: str
    duration: int
    difficulty: DifficultyLevel
    icon: Optional[str] = None
    category: Optional[str] = None

class ChallengeCreate(ChallengeBase):
    pass

class ChallengeUpdate(BaseModel):
    role: Optional[str] = None
    prompt: Optional[str] = None
    duration: Optional[int] = None
    difficulty: Optional[DifficultyLevel] = None
    icon: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class Challenge(ChallengeBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

# Candidate Schemas
class CandidateBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role_interest: Optional[str] = None
    experience_years: Optional[int] = None
    current_role: Optional[str] = None
    location: Optional[str] = None

class CandidateCreate(CandidateBase):
    password: Optional[str] = None  # Optional for backward compatibility

# Authentication Schemas  
class CandidateLogin(BaseModel):
    email: EmailStr
    password: str

class CandidateAuthResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role_interest: Optional[str]
    phone: Optional[str]
    message: str

class CandidateUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    role_interest: Optional[str] = None
    experience_years: Optional[int] = None
    current_role: Optional[str] = None
    location: Optional[str] = None

class Candidate(CandidateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True

# Voice Scoring Schemas
class VoiceScores(BaseModel):
    overall_score: Optional[float] = None
    fluency_score: Optional[float] = None
    confidence_score: Optional[float] = None
    relevance_score: Optional[float] = None
    clarity_score: Optional[float] = None
    tone_score: Optional[float] = None

class LinguisticFeatures(BaseModel):
    word_count: Optional[int] = None
    unique_words_count: Optional[int] = None
    sentence_count: Optional[int] = None
    filler_words_count: Optional[int] = None
    speaking_rate: Optional[float] = None  # words per minute
    pause_frequency: Optional[float] = None

class AIAnalysis(BaseModel):
    key_points: List[str] = []
    strengths: List[str] = []
    areas_for_improvement: List[str] = []
    overall_feedback: Optional[str] = None
    technical_accuracy: Optional[float] = None
    communication_effectiveness: Optional[float] = None

# Challenge Submission Schemas
class ChallengeSubmissionBase(BaseModel):
    candidate_id: int
    challenge_id: int

class ChallengeSubmissionCreate(ChallengeSubmissionBase):
    pass

class AudioUploadResponse(BaseModel):
    submission_id: int
    file_path: str
    message: str

class ChallengeSubmission(ChallengeSubmissionBase):
    id: int
    audio_file_path: Optional[str] = None
    audio_duration: Optional[float] = None
    audio_format: Optional[str] = None
    audio_size: Optional[int] = None
    transcription: Optional[str] = None
    transcription_confidence: Optional[float] = None
    submission_status: SubmissionStatus
    submitted_at: datetime
    processed_at: Optional[datetime] = None
    
    # Scores
    overall_score: Optional[float] = None
    fluency_score: Optional[float] = None
    confidence_score: Optional[float] = None
    relevance_score: Optional[float] = None
    clarity_score: Optional[float] = None
    tone_score: Optional[float] = None
    
    # Analysis
    ai_analysis: Optional[Dict[str, Any]] = None
    linguistic_features: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class ChallengeSubmissionWithDetails(ChallengeSubmission):
    candidate: Candidate
    challenge: Challenge

# Voice Processing Schemas
class TranscriptionRequest(BaseModel):
    audio_file_path: str
    language: str = "en"

class TranscriptionResponse(BaseModel):
    transcription: str
    confidence: float
    processing_time: float
    word_count: int

class ScoringRequest(BaseModel):
    transcription: str
    challenge_prompt: str
    audio_duration: float
    challenge_role: str

class ScoringResponse(BaseModel):
    scores: VoiceScores
    linguistic_features: LinguisticFeatures
    ai_analysis: AIAnalysis
    processing_time: float

# Recruiter Dashboard Schemas
class CandidateListResponse(BaseModel):
    candidates: List[ChallengeSubmissionWithDetails]
    total_count: int
    page: int
    per_page: int
    total_pages: int

class DashboardStats(BaseModel):
    total_candidates: int
    completed_submissions: int
    pending_submissions: int
    average_score: float
    top_performers: List[ChallengeSubmissionWithDetails]

# Filter and Search Schemas
class CandidateFilters(BaseModel):
    role: Optional[str] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    status: Optional[SubmissionStatus] = None

class SearchRequest(BaseModel):
    query: Optional[str] = None
    filters: Optional[CandidateFilters] = None
    page: int = 1
    per_page: int = 20
    sort_by: str = "submitted_at"
    sort_order: str = "desc"

# API Response Schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    errors: Optional[List[str]] = None

class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None

# Webhook and Integration Schemas
class WebhookEvent(BaseModel):
    event_type: str
    timestamp: datetime
    data: Dict[str, Any]

class OmnidimensionWebhook(BaseModel):
    call_id: str
    phone_number: str
    recording_url: str
    call_duration: float
    transcript: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

# Export Schemas
class ExportRequest(BaseModel):
    format: str = "csv"  # csv, xlsx, json
    filters: Optional[CandidateFilters] = None
    include_audio_links: bool = False

class ExportResponse(BaseModel):
    download_url: str
    file_name: str
    expires_at: datetime 