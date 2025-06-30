from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging
from typing import Optional

from database import get_db
from models import ChallengeSubmission, Challenge
from services.scoring_service import ScoringService
from schemas import (
    ScoringRequest,
    ScoringResponse,
    APIResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize scoring service
scoring_service = ScoringService()

@router.post("/scoring/score-text", response_model=ScoringResponse)
async def score_text_response(
    scoring_request: ScoringRequest
):
    """Score a text response directly (for testing purposes)"""
    try:
        response = await scoring_service.score_submission(
            transcription=scoring_request.transcription,
            challenge_prompt=scoring_request.challenge_prompt,
            audio_duration=scoring_request.audio_duration,
            challenge_role=scoring_request.challenge_role
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error scoring text response: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to score response")

@router.post("/scoring/rescore/{submission_id}", response_model=APIResponse)
async def rescore_submission(
    submission_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Re-score an existing submission"""
    try:
        # Get submission
        query = select(ChallengeSubmission).where(ChallengeSubmission.id == submission_id)
        result = await db.execute(query)
        submission = result.scalar_one_or_none()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        if not submission.transcription:
            raise HTTPException(status_code=400, detail="No transcription available for scoring")
        
        # Add rescoring task to background
        background_tasks.add_task(rescore_submission_task, submission_id)
        
        return APIResponse(
            success=True,
            message="Re-scoring started in background"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating re-scoring: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to initiate re-scoring")

async def rescore_submission_task(submission_id: int):
    """Background task to re-score a submission"""
    try:
        from database import async_session_maker
        
        async with async_session_maker() as db:
            # Get submission and challenge
            submission_query = select(ChallengeSubmission).where(ChallengeSubmission.id == submission_id)
            submission_result = await db.execute(submission_query)
            submission = submission_result.scalar_one_or_none()
            
            if not submission:
                logger.error(f"Submission {submission_id} not found during re-scoring")
                return
            
            challenge_query = select(Challenge).where(Challenge.id == submission.challenge_id)
            challenge_result = await db.execute(challenge_query)
            challenge = challenge_result.scalar_one_or_none()
            
            if not challenge:
                logger.error(f"Challenge not found for submission {submission_id}")
                return
            
            # Re-score the submission
            scoring_response = await scoring_service.score_submission(
                transcription=submission.transcription,
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
            
            # Update detailed analysis
            submission.ai_analysis = scoring_response.ai_analysis.dict()
            submission.linguistic_features = scoring_response.linguistic_features.dict()
            
            await db.commit()
            
            logger.info(f"Successfully re-scored submission {submission_id}")
            
    except Exception as e:
        logger.error(f"Error re-scoring submission {submission_id}: {str(e)}")

@router.get("/scoring/submission/{submission_id}/analysis")
async def get_submission_analysis(
    submission_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analysis for a submission"""
    try:
        query = select(ChallengeSubmission).where(ChallengeSubmission.id == submission_id)
        result = await db.execute(query)
        submission = result.scalar_one_or_none()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        analysis_data = {
            "submission_id": submission_id,
            "transcription": submission.transcription,
            "transcription_confidence": submission.transcription_confidence,
            "scores": {
                "overall_score": submission.overall_score,
                "fluency_score": submission.fluency_score,
                "confidence_score": submission.confidence_score,
                "relevance_score": submission.relevance_score,
                "clarity_score": submission.clarity_score,
                "tone_score": submission.tone_score
            },
            "ai_analysis": submission.ai_analysis,
            "linguistic_features": submission.linguistic_features,
            "audio_info": {
                "duration": submission.audio_duration,
                "format": submission.audio_format,
                "size": submission.audio_size
            },
            "processing_info": {
                "status": submission.submission_status,
                "submitted_at": submission.submitted_at,
                "processed_at": submission.processed_at
            }
        }
        
        return APIResponse(
            success=True,
            message="Analysis retrieved successfully",
            data=analysis_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting submission analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get submission analysis")

@router.get("/scoring/analytics/performance")
async def get_scoring_analytics(
    role_filter: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get scoring analytics and performance metrics"""
    try:
        from sqlalchemy import func, and_
        
        # Base query
        base_query = select(ChallengeSubmission).where(
            ChallengeSubmission.overall_score.isnot(None)
        )
        
        if role_filter:
            base_query = base_query.join(Challenge).where(
                Challenge.role.ilike(f"%{role_filter}%")
            )
        
        # Overall statistics
        stats_query = select(
            func.count(ChallengeSubmission.id).label('total_submissions'),
            func.avg(ChallengeSubmission.overall_score).label('avg_overall_score'),
            func.avg(ChallengeSubmission.fluency_score).label('avg_fluency_score'),
            func.avg(ChallengeSubmission.confidence_score).label('avg_confidence_score'),
            func.avg(ChallengeSubmission.relevance_score).label('avg_relevance_score'),
            func.avg(ChallengeSubmission.clarity_score).label('avg_clarity_score'),
            func.avg(ChallengeSubmission.tone_score).label('avg_tone_score'),
            func.min(ChallengeSubmission.overall_score).label('min_score'),
            func.max(ChallengeSubmission.overall_score).label('max_score')
        ).where(ChallengeSubmission.overall_score.isnot(None))
        
        if role_filter:
            stats_query = stats_query.join(Challenge).where(
                Challenge.role.ilike(f"%{role_filter}%")
            )
        
        stats_result = await db.execute(stats_query)
        stats = stats_result.first()
        
        # Score distribution (buckets)
        score_buckets = {
            "0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0
        }
        
        scores_query = select(ChallengeSubmission.overall_score).where(
            ChallengeSubmission.overall_score.isnot(None)
        )
        if role_filter:
            scores_query = scores_query.join(Challenge).where(
                Challenge.role.ilike(f"%{role_filter}%")
            )
        
        scores_result = await db.execute(scores_query)
        scores = [row[0] for row in scores_result.fetchall()]
        
        for score in scores:
            if score <= 20:
                score_buckets["0-20"] += 1
            elif score <= 40:
                score_buckets["21-40"] += 1
            elif score <= 60:
                score_buckets["41-60"] += 1
            elif score <= 80:
                score_buckets["61-80"] += 1
            else:
                score_buckets["81-100"] += 1
        
        analytics_data = {
            "total_submissions": stats.total_submissions if stats else 0,
            "average_scores": {
                "overall": round(stats.avg_overall_score, 2) if stats and stats.avg_overall_score else 0,
                "fluency": round(stats.avg_fluency_score, 2) if stats and stats.avg_fluency_score else 0,
                "confidence": round(stats.avg_confidence_score, 2) if stats and stats.avg_confidence_score else 0,
                "relevance": round(stats.avg_relevance_score, 2) if stats and stats.avg_relevance_score else 0,
                "clarity": round(stats.avg_clarity_score, 2) if stats and stats.avg_clarity_score else 0,
                "tone": round(stats.avg_tone_score, 2) if stats and stats.avg_tone_score else 0
            },
            "score_range": {
                "min": stats.min_score if stats else 0,
                "max": stats.max_score if stats else 0
            },
            "score_distribution": score_buckets,
            "role_filter": role_filter
        }
        
        return APIResponse(
            success=True,
            message="Scoring analytics retrieved",
            data=analytics_data
        )
        
    except Exception as e:
        logger.error(f"Error getting scoring analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scoring analytics")

@router.get("/scoring/weights")
async def get_scoring_weights():
    """Get current scoring weights configuration"""
    try:
        from config import settings
        
        return APIResponse(
            success=True,
            message="Scoring weights retrieved",
            data={
                "weights": settings.SCORING_WEIGHTS,
                "description": {
                    "fluency": "Based on speaking rate, pauses, and filler words",
                    "confidence": "Based on linguistic patterns and certainty markers",
                    "relevance": "AI analysis of how well the response addresses the prompt",
                    "clarity": "Communication effectiveness and structure",
                    "tone": "Professional language and appropriateness"
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Error getting scoring weights: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scoring weights")

@router.get("/scoring/health-check")
async def scoring_health_check():
    """Check if scoring services are available"""
    try:
        # Test basic scoring functionality
        test_response = await scoring_service.score_submission(
            transcription="This is a test response for health check.",
            challenge_prompt="Please provide a brief introduction about yourself.",
            audio_duration=10.0,
            challenge_role="Test Role"
        )
        
        return APIResponse(
            success=True,
            message="Scoring service is healthy",
            data={
                "openai_available": True,
                "spacy_available": scoring_service.nlp is not None,
                "test_score": test_response.scores.overall_score
            }
        )
        
    except Exception as e:
        logger.error(f"Scoring health check failed: {str(e)}")
        return APIResponse(
            success=False,
            message="Scoring service health check failed",
            errors=[str(e)]
        ) 