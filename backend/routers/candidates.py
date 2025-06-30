from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging
from datetime import datetime
import bcrypt

from database import get_db
from models import Candidate, ChallengeSubmission, Challenge
from schemas import (
    Candidate as CandidateSchema,
    CandidateCreate,
    CandidateUpdate,
    ChallengeSubmission as ChallengeSubmissionSchema,
    ChallengeSubmissionCreate,
    ChallengeSubmissionWithDetails,
    CandidateListResponse,
    DashboardStats,
    SearchRequest,
    APIResponse
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Password hashing utility
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

@router.get("/candidates", response_model=List[CandidateSchema])
async def get_candidates(
    skip: int = Query(0, description="Number of candidates to skip"),
    limit: int = Query(100, description="Maximum number of candidates to return"),
    active_only: bool = Query(True, description="Return only active candidates"),
    db: AsyncSession = Depends(get_db)
):
    """Get all candidates with pagination"""
    try:
        query = select(Candidate)
        
        if active_only:
            query = query.where(Candidate.is_active == True)
        
        query = query.order_by(desc(Candidate.created_at)).offset(skip).limit(limit)
        
        result = await db.execute(query)
        candidates = result.scalars().all()
        
        return candidates
        
    except Exception as e:
        logger.error(f"Error fetching candidates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch candidates")

@router.get("/candidates/{candidate_id}", response_model=CandidateSchema)
async def get_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific candidate by ID"""
    try:
        query = select(Candidate).where(Candidate.id == candidate_id)
        result = await db.execute(query)
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return candidate
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching candidate {candidate_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch candidate")

@router.post("/candidates", response_model=CandidateSchema)
async def create_candidate(
    candidate_data: CandidateCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new candidate"""
    try:
        # Check if email already exists
        existing_query = select(Candidate).where(Candidate.email == candidate_data.email)
        existing_result = await db.execute(existing_query)
        existing_candidate = existing_result.scalar_one_or_none()
        
        if existing_candidate:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Prepare candidate data
        candidate_dict = candidate_data.dict()
        
        # Hash password if provided
        if candidate_dict.get('password'):
            candidate_dict['hashed_password'] = hash_password(candidate_dict['password'])
        
        # Remove password from dict to avoid passing it to the model
        candidate_dict.pop('password', None)
        
        candidate = Candidate(**candidate_dict)
        db.add(candidate)
        await db.commit()
        await db.refresh(candidate)
        
        logger.info(f"Created candidate: {candidate.id} - {candidate.email}")
        return candidate
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating candidate: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create candidate")

@router.put("/candidates/{candidate_id}", response_model=CandidateSchema)
async def update_candidate(
    candidate_id: int,
    candidate_update: CandidateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing candidate"""
    try:
        query = select(Candidate).where(Candidate.id == candidate_id)
        result = await db.execute(query)
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Check email uniqueness if email is being updated
        if candidate_update.email and candidate_update.email != candidate.email:
            email_query = select(Candidate).where(Candidate.email == candidate_update.email)
            email_result = await db.execute(email_query)
            if email_result.scalar_one_or_none():
                raise HTTPException(status_code=400, detail="Email already in use")
        
        # Update only provided fields
        update_data = candidate_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(candidate, field, value)
        
        await db.commit()
        await db.refresh(candidate)
        
        logger.info(f"Updated candidate: {candidate.id}")
        return candidate
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating candidate {candidate_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update candidate")

@router.delete("/candidates/{candidate_id}", response_model=APIResponse)
async def delete_candidate(
    candidate_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a candidate (mark as inactive)"""
    try:
        query = select(Candidate).where(Candidate.id == candidate_id)
        result = await db.execute(query)
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        candidate.is_active = False
        await db.commit()
        
        logger.info(f"Soft deleted candidate: {candidate.id}")
        return APIResponse(
            success=True,
            message=f"Candidate {candidate_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting candidate {candidate_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete candidate")

@router.get("/candidates/{candidate_id}/submissions", response_model=List[ChallengeSubmissionSchema])
async def get_candidate_submissions(
    candidate_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get all submissions for a specific candidate"""
    try:
        query = select(ChallengeSubmission).where(
            ChallengeSubmission.candidate_id == candidate_id
        ).order_by(desc(ChallengeSubmission.submitted_at))
        
        result = await db.execute(query)
        submissions = result.scalars().all()
        
        return submissions
        
    except Exception as e:
        logger.error(f"Error fetching submissions for candidate {candidate_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch candidate submissions")

@router.post("/submissions", response_model=ChallengeSubmissionSchema)
async def create_submission(
    submission_data: ChallengeSubmissionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new challenge submission"""
    try:
        # Verify candidate exists
        candidate_query = select(Candidate).where(Candidate.id == submission_data.candidate_id)
        candidate_result = await db.execute(candidate_query)
        candidate = candidate_result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Verify challenge exists
        challenge_query = select(Challenge).where(Challenge.id == submission_data.challenge_id)
        challenge_result = await db.execute(challenge_query)
        challenge = challenge_result.scalar_one_or_none()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Check if submission already exists for this candidate-challenge pair
        existing_query = select(ChallengeSubmission).where(
            and_(
                ChallengeSubmission.candidate_id == submission_data.candidate_id,
                ChallengeSubmission.challenge_id == submission_data.challenge_id
            )
        )
        existing_result = await db.execute(existing_query)
        existing_submission = existing_result.scalar_one_or_none()
        
        if existing_submission:
            raise HTTPException(
                status_code=400, 
                detail="Submission already exists for this candidate and challenge"
            )
        
        submission = ChallengeSubmission(**submission_data.dict())
        db.add(submission)
        await db.commit()
        await db.refresh(submission)
        
        logger.info(f"Created submission: {submission.id}")
        return submission
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating submission: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create submission")

@router.get("/submissions/{submission_id}", response_model=ChallengeSubmissionWithDetails)
async def get_submission(
    submission_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific submission with candidate and challenge details"""
    try:
        query = select(ChallengeSubmission).options(
            selectinload(ChallengeSubmission.candidate),
            selectinload(ChallengeSubmission.challenge)
        ).where(ChallengeSubmission.id == submission_id)
        
        result = await db.execute(query)
        submission = result.scalar_one_or_none()
        
        if not submission:
            raise HTTPException(status_code=404, detail="Submission not found")
        
        return submission
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching submission {submission_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch submission")

@router.post("/candidates/search", response_model=CandidateListResponse)
async def search_candidates(
    search_request: SearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Search and filter candidates with their submissions"""
    try:
        # Base query with joins
        query = select(ChallengeSubmission).options(
            selectinload(ChallengeSubmission.candidate),
            selectinload(ChallengeSubmission.challenge)
        )
        
        # Apply filters
        conditions = []
        
        if search_request.filters:
            filters = search_request.filters
            
            if filters.role:
                conditions.append(Challenge.role.ilike(f"%{filters.role}%"))
            
            if filters.min_score is not None:
                conditions.append(ChallengeSubmission.overall_score >= filters.min_score)
            
            if filters.max_score is not None:
                conditions.append(ChallengeSubmission.overall_score <= filters.max_score)
            
            if filters.date_from:
                conditions.append(ChallengeSubmission.submitted_at >= filters.date_from)
            
            if filters.date_to:
                conditions.append(ChallengeSubmission.submitted_at <= filters.date_to)
            
            if filters.status:
                conditions.append(ChallengeSubmission.submission_status == filters.status)
        
        # Text search
        if search_request.query:
            text_conditions = [
                Candidate.full_name.ilike(f"%{search_request.query}%"),
                Candidate.email.ilike(f"%{search_request.query}%"),
                Challenge.role.ilike(f"%{search_request.query}%")
            ]
            conditions.append(func.or_(*text_conditions))
        
        if conditions:
            query = query.join(Candidate).join(Challenge).where(and_(*conditions))
        
        # Count total results
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Apply sorting
        if search_request.sort_by == "submitted_at":
            if search_request.sort_order == "desc":
                query = query.order_by(desc(ChallengeSubmission.submitted_at))
            else:
                query = query.order_by(ChallengeSubmission.submitted_at)
        elif search_request.sort_by == "overall_score":
            if search_request.sort_order == "desc":
                query = query.order_by(desc(ChallengeSubmission.overall_score))
            else:
                query = query.order_by(ChallengeSubmission.overall_score)
        
        # Apply pagination
        offset = (search_request.page - 1) * search_request.per_page
        query = query.offset(offset).limit(search_request.per_page)
        
        result = await db.execute(query)
        submissions = result.scalars().all()
        
        total_pages = (total_count + search_request.per_page - 1) // search_request.per_page
        
        return CandidateListResponse(
            candidates=submissions,
            total_count=total_count,
            page=search_request.page,
            per_page=search_request.per_page,
            total_pages=total_pages
        )
        
    except Exception as e:
        logger.error(f"Error searching candidates: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search candidates")

@router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    """Get dashboard statistics"""
    try:
        # Total candidates
        total_candidates_query = select(func.count(Candidate.id)).where(Candidate.is_active == True)
        total_candidates_result = await db.execute(total_candidates_query)
        total_candidates = total_candidates_result.scalar()
        
        # Completed submissions
        completed_query = select(func.count(ChallengeSubmission.id)).where(
            ChallengeSubmission.submission_status == "completed"
        )
        completed_result = await db.execute(completed_query)
        completed_submissions = completed_result.scalar()
        
        # Pending submissions
        pending_query = select(func.count(ChallengeSubmission.id)).where(
            ChallengeSubmission.submission_status.in_(["pending", "processing"])
        )
        pending_result = await db.execute(pending_query)
        pending_submissions = pending_result.scalar()
        
        # Average score
        avg_score_query = select(func.avg(ChallengeSubmission.overall_score)).where(
            ChallengeSubmission.overall_score.isnot(None)
        )
        avg_score_result = await db.execute(avg_score_query)
        average_score = avg_score_result.scalar() or 0.0
        
        # Top performers
        top_performers_query = select(ChallengeSubmission).options(
            selectinload(ChallengeSubmission.candidate),
            selectinload(ChallengeSubmission.challenge)
        ).where(
            ChallengeSubmission.overall_score.isnot(None)
        ).order_by(desc(ChallengeSubmission.overall_score)).limit(5)
        
        top_performers_result = await db.execute(top_performers_query)
        top_performers = top_performers_result.scalars().all()
        
        return DashboardStats(
            total_candidates=total_candidates,
            completed_submissions=completed_submissions,
            pending_submissions=pending_submissions,
            average_score=round(average_score, 2),
            top_performers=top_performers
        )
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard statistics") 