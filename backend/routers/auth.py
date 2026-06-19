"""
routers/auth.py — Authentication endpoints (register, login, me) and history retrieval.
"""

import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from models import database
from models.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from utils.helpers import generate_analysis_id

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


def _raise_db_unavailable():
    """Raise a clear 503 error when MongoDB is unreachable."""
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="Database is temporarily unavailable. Please check your MONGODB_URI configuration.",
    )


# ──────────────────────────────────────────────────────────────────────
#  Security Dependency
# ──────────────────────────────────────────────────────────────────────

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    FastAPI dependency to extract and verify the JWT access token from the
    Authorization header. Returns the user document if valid.
    """
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please log in to analyze and optimize your resume.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload["sub"]
    users_col = database.get_users_collection()
    user = await users_col.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found.",
        )
    return user


# Helper to convert MongoDB document to UserResponse
def map_user_to_response(user_doc: dict) -> UserResponse:
    return UserResponse(
        id=str(user_doc["_id"]),
        full_name=user_doc["full_name"],
        email=user_doc["email"],
        username=user_doc["username"],
        mobile_number=user_doc["mobile_number"],
        created_at=user_doc.get("created_at", datetime.utcnow()),
    )


# ──────────────────────────────────────────────────────────────────────
#  Endpoints
# ──────────────────────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(user_data: UserCreate):
    """
    Register a user. Automatically derives username from email (before @).
    Checks for duplicates by email, username, or mobile number.
    """
    users_col = database.get_users_collection()

    # Normalize email
    email_lower = user_data.email.lower().strip()
    
    # Derive username as part before @
    derived_username = email_lower.split("@")[0]
    
    # Check for existing user with same email, username, or mobile number
    try:
        existing_user = await users_col.find_one({
            "$or": [
                {"email": email_lower},
                {"username": derived_username},
                {"mobile_number": user_data.mobile_number}
            ]
        })
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error("MongoDB unreachable during registration: %s", e)
        _raise_db_unavailable()
    
    if existing_user:
        if existing_user.get("email") == email_lower:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already registered."
            )
        if existing_user.get("mobile_number") == user_data.mobile_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mobile number is already registered."
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or credentials already exist."
        )

    # Hash password and create record
    hashed = hash_password(user_data.password)
    user_id = generate_analysis_id() # Unique ID helper
    
    user_doc = {
        "_id": user_id,
        "full_name": user_data.full_name,
        "email": email_lower,
        "username": derived_username,
        "mobile_number": user_data.mobile_number,
        "password_hash": hashed,
        "created_at": datetime.utcnow(),
    }
    
    try:
        await users_col.insert_one(user_doc)
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error("MongoDB unreachable during user insert: %s", e)
        _raise_db_unavailable()

    logger.info("Registered new user: %s (username: %s)", email_lower, derived_username)
    
    # Create token
    access_token = create_access_token(data={"sub": email_lower})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=map_user_to_response(user_doc)
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate user and retrieve token",
)
async def login(credentials: UserLogin):
    """
    Log in a user. Matches identifier against email, derived username,
    or mobile number. Verifies hash-password.
    """
    users_col = database.get_users_collection()
    ident = credentials.identifier.strip()
    
    # Match against email, username, or mobile_number
    try:
        user_doc = await users_col.find_one({
            "$or": [
                {"email": ident.lower()},
                {"username": ident},
                {"mobile_number": ident}
            ]
        })
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error("MongoDB unreachable during login: %s", e)
        _raise_db_unavailable()
    
    if not user_doc or not verify_password(credentials.password, user_doc["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email/username/mobile number or password."
        )
        
    logger.info("User logged in successfully: %s", user_doc["email"])
    
    # Generate token
    access_token = create_access_token(data={"sub": user_doc["email"]})
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=map_user_to_response(user_doc)
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile info",
)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Returns the authenticated user details."""
    return map_user_to_response(current_user)


# ──────────────────────────────────────────────────────────────────────
#  History & Analysis Management
# ──────────────────────────────────────────────────────────────────────

class SavedAnalysisSummary(BaseModel):
    analysis_id: str
    job_description_snippet: str
    ats_score: int
    matched_keywords_count: int
    total_keywords_count: int
    created_at: datetime


@router.get(
    "/history",
    response_model=List[SavedAnalysisSummary],
    summary="Get past analyses for the authenticated user",
)
async def get_history(current_user: dict = Depends(get_current_user)):
    """
    Retrieve all resume analyses generated by this user.
    """
    analyses_col = database.get_analyses_collection()
    user_email = current_user["email"]
    
    # Find matching records
    cursor = analyses_col.find({"user_email": user_email}).sort("created_at", -1)
    results = []
    
    async for doc in cursor:
        # Generate snippet of job description
        jd = doc.get("job_description", "")
        jd_snippet = jd[:100] + ("..." if len(jd) > 100 else "")
        
        results.append(SavedAnalysisSummary(
            analysis_id=doc["analysis_id"],
            job_description_snippet=jd_snippet,
            ats_score=doc["ats_score"],
            matched_keywords_count=len(doc.get("matched_keywords", [])),
            total_keywords_count=doc.get("total_keywords", 0),
            created_at=doc.get("created_at", datetime.utcnow())
        ))
        
    return results
