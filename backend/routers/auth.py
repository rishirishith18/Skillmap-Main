from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
import bcrypt
import jwt
import logging

from database import get_db
from models import Recruiter, Candidate
from config import settings
from schemas import CandidateLogin, CandidateAuthResponse

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Pydantic models
class RecruiterRegister(BaseModel):
    full_name: str
    email: EmailStr
    company: Optional[str] = None
    role: Optional[str] = None
    password: str

class RecruiterLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class RecruiterProfile(BaseModel):
    id: int
    full_name: str
    email: str
    company: Optional[str]
    role: Optional[str]
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

# Password hashing utilities
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
):
    """Get current authenticated recruiter"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(credentials.credentials, settings.SECRET_KEY, algorithms=["HS256"])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    
    query = select(Recruiter).where(Recruiter.email == email)
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    return user

@router.post("/auth/register", response_model=TokenResponse)
async def register_recruiter(
    recruiter_data: RecruiterRegister,
    db: AsyncSession = Depends(get_db)
):
    """Register a new recruiter"""
    try:
        # Check if email already exists
        existing_query = select(Recruiter).where(Recruiter.email == recruiter_data.email)
        existing_result = await db.execute(existing_query)
        existing_recruiter = existing_result.scalar_one_or_none()
        
        if existing_recruiter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(recruiter_data.password)
        
        # Create recruiter
        recruiter = Recruiter(
            full_name=recruiter_data.full_name,
            email=recruiter_data.email,
            company=recruiter_data.company,
            role=recruiter_data.role,
            hashed_password=hashed_password,
            is_verified=True  # Auto-verify for now
        )
        
        db.add(recruiter)
        await db.commit()
        await db.refresh(recruiter)
        
        # Create access token
        access_token_expires = timedelta(hours=24)
        access_token = create_access_token(
            data={"sub": recruiter.email}, expires_delta=access_token_expires
        )
        
        logger.info(f"Registered new recruiter: {recruiter.email}")
        
        return TokenResponse(
            access_token=access_token,
            expires_in=86400,  # 24 hours
            user={
                "id": recruiter.id,
                "full_name": recruiter.full_name,
                "email": recruiter.email,
                "company": recruiter.company,
                "role": recruiter.role
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error registering recruiter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register recruiter"
        )

@router.post("/auth/login", response_model=TokenResponse)
async def login_recruiter(
    login_data: RecruiterLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login recruiter"""
    try:
        query = select(Recruiter).where(Recruiter.email == login_data.email)
        result = await db.execute(query)
        recruiter = result.scalar_one_or_none()
        
        if not recruiter or not verify_password(login_data.password, recruiter.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not recruiter.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Update last login
        recruiter.last_login = datetime.utcnow()
        await db.commit()
        
        # Create access token
        access_token_expires = timedelta(hours=24)
        access_token = create_access_token(
            data={"sub": recruiter.email}, expires_delta=access_token_expires
        )
        
        logger.info(f"Recruiter logged in: {recruiter.email}")
        
        return TokenResponse(
            access_token=access_token,
            expires_in=86400,  # 24 hours
            user={
                "id": recruiter.id,
                "full_name": recruiter.full_name,
                "email": recruiter.email,
                "company": recruiter.company,
                "role": recruiter.role
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in recruiter: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )

@router.get("/auth/profile", response_model=RecruiterProfile)
async def get_profile(
    current_user: Recruiter = Depends(get_current_user)
):
    """Get current recruiter profile"""
    return RecruiterProfile(
        id=current_user.id,
        full_name=current_user.full_name,
        email=current_user.email,
        company=current_user.company,
        role=current_user.role,
        is_verified=current_user.is_verified,
        created_at=current_user.created_at,
        last_login=current_user.last_login
    )

@router.post("/auth/logout")
async def logout():
    """Logout recruiter (client-side token removal)"""
    return {"message": "Successfully logged out"}

# Candidate Authentication Endpoints
@router.post("/auth/candidate/login", response_model=CandidateAuthResponse)
async def login_candidate(
    login_data: CandidateLogin,
    db: AsyncSession = Depends(get_db)
):
    """Login candidate with email and password"""
    try:
        query = select(Candidate).where(Candidate.email == login_data.email)
        result = await db.execute(query)
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if candidate has a password (for backward compatibility)
        if not candidate.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Please register with a password to login"
            )
        
        # Verify password
        if not verify_password(login_data.password, candidate.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not candidate.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        logger.info(f"Candidate logged in: {candidate.email}")
        
        return CandidateAuthResponse(
            id=candidate.id,
            full_name=candidate.full_name,
            email=candidate.email,
            role_interest=candidate.role_interest,
            phone=candidate.phone,
            message="Login successful"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in candidate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )

@router.get("/auth/candidate/{candidate_id}", response_model=CandidateAuthResponse)
async def get_candidate_profile(
    candidate_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get candidate profile by ID"""
    try:
        query = select(Candidate).where(Candidate.id == candidate_id)
        result = await db.execute(query)
        candidate = result.scalar_one_or_none()
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        return CandidateAuthResponse(
            id=candidate.id,
            full_name=candidate.full_name,
            email=candidate.email,
            role_interest=candidate.role_interest,
            phone=candidate.phone,
            message="Profile retrieved successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching candidate profile: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch candidate profile") 