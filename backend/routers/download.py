"""
routers/download.py — GET /api/download/{analysis_id} endpoint.

Streams the PDF of a previously generated resume.
If the PDF wasn't stored in MongoDB, regenerates it on-the-fly from
the stored resume text — so download always works.
"""

import io
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from models import database
from services import pdf_generator

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/download/{analysis_id}",
    summary="Download the generated resume as a PDF",
    response_description="PDF file stream",
)
async def download_resume(analysis_id: str):
    """
    Retrieve and stream a previously generated resume PDF by its analysis ID.
    The analysis_id is returned in the POST /api/analyze response.
    """
    if not analysis_id or len(analysis_id) < 6:
        raise HTTPException(status_code=400, detail="Invalid analysis ID.")

    # Fetch record from MongoDB — get both pdf_bytes and generated_resume
    try:
        collection = database.get_analyses_collection()
        doc = await collection.find_one(
            {"analysis_id": analysis_id},
            {"pdf_bytes": 1, "generated_resume": 1, "analysis_id": 1, "_id": 0},
        )
    except Exception as e:
        logger.error("MongoDB fetch error for id=%s: %s", analysis_id, e)
        raise HTTPException(
            status_code=503,
            detail="Database unavailable. Please try again."
        )

    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"No analysis found with ID '{analysis_id}'. It may have expired.",
        )

    # Try stored PDF bytes first
    pdf_bytes = doc.get("pdf_bytes")

    # If no PDF was stored, regenerate from saved resume text
    if not pdf_bytes:
        resume_text = doc.get("generated_resume", "")
        if not resume_text:
            raise HTTPException(
                status_code=404,
                detail="Resume data not available. Please regenerate your resume.",
            )
        logger.info(
            "PDF not stored for %s — regenerating from resume text (%d chars)",
            analysis_id, len(resume_text),
        )
        try:
            pdf_bytes = pdf_generator.generate_pdf(resume_text)
        except Exception as e:
            logger.error("PDF regeneration failed for %s: %s", analysis_id, e)
            raise HTTPException(
                status_code=500,
                detail="PDF generation failed. Please try again.",
            )

    logger.info(
        "Serving PDF download | id=%s | size=%d bytes",
        analysis_id, len(pdf_bytes),
    )

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="ATS_Resume_{analysis_id[:8]}.pdf"',
            "Content-Length": str(len(pdf_bytes)),
            "Cache-Control": "no-cache",
        },
    )
