from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Optional
import logging

from database import get_db
from models import Challenge
from schemas import Challenge as ChallengeSchema, ChallengeCreate, ChallengeUpdate, APIResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/challenges", response_model=List[ChallengeSchema])
async def get_challenges(
    category: Optional[str] = Query(None, description="Filter by category"),
    difficulty: Optional[str] = Query(None, description="Filter by difficulty"),
    active_only: bool = Query(True, description="Return only active challenges"),
    db: AsyncSession = Depends(get_db)
):
    """Get all challenges with optional filtering"""
    try:
        query = select(Challenge)
        
        # Apply filters
        conditions = []
        if active_only:
            conditions.append(Challenge.is_active == True)
        if category:
            conditions.append(Challenge.category == category)
        if difficulty:
            conditions.append(Challenge.difficulty == difficulty)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(Challenge.created_at.desc())
        
        result = await db.execute(query)
        challenges = result.scalars().all()
        
        return challenges
        
    except Exception as e:
        logger.error(f"Error fetching challenges: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch challenges")

@router.get("/challenges/{challenge_id}", response_model=ChallengeSchema)
async def get_challenge(
    challenge_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific challenge by ID"""
    try:
        query = select(Challenge).where(Challenge.id == challenge_id)
        result = await db.execute(query)
        challenge = result.scalar_one_or_none()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        return challenge
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching challenge {challenge_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch challenge")

@router.post("/challenges", response_model=ChallengeSchema)
async def create_challenge(
    challenge_data: ChallengeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new challenge"""
    try:
        challenge = Challenge(**challenge_data.dict())
        db.add(challenge)
        await db.commit()
        await db.refresh(challenge)
        
        logger.info(f"Created challenge: {challenge.id} - {challenge.role}")
        return challenge
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating challenge: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create challenge")

@router.put("/challenges/{challenge_id}", response_model=ChallengeSchema)
async def update_challenge(
    challenge_id: int,
    challenge_update: ChallengeUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an existing challenge"""
    try:
        query = select(Challenge).where(Challenge.id == challenge_id)
        result = await db.execute(query)
        challenge = result.scalar_one_or_none()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        # Update only provided fields
        update_data = challenge_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(challenge, field, value)
        
        await db.commit()
        await db.refresh(challenge)
        
        logger.info(f"Updated challenge: {challenge.id}")
        return challenge
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating challenge {challenge_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update challenge")

@router.delete("/challenges/{challenge_id}", response_model=APIResponse)
async def delete_challenge(
    challenge_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a challenge (mark as inactive)"""
    try:
        query = select(Challenge).where(Challenge.id == challenge_id)
        result = await db.execute(query)
        challenge = result.scalar_one_or_none()
        
        if not challenge:
            raise HTTPException(status_code=404, detail="Challenge not found")
        
        challenge.is_active = False
        await db.commit()
        
        logger.info(f"Soft deleted challenge: {challenge.id}")
        return APIResponse(
            success=True,
            message=f"Challenge {challenge_id} deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting challenge {challenge_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete challenge")

@router.get("/challenges/categories/list")
async def get_challenge_categories(db: AsyncSession = Depends(get_db)):
    """Get list of all challenge categories"""
    try:
        query = select(Challenge.category).distinct().where(
            and_(Challenge.category.isnot(None), Challenge.is_active == True)
        )
        result = await db.execute(query)
        categories = [row[0] for row in result.fetchall()]
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error fetching categories: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

@router.get("/challenges/stats/summary")
async def get_challenges_stats(db: AsyncSession = Depends(get_db)):
    """Get challenge statistics"""
    try:
        # Total challenges
        total_query = select(Challenge).where(Challenge.is_active == True)
        total_result = await db.execute(total_query)
        total_challenges = len(total_result.scalars().all())
        
        # Challenges by difficulty
        easy_query = select(Challenge).where(
            and_(Challenge.difficulty == "Easy", Challenge.is_active == True)
        )
        easy_result = await db.execute(easy_query)
        easy_count = len(easy_result.scalars().all())
        
        medium_query = select(Challenge).where(
            and_(Challenge.difficulty == "Medium", Challenge.is_active == True)
        )
        medium_result = await db.execute(medium_query)
        medium_count = len(medium_result.scalars().all())
        
        hard_query = select(Challenge).where(
            and_(Challenge.difficulty == "Hard", Challenge.is_active == True)
        )
        hard_result = await db.execute(hard_query)
        hard_count = len(hard_result.scalars().all())
        
        # Challenges by category
        category_query = select(Challenge.category).where(Challenge.is_active == True)
        category_result = await db.execute(category_query)
        categories = [row[0] for row in category_result.fetchall() if row[0]]
        category_counts = {cat: categories.count(cat) for cat in set(categories)}
        
        return {
            "total_challenges": total_challenges,
            "by_difficulty": {
                "easy": easy_count,
                "medium": medium_count,
                "hard": hard_count
            },
            "by_category": category_counts
        }
        
    except Exception as e:
        logger.error(f"Error fetching challenge stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch challenge statistics") 