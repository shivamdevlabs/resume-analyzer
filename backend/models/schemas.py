"""
models/schemas.py — Pydantic request and response models.
These define the exact JSON shapes the API sends and receives.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# ─────────────────────────────────────────────
#  Response Models
# ─────────────────────────────────────────────

class AnalyzeResponse(BaseModel):
    """
    Response body for POST /api/analyze.
    Must match the shape the React frontend expects.
    """
    success: bool = True
    analysis_id: str
    generated_resume: str
    ats_score: int = Field(ge=0, le=100)
    matched_keywords: List[str]
    total_keywords: int
    improvements: List[str]
    mock: bool = False


class HealthResponse(BaseModel):
    """Response body for GET /api/health."""
    status: str = "ok"
    version: str = "1.0.0"
    database: str          # "connected" | "disconnected"
    ai_service: str        # "configured" | "not configured"


class DownloadResponse(BaseModel):
    """Metadata returned before streaming a PDF (not used directly; PDF is streamed)."""
    analysis_id: str
    filename: str


class ErrorResponse(BaseModel):
    """Standard error envelope."""
    success: bool = False
    detail: str


# ─────────────────────────────────────────────
#  Database Document Model
# ─────────────────────────────────────────────

class AnalysisDocument(BaseModel):
    """Shape of a document stored in MongoDB analyses collection."""
    analysis_id: str
    original_resume: str
    job_description: str
    generated_resume: str
    ats_score: int
    matched_keywords: List[str]
    total_keywords: int
    improvements: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # PDF bytes stored as binary in MongoDB (excluded from normal JSON output)
    pdf_bytes: Optional[bytes] = None

    model_config = {"arbitrary_types_allowed": True}
