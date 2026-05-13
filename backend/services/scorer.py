"""
services/scorer.py — ATS score calculation.

Calculates a 0–100 ATS compatibility score based on keyword matching,
section completeness, and resume length quality.
"""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)


def calculate_ats_score(
    generated_resume: str,
    jd_keywords: List[str],
    matched_before: List[str],
) -> Tuple[int, List[str]]:
    """
    Calculate ATS score for the generated resume.

    Scoring breakdown (total = 100):
      - Keyword match rate:      60 points
      - Section completeness:    25 points
      - Resume length quality:   10 points
      - Formatting quality:       5 points

    Args:
        generated_resume:  The AI-generated resume text.
        jd_keywords:       All keywords extracted from the JD.
        matched_before:    Keywords that were in the original resume.

    Returns:
        Tuple of (score_0_to_100, list_of_matched_keywords_in_generated)
    """
    if not generated_resume or not jd_keywords:
        return 50, []

    resume_lower = generated_resume.lower()
    total_keywords = len(jd_keywords)

    # ── 1. Keyword match score (60 pts) ──────────────────────
    matched_keywords = []
    for kw in jd_keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, resume_lower):
            matched_keywords.append(kw)

    match_rate = len(matched_keywords) / total_keywords if total_keywords > 0 else 0
    keyword_score = round(match_rate * 60)

    # ── 2. Section completeness (25 pts) ─────────────────────
    section_score = _score_sections(resume_lower)

    # ── 3. Resume length quality (10 pts) ────────────────────
    word_count = len(generated_resume.split())
    if 300 <= word_count <= 800:
        length_score = 10
    elif 200 <= word_count < 300 or 800 < word_count <= 1000:
        length_score = 7
    elif word_count < 200:
        length_score = 3
    else:
        length_score = 5

    # ── 4. Formatting quality (5 pts) ────────────────────────
    format_score = _score_formatting(generated_resume)

    # ── Total ─────────────────────────────────────────────────
    total = keyword_score + section_score + length_score + format_score
    # Clamp to 0–100 and ensure a reasonable floor if keywords matched
    total = max(min(total, 100), 0)
    if matched_keywords and total < 40:
        total = 40

    logger.info(
        "ATS Score: %d | keywords=%d/%d | sections=%d | length=%d | format=%d",
        total, len(matched_keywords), total_keywords, section_score, length_score, format_score,
    )

    return total, matched_keywords


def _score_sections(resume_lower: str) -> int:
    """Award points for presence of key resume sections (max 25)."""
    sections = {
        "summary":       (["summary", "objective", "profile", "about"], 5),
        "experience":    (["experience", "employment", "work history"], 8),
        "education":     (["education", "academic", "degree", "university", "college"], 5),
        "skills":        (["skills", "competencies", "technologies", "expertise"], 5),
        "achievements":  (["certifications", "awards", "projects", "publications"], 2),
    }
    score = 0
    for _, (keywords, points) in sections.items():
        if any(kw in resume_lower for kw in keywords):
            score += points
    return min(score, 25)


def _score_formatting(resume: str) -> int:
    """Award points for clean, ATS-parseable formatting (max 5)."""
    score = 0
    # Has consistent line structure
    lines = resume.split("\n")
    non_empty = [ln for ln in lines if ln.strip()]
    if len(non_empty) >= 10:
        score += 2
    # Uses bullet points
    if any(line.strip().startswith("•") or line.strip().startswith("-") for line in lines):
        score += 2
    # No suspicious characters (tables, boxes)
    if not re.search(r"[│├─┼┤╔╗╚╝║═]", resume):
        score += 1
    return score
