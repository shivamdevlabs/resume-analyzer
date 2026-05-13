"""
routers/analyze.py — POST /api/analyze endpoint.

Orchestrates the full pipeline:
  1. Parse uploaded file OR accept pasted text
  2. Extract ATS keywords from job description
  3. Call Gemini to generate optimized resume
  4. Calculate ATS score
  5. Generate PDF
  6. Save to MongoDB
  7. Return JSON response
"""

import logging
from fastapi import APIRouter, Form, File, UploadFile, HTTPException
from typing import Optional
from datetime import datetime

from models.schemas import AnalyzeResponse
from models import database
from services import parser, keyword_extractor, ai_service, scorer, pdf_generator
from utils.helpers import generate_analysis_id, clean_text

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze resume and generate ATS-optimized version",
    response_description="The optimized resume with ATS score and keyword analysis",
)
async def analyze_resume(
    job_description: str = Form(..., description="Full job description text"),
    resume_text: Optional[str] = Form(None, description="Pasted resume text"),
    resume_file: Optional[UploadFile] = File(None, description="Resume file (PDF/DOCX/TXT)"),
):
    """
    Core endpoint: accepts resume (text or file) + job description,
    returns an ATS-optimized resume with score and keyword analysis.
    """

    # ── Validate inputs ───────────────────────────────────────
    if not job_description or len(job_description.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Job description is too short. Please paste the full job description."
        )

    has_file = resume_file and resume_file.filename
    has_text = resume_text and resume_text.strip()

    if not has_file and not has_text:
        raise HTTPException(
            status_code=400,
            detail="Please provide a resume — either upload a file or paste the text."
        )

    logger.info("New analysis request | has_file=%s | jd_length=%d", bool(has_file), len(job_description))

    # ── Step 1: Parse resume ──────────────────────────────────
    if has_file:
        original_resume = await parser.parse_resume_file(resume_file)
        logger.info("Parsed uploaded file: %s", resume_file.filename)
    else:
        original_resume = clean_text(resume_text)

    if len(original_resume.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="Resume content is too short to analyze. Please provide your complete resume."
        )

    # ── Step 2: Extract keywords from JD ─────────────────────
    jd_keywords, total_keywords = keyword_extractor.extract_keywords(job_description)
    matched_before = keyword_extractor.get_matched_keywords(original_resume, jd_keywords)
    missing_keywords = keyword_extractor.get_missing_keywords(original_resume, jd_keywords)

    logger.info(
        "Keywords | total=%d | matched_before=%d | missing=%d",
        total_keywords, len(matched_before), len(missing_keywords)
    )

    # ── Step 3: AI resume generation ─────────────────────────
    try:
        generated_resume, improvements = await ai_service.generate_optimized_resume(
            original_resume=original_resume,
            job_description=job_description,
            jd_keywords=jd_keywords,
            missing_keywords=missing_keywords,
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    # ── Step 4: ATS scoring ───────────────────────────────────
    ats_score, matched_keywords = scorer.calculate_ats_score(
        generated_resume=generated_resume,
        jd_keywords=jd_keywords,
        matched_before=matched_before,
    )

    # ── Step 5: Generate PDF ──────────────────────────────────
    try:
        pdf_bytes = pdf_generator.generate_pdf(generated_resume)
    except Exception as e:
        logger.warning("PDF generation failed (non-fatal): %s", e)
        pdf_bytes = None

    # ── Step 6: Save to MongoDB ───────────────────────────────
    analysis_id = generate_analysis_id()
    try:
        collection = database.get_analyses_collection()
        doc = {
            "analysis_id": analysis_id,
            "original_resume": original_resume,
            "job_description": job_description,
            "generated_resume": generated_resume,
            "ats_score": ats_score,
            "matched_keywords": matched_keywords,
            "total_keywords": total_keywords,
            "improvements": improvements,
            "pdf_bytes": pdf_bytes,
            "created_at": datetime.utcnow(),
        }
        await collection.insert_one(doc)
        logger.info("Saved analysis %s to MongoDB", analysis_id)
    except Exception as e:
        # DB failure is non-fatal — we still return the result
        logger.warning("MongoDB save failed (non-fatal): %s", e)

    # ── Step 7: Return response ───────────────────────────────
    logger.info("Analysis complete | id=%s | score=%d", analysis_id, ats_score)

    return AnalyzeResponse(
        success=True,
        analysis_id=analysis_id,
        generated_resume=generated_resume,
        ats_score=ats_score,
        matched_keywords=matched_keywords,
        total_keywords=total_keywords,
        improvements=improvements,
        mock=False,
    )
