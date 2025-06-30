from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid
import aiofiles
from typing import Optional, List
import logging
from datetime import datetime

from database import get_db, async_session_maker
from models import ChallengeSubmission, Challenge, Candidate
from services.whisper_service import TranscriptionService
from services.scoring_service import ScoringService
from services.voice_service import VoiceInteractionService, VoiceQualityAnalyzer
from schemas import (
    AudioUploadResponse, 
    TranscriptionResponse, 
    ScoringResponse, 
    APIResponse,
    OmnidimensionWebhook
)
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
transcription_service = TranscriptionService()
scoring_service = ScoringService()
voice_service = VoiceInteractionService()

@router.post("/voice/upload/{submission_id}", response_model=AudioUploadResponse)
async def upload_audio(
    submission_id: int,
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload audio file for a challenge submission"""
    try:
        # Validate file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Check file size
        if audio_file.size > settings.MAX_AUDIO_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {settings.MAX_AUDIO_FILE_SIZE // (1024*1024)}MB"
            )
        
        # Get submission
        query = select(ChallengeSubmission).where(ChallengeSubmission.id == submission_id)
        result = await db.execute(query)
        submission = result.scalar_one_or_none()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        # Generate unique filename
        file_extension = os.path.splitext(audio_file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(settings.AUDIO_DIR, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await audio_file.read()
            await f.write(content)
        
        # Update submission record
        submission.audio_file_path = file_path
        submission.audio_format = file_extension[1:]  # Remove the dot
        submission.audio_size = audio_file.size
        submission.submission_status = "processing"
        
        await db.commit()
        
        # Process audio in background
        background_tasks.add_task(process_audio_submission, submission_id, file_path)
        
        logger.info(f"Audio uploaded for submission {submission_id}: {file_path}")
        
        return AudioUploadResponse(
            submission_id=submission_id,
            file_path=file_path,
            message="Audio uploaded successfully and processing started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading audio: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to upload audio file")

@router.post("/voice/upload", response_model=AudioUploadResponse)
async def upload_voice_challenge(
    background_tasks: BackgroundTasks,
    audio_file: UploadFile = File(...),
    candidate_id: int = Form(...),
    challenge_type: str = Form("general"),
    db: AsyncSession = Depends(get_db)
):
    """Upload voice challenge recording directly from candidate"""
    try:
        # Validate file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Check file size (default 10MB if not set)
        max_size = getattr(settings, 'MAX_AUDIO_FILE_SIZE', 10 * 1024 * 1024)
        if audio_file.size and audio_file.size > max_size:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {max_size // (1024*1024)}MB"
            )
        
        # Get candidate
        candidate_query = select(Candidate).where(Candidate.id == candidate_id)
        candidate_result = await db.execute(candidate_query)
        candidate = candidate_result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Find or create a default challenge for this role
        challenge_query = select(Challenge).where(
            Challenge.role == challenge_type
        ).limit(1)
        challenge_result = await db.execute(challenge_query)
        challenge = challenge_result.scalar_one_or_none()
        
        # If no specific challenge found, create a general one or use the first available
        if not challenge:
            general_challenge_query = select(Challenge).limit(1)
            general_result = await db.execute(general_challenge_query)
            challenge = general_result.scalar_one_or_none()
            
            if not challenge:
                # Create a default challenge if none exist
                challenge = Challenge(
                    title="General Voice Challenge",
                    description="General voice assessment challenge",
                    prompt="Tell me about yourself and your experience in this field.",
                    role=challenge_type,
                    duration_minutes=5,
                    difficulty_level="intermediate",
                    is_active=True
                )
                db.add(challenge)
                await db.commit()
                await db.refresh(challenge)
        
        # Create submission record
        submission = ChallengeSubmission(
            candidate_id=candidate_id,
            challenge_id=challenge.id,
            submission_status="uploading",
            submitted_at=datetime.utcnow()
        )
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        
        # Generate unique filename
        file_extension = os.path.splitext(audio_file.filename or "recording.webm")[1]
        if not file_extension:
            file_extension = ".webm"  # Default for web recordings
            
        unique_filename = f"voice_challenge_{candidate_id}_{submission.id}_{uuid.uuid4()}{file_extension}"
        
        # Ensure upload directory exists
        upload_dir = getattr(settings, 'AUDIO_DIR', 'backend/uploads')
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            content = await audio_file.read()
            await f.write(content)
        
        # Update submission record
        submission.audio_file_path = file_path
        submission.audio_format = file_extension[1:]  # Remove the dot
        submission.audio_size = audio_file.size or len(content)
        submission.submission_status = "processing"
        
        await db.commit()
        
        # Process audio in background
        background_tasks.add_task(process_audio_submission, submission.id, file_path)
        
        logger.info(f"Voice challenge uploaded for candidate {candidate_id}, submission {submission.id}: {file_path}")
        
        return AudioUploadResponse(
            submission_id=submission.id,
            file_path=file_path,
            message="Voice challenge uploaded successfully and processing started"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading voice challenge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload voice challenge: {str(e)}")

async def process_audio_submission(submission_id: int, file_path: str):
    """Background task to process audio submission"""
    try:
        # Get database session
        async with async_session_maker() as db:
            # Get submission with related data
            query = select(ChallengeSubmission).where(ChallengeSubmission.id == submission_id)
            result = await db.execute(query)
            submission = result.scalar_one_or_none()
            
            if not submission:
                logger.error(f"Submission {submission_id} not found during processing")
                return
            
            # Get challenge details
            challenge_query = select(Challenge).where(Challenge.id == submission.challenge_id)
            challenge_result = await db.execute(challenge_query)
            challenge = challenge_result.scalar_one_or_none()
            
            if not challenge:
                logger.error(f"Challenge not found for submission {submission_id}")
                return
            
            # 1. Analyze audio quality
            quality_analysis = VoiceQualityAnalyzer.analyze_audio_file(file_path)
            if quality_analysis.get("duration"):
                submission.audio_duration = quality_analysis["duration"]
            
            # 2. Transcribe audio
            transcription_response = await transcription_service.transcribe(file_path)
            submission.transcription = transcription_response.transcription
            submission.transcription_confidence = transcription_response.confidence
            
            # 3. Score the response
            if transcription_response.transcription:
                scoring_response = await scoring_service.score_submission(
                    transcription=transcription_response.transcription,
                    challenge_prompt=challenge.prompt,
                    audio_duration=submission.audio_duration or 0,
                    challenge_role=challenge.role
                )
                
                # Update scores
                submission.overall_score = scoring_response.scores.overall_score
                submission.fluency_score = scoring_response.scores.fluency_score
                submission.confidence_score = scoring_response.scores.confidence_score
                submission.relevance_score = scoring_response.scores.relevance_score
                submission.clarity_score = scoring_response.scores.clarity_score
                submission.tone_score = scoring_response.scores.tone_score
                
                # Store detailed analysis
                submission.ai_analysis = scoring_response.ai_analysis.dict()
                submission.linguistic_features = scoring_response.linguistic_features.dict()
            
            # Mark as completed
            submission.submission_status = "completed"
            submission.processed_at = datetime.utcnow()
            
            await db.commit()
            
            logger.info(f"Successfully processed submission {submission_id}")
            
    except Exception as e:
        logger.error(f"Error processing submission {submission_id}: {str(e)}")
        # Mark as failed
        try:
            async with async_session_maker() as db:
                query = select(ChallengeSubmission).where(ChallengeSubmission.id == submission_id)
                result = await db.execute(query)
                submission = result.scalar_one_or_none()
                if submission:
                    submission.submission_status = "failed"
                    await db.commit()
        except:
            pass

@router.post("/voice/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(
    audio_file: UploadFile = File(...),
    language: str = Form("en"),
    provider: Optional[str] = Form(None)
):
    """Transcribe audio file (standalone endpoint)"""
    try:
        # Validate file
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail="File must be an audio file")
        
        # Save temporary file
        temp_filename = f"temp_{uuid.uuid4()}{os.path.splitext(audio_file.filename)[1]}"
        temp_path = os.path.join(settings.AUDIO_DIR, temp_filename)
        
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await audio_file.read()
            await f.write(content)
        
        try:
            # Transcribe
            response = await transcription_service.transcribe(temp_path, language, provider)
            return response
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in transcription: {str(e)}")
        raise HTTPException(status_code=500, detail="Transcription failed")

@router.post("/voice/voice-challenge/initiate")
async def initiate_voice_challenge(
    candidate_id: int = Form(...),
    challenge_id: int = Form(...),
    phone_number: str = Form(...),
    candidate_name: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """Initiate a voice challenge (automated call or self-recording instructions)"""
    try:
        # Verify candidate and challenge exist
        candidate_query = select(Candidate).where(Candidate.id == candidate_id)
        candidate_result = await db.execute(candidate_query)
        candidate = candidate_result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        challenge_query = select(Challenge).where(Challenge.id == challenge_id)
        challenge_result = await db.execute(challenge_query)
        challenge = challenge_result.scalar_one_or_none()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Create voice challenge session
        session_data = await voice_service.create_voice_challenge(
            candidate_id=candidate_id,
            challenge_id=challenge_id,
            phone_number=phone_number,
            candidate_name=candidate_name
        )
        
        return APIResponse(
            success=True,
            message="Voice challenge initiated",
            data=session_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating voice challenge: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate voice challenge")

@router.post("/webhooks/omnidimension")
async def omnidimension_webhook(
    webhook_data: OmnidimensionWebhook,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Handle webhooks from Omnidimension voice service"""
    try:
        logger.info(f"Received Omnidimension webhook for call {webhook_data.call_id}")
        
        # Process webhook in background
        background_tasks.add_task(process_omnidimension_webhook, webhook_data.dict())
        
        return APIResponse(
            success=True,
            message="Webhook received and processing started"
        )
        
    except Exception as e:
        logger.error(f"Error processing Omnidimension webhook: {str(e)}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")

async def process_omnidimension_webhook(webhook_data: dict):
    """Background task to process Omnidimension webhook"""
    try:
        webhook = OmnidimensionWebhook(**webhook_data)
        
        # Process the voice response
        await voice_service.process_voice_response(
            session_id=webhook.call_id,
            webhook_data=webhook_data
        )
        
        logger.info(f"Processed Omnidimension webhook for call {webhook.call_id}")
        
    except Exception as e:
        logger.error(f"Error processing Omnidimension webhook: {str(e)}")

@router.get("/voice/analytics/{session_id}")
async def get_voice_analytics(session_id: str):
    """Get detailed voice analytics for a session"""
    try:
        analytics = await voice_service.get_voice_analytics(session_id)
        return APIResponse(
            success=True,
            message="Voice analytics retrieved",
            data=analytics
        )
        
    except Exception as e:
        logger.error(f"Error getting voice analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get voice analytics")

@router.get("/voice/submissions", response_model=List[dict])
async def get_voice_submissions(
    skip: int = 0,
    limit: int = 50,
    candidate_name: Optional[str] = None,
    challenge_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all voice submissions for recruiters to review"""
    try:
        # Build the query
        query = select(
            ChallengeSubmission,
            Candidate.first_name,
            Candidate.last_name,
            Candidate.email,
            Candidate.phone,
            Candidate.role_interest,
            Challenge.title.label('challenge_title'),
            Challenge.prompt.label('challenge_prompt')
        ).join(
            Candidate, ChallengeSubmission.candidate_id == Candidate.id
        ).join(
            Challenge, ChallengeSubmission.challenge_id == Challenge.id
        ).where(
            ChallengeSubmission.audio_file_path.isnot(None)  # Only submissions with audio
        )
        
        # Apply filters
        if candidate_name:
            name_filter = f"%{candidate_name}%"
            query = query.where(
                (Candidate.first_name.ilike(name_filter)) |
                (Candidate.last_name.ilike(name_filter))
            )
        
        if challenge_type:
            query = query.where(Candidate.role_interest == challenge_type)
            
        if status:
            query = query.where(ChallengeSubmission.submission_status == status)
        
        # Order by submission date (newest first)
        query = query.order_by(ChallengeSubmission.submitted_at.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        submissions_data = result.fetchall()
        
        # Format response
        submissions = []
        for row in submissions_data:
            submission = row[0]  # ChallengeSubmission object
            
            submissions.append({
                "submission_id": submission.id,
                "candidate_id": submission.candidate_id,
                "candidate_name": f"{row.first_name} {row.last_name}",
                "candidate_email": row.email,
                "candidate_phone": row.phone,
                "role_interest": row.role_interest,
                "challenge_title": row.challenge_title,
                "challenge_prompt": row.challenge_prompt,
                "submitted_at": submission.submitted_at.isoformat() if submission.submitted_at else None,
                "processed_at": submission.processed_at.isoformat() if submission.processed_at else None,
                "status": submission.submission_status,
                "audio_duration": submission.audio_duration,
                "transcription": submission.transcription,
                "overall_score": submission.overall_score,
                "fluency_score": submission.fluency_score,
                "confidence_score": submission.confidence_score,
                "relevance_score": submission.relevance_score,
                "clarity_score": submission.clarity_score,
                "tone_score": submission.tone_score,
                "has_audio": bool(submission.audio_file_path),
                "audio_url": f"/api/v1/voice/audio/{submission.id}" if submission.audio_file_path else None
            })
        
        return submissions
        
    except Exception as e:
        logger.error(f"Error getting voice submissions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get voice submissions")

@router.get("/voice/audio/{submission_id}")
async def get_audio_file(
    submission_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Serve audio file for a specific submission"""
    try:
        # Get submission
        query = select(ChallengeSubmission).where(ChallengeSubmission.id == submission_id)
        result = await db.execute(query)
        submission = result.scalar_one_or_none()
        
        if not submission or not submission.audio_file_path:
            raise HTTPException(status_code=404, detail="Audio file not found")
        
        # Check if file exists
        if not os.path.exists(submission.audio_file_path):
            raise HTTPException(status_code=404, detail="Audio file not found on disk")
        
        # Return file
        from fastapi.responses import FileResponse
        return FileResponse(
            submission.audio_file_path,
            media_type="audio/webm",
            filename=f"voice_submission_{submission_id}.webm"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving audio file: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to serve audio file")

@router.get("/voice/submission/{submission_id}/status")
async def get_submission_status(
    submission_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get the processing status of a submission"""
    try:
        query = select(ChallengeSubmission).where(ChallengeSubmission.id == submission_id)
        result = await db.execute(query)
        submission = result.scalar_one_or_none()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        return {
            "submission_id": submission_id,
            "status": submission.submission_status,
            "submitted_at": submission.submitted_at,
            "processed_at": submission.processed_at,
            "has_audio": bool(submission.audio_file_path),
            "has_transcription": bool(submission.transcription),
            "has_scores": bool(submission.overall_score)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get submission status") 