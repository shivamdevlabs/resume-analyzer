"""
services/parser.py — Resume file parser.
Extracts plain text from PDF, DOCX, or plain-text (.txt) uploads.
"""

import io
import logging
from fastapi import UploadFile, HTTPException
from utils.helpers import clean_text

logger = logging.getLogger(__name__)

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB = 5


async def parse_resume_file(file: UploadFile) -> str:
    """
    Read an uploaded resume file and return its plain text content.

    Args:
        file: FastAPI UploadFile (PDF, DOCX, or TXT)

    Returns:
        Cleaned plain-text content of the resume.

    Raises:
        HTTPException 400 if file type is unsupported or file is too large.
    """
    filename = file.filename or ""
    extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension}'. Please upload PDF, DOCX, or TXT."
        )

    # Read file bytes
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({size_mb:.1f} MB). Maximum size is {MAX_FILE_SIZE_MB} MB."
        )

    logger.info("Parsing resume file: %s (%.1f KB)", filename, len(contents) / 1024)

    if extension == ".pdf":
        text = _parse_pdf(contents)
    elif extension == ".docx":
        text = _parse_docx(contents)
    else:
        text = _parse_txt(contents)

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail="Could not extract text from the uploaded file. Please check the file is not empty or image-based."
        )

    return clean_text(text)


def _parse_pdf(content: bytes) -> str:
    """Extract text from a PDF file using pypdf."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(content))
        pages_text = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                pages_text.append(page_text)
        return "\n\n".join(pages_text)
    except Exception as e:
        logger.error("PDF parsing error: %s", e)
        raise HTTPException(status_code=422, detail=f"Failed to read PDF: {e}")


def _parse_docx(content: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(content))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        logger.error("DOCX parsing error: %s", e)
        raise HTTPException(status_code=422, detail=f"Failed to read DOCX: {e}")


def _parse_txt(content: bytes) -> str:
    """Decode plain text from bytes, trying UTF-8 then latin-1."""
    for encoding in ("utf-8", "latin-1", "cp1252"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise HTTPException(status_code=422, detail="Could not decode text file. Please ensure it is UTF-8 encoded.")
