"""
utils/helpers.py — Shared utility functions used across services.
"""

import re
import uuid
import unicodedata


def generate_analysis_id() -> str:
    """Generate a unique analysis ID (short UUID4)."""
    return uuid.uuid4().hex[:16]


def clean_text(text: str) -> str:
    """
    Normalize and clean raw extracted text:
    - Normalize unicode (NFKD → ASCII where possible)
    - Collapse multiple blank lines into one
    - Strip leading/trailing whitespace per line
    - Remove non-printable characters
    """
    if not text:
        return ""

    # Normalize unicode
    text = unicodedata.normalize("NFKD", text)

    # Remove non-printable characters (keep newlines and tabs)
    text = re.sub(r"[^\x09\x0A\x0D\x20-\x7E\u00A0-\uFFFF]", "", text)

    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Strip each line
    lines = [line.rstrip() for line in text.split("\n")]

    # Collapse 3+ consecutive blank lines into 2
    cleaned_lines = []
    blank_count = 0
    for line in lines:
        if line.strip() == "":
            blank_count += 1
            if blank_count <= 2:
                cleaned_lines.append(line)
        else:
            blank_count = 0
            cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def truncate_text(text: str, max_chars: int = 8000) -> str:
    """Truncate text to max_chars to stay within AI token limits."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... truncated for AI processing ...]"


def extract_sections(text: str) -> dict:
    """
    Attempt to identify common resume sections by heading patterns.
    Returns a dict of { section_name: content }.
    """
    section_patterns = [
        r"(SUMMARY|PROFESSIONAL SUMMARY|OBJECTIVE|PROFILE)",
        r"(EXPERIENCE|WORK EXPERIENCE|EMPLOYMENT|EMPLOYMENT HISTORY)",
        r"(EDUCATION|ACADEMIC BACKGROUND)",
        r"(SKILLS|TECHNICAL SKILLS|CORE COMPETENCIES)",
        r"(CERTIFICATIONS|CERTIFICATES|LICENSES)",
        r"(PROJECTS|PERSONAL PROJECTS|KEY PROJECTS)",
        r"(AWARDS|ACHIEVEMENTS|HONORS)",
    ]

    sections = {}
    combined_pattern = "|".join(f"(?P<{re.sub(r'[^a-z]', '_', p.split('|')[0].lower())}>{p})" for p in section_patterns)

    # Simple split — find each header and grab text until next header
    header_re = re.compile(
        r"^(" + "|".join(p for p in section_patterns) + r")\s*$",
        re.IGNORECASE | re.MULTILINE
    )

    parts = header_re.split(text)
    current_section = "header"
    for part in parts:
        if part and header_re.match(part.strip()):
            current_section = part.strip().upper()
        else:
            sections[current_section] = part.strip()

    return sections
