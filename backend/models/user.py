"""
models/user.py — Pydantic user models, password hashing, and JWT token management.
"""

import hashlib
import os
import base64
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
import jwt
from config import settings

# ──────────────────────────────────────────────────────────────────────
#  Password Hashing (Secure PBKDF2-HMAC-SHA256)
# ──────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Hash a password using PBKDF2-HMAC-SHA256."""
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        100000
    )
    # Format: pbkdf2_sha256$iterations$salt$hash
    salt_b64 = base64.b64encode(salt).decode("utf-8")
    key_b64 = base64.b64encode(key).decode("utf-8")
    return f"pbkdf2_sha256$100000${salt_b64}${key_b64}"


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        parts = hashed_password.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        iterations = int(parts[1])
        salt = base64.b64decode(parts[2])
        key = base64.b64decode(parts[3])
        
        # Calculate new key
        new_key = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations
        )
        return new_key == key
    except Exception:
        return False


# ──────────────────────────────────────────────────────────────────────
#  JWT Configuration & Operations
# ──────────────────────────────────────────────────────────────────────

JWT_SECRET = getattr(settings, "JWT_SECRET", "careercraft_super_secret_key_123456")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generate a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT access token and return its payload."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # Return none if expired or invalid
        return payload
    except jwt.PyJWTError:
        return None


# ──────────────────────────────────────────────────────────────────────
#  Pydantic Schemas
# ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    mobile_number: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=6, max_length=100)


class UserLogin(BaseModel):
    identifier: str = Field(..., description="Email, username, or mobile number")
    password: str


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    username: str
    mobile_number: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
