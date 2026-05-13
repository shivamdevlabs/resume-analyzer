"""
services/ai_service.py -- Google Gemini API integration via REST.

Calls the Gemini REST API directly using httpx (no google-generativeai SDK).
Compatible with Python 3.14+ -- zero compiled C extensions.

Discovers available models DYNAMICALLY so we never hardcode a model name.

API References:
  GET  https://generativelanguage.googleapis.com/v1beta/models
  POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent
"""

import logging
from typing import List, Tuple, Optional

import httpx

from config import settings
from utils.helpers import truncate_text

logger = logging.getLogger(__name__)

_GEMINI_API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Cached model name discovered at first call
_cached_model: Optional[str] = None

# Preferred model priority -- first one found wins
_PREFERRED_MODELS = [
    "gemini-2.5-flash-preview-05-20",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-2.0-flash-lite",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-8b",
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
]


def is_configured() -> bool:
    """Check if the Gemini API key is available."""
    return bool(settings.GEMINI_API_KEY)


async def _discover_model() -> str:
    """
    Call the Gemini /models endpoint to discover which models are actually
    available for this API key, then pick the best one.

    This runs once and caches the result -- one extra HTTP call on the very
    first request, then instant for all subsequent requests.
    """
    global _cached_model
    if _cached_model:
        return _cached_model

    if not settings.GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Add it to backend/.env\n"
            "Get a free key at: https://aistudio.google.com/app/apikey"
        )

    logger.info("Discovering available Gemini models for this API key...")

    url = f"{_GEMINI_API_BASE}/models"
    params = {"key": settings.GEMINI_API_KEY}

    async with httpx.AsyncClient(timeout=20.0) as client:
        response = await client.get(url, params=params)

    if response.status_code == 400:
        raise RuntimeError(
            "Invalid Gemini API key (HTTP 400). "
            "Please create a new key at: https://aistudio.google.com/app/apikey "
            "and update backend/.env"
        )
    if response.status_code == 403:
        raise RuntimeError(
            "Gemini API key is not authorized (HTTP 403). "
            "Your key may be restricted or the Generative Language API is not enabled. "
            "Check: https://aistudio.google.com/app/apikey"
        )
    if response.status_code != 200:
        raise RuntimeError(
            f"Could not retrieve Gemini model list (HTTP {response.status_code}). "
            f"Response: {response.text[:300]}"
        )

    data = response.json()
    all_models = data.get("models", [])

    generative_models = []
    for m in all_models:
        short_name = m.get("name", "").replace("models/", "")
        methods = m.get("supportedGenerationMethods", [])
        if "generateContent" in methods:
            generative_models.append(short_name)

    logger.info(
        "Found %d models supporting generateContent: %s",
        len(generative_models),
        ", ".join(generative_models[:8]),
    )

    if not generative_models:
        raise RuntimeError(
            "Your Gemini API key has no models available for generateContent. "
            "Please create a new key at: https://aistudio.google.com/app/apikey"
        )

    for preferred in _PREFERRED_MODELS:
        if preferred in generative_models:
            _cached_model = preferred
            logger.info("Selected Gemini model: %s", _cached_model)
            return _cached_model

    _cached_model = generative_models[0]
    logger.info("Using first available Gemini model: %s", _cached_model)
    return _cached_model


async def _call_gemini_api(prompt: str) -> str:
    """
    Send a prompt to the Gemini REST API and return the generated text.

    Raises:
        RuntimeError: If the API call fails.
    """
    model_name = await _discover_model()

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.55,  # slightly higher for richer vocabulary
            "topP": 0.95,
            "topK": 64,
            "maxOutputTokens": 8192,
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ],
    }

    url = f"{_GEMINI_API_BASE}/models/{model_name}:generateContent"
    params = {"key": settings.GEMINI_API_KEY}
    headers = {"Content-Type": "application/json"}

    logger.info("Calling Gemini model: %s", model_name)

    async with httpx.AsyncClient(timeout=90.0) as client:
        response = await client.post(url, json=payload, params=params, headers=headers)

    if response.status_code != 200:
        global _cached_model
        _cached_model = None
        try:
            error_detail = (
                response.json().get("error", {}).get("message", response.text)
            )
        except Exception:
            error_detail = response.text
        raise RuntimeError(
            f"Gemini API error (HTTP {response.status_code}): {error_detail}"
        )

    try:
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError(
                "Gemini returned no output. Content may have been blocked by safety filters."
            )
        return candidates[0]["content"]["parts"][0]["text"].strip()
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Unexpected Gemini response format: {e}") from e


async def generate_optimized_resume(
    original_resume: str,
    job_description: str,
    jd_keywords: List[str],
    missing_keywords: List[str],
) -> Tuple[str, List[str]]:
    """
    Call Gemini to generate a high-quality, ATS-optimized resume.

    Returns:
        Tuple of (optimized_resume_text, list_of_improvements_made)
    """
    resume_truncated = truncate_text(original_resume, max_chars=12000)
    jd_truncated = truncate_text(job_description, max_chars=5000)
    keywords_str = ", ".join(jd_keywords[:40]) if jd_keywords else "None"
    missing_str = ", ".join(missing_keywords[:20]) if missing_keywords else "None"

    prompt = (
        "You are a world-class ATS resume writer and career coach.\n\n"
        "Your task: Completely rewrite the candidate's resume to be:\n"
        "  1. 100% tailored to the specific job description provided\n"
        "  2. Fully ATS-optimized (keyword-rich, standard sections, parseable)\n"
        "  3. Highly compelling to human recruiters (strong action verbs, quantified results)\n"
        "  4. ZERO repetition -- every bullet point must be completely unique\n"
        "  5. ONE PAGE ONLY -- the entire resume MUST fit on a single page, so be concise\n\n"
        "## ORIGINAL RESUME:\n"
        f"{resume_truncated}\n\n"
        "## TARGET JOB DESCRIPTION:\n"
        f"{jd_truncated}\n\n"
        "## ATS KEYWORDS TO WEAVE IN NATURALLY:\n"
        f"{keywords_str}\n\n"
        "## MISSING KEYWORDS TO ADD:\n"
        f"{missing_str}\n\n"
        "## STRICT WRITING RULES:\n"
        "1. ACCURACY: Never invent companies, universities, dates, or degrees. Only rewrite what exists.\n"
        "2. NO REPETITION: Never start two bullet points with the same word. Never repeat the same\n"
        "   phrase or idea across any two bullets. Every bullet must describe a DIFFERENT achievement.\n"
        "3. STRONG ACTION VERBS: Start each bullet with a powerful, VARIED action verb.\n"
        "   Use words like: Engineered, Architected, Spearheaded, Optimized, Streamlined, Delivered,\n"
        "   Reduced, Increased, Built, Designed, Deployed, Automated, Improved, Collaborated, Led,\n"
        "   Implemented, Integrated, Migrated, Launched, Maintained, Resolved, Analyzed, Established.\n"
        "   NEVER repeat the same verb twice in the same job entry.\n"
        "4. STAR FORMAT: Each bullet = Action verb + What you did + Technology used + Measurable result\n"
        "5. KEYWORDS: Integrate ATS keywords naturally in summary, skills, and bullets.\n"
        "6. NO FILLER: Never use 'worked on', 'helped with', 'responsible for', 'involved in'.\n"
        "7. SKILLS: Organize into clear categories (Web, Backend, Database, Tools, Languages, OS).\n"
        "8. ONE PAGE: Keep EVERYTHING concise. Career objective = 2 sentences max. "
        "Each job entry = MAX 3 bullets (2 bullets preferred for older/shorter roles). "
        "Each bullet = max 20 words. Skills categories = max 5 items each.\n\n"
        "## REQUIRED OUTPUT FORMAT (plain text ONLY -- no markdown, no asterisks, no bold):\n\n"
        "[FULL NAME IN CAPS]\n"
        "[Phone] | [Email] | [City, Country] | [LinkedIn profile] | [GitHub profile]\n\n"
        "CAREER OBJECTIVE\n"
        "[2-3 sentences tailored to the JD, using key job description language and skills]\n\n"
        "EDUCATION\n"
        "[Degree Name], [University Name], [City]  [Month Year]\n\n"
        "PROFESSIONAL EXPERIENCE\n\n"
        "[Job Title], [Company Name], [City]  [Month Year] - [Month Year]\n"
        "  * [Unique bullet 1 -- max 20 words, STAR format, unique action verb]\n"
        "  * [Unique bullet 2 -- max 20 words, STAR format, unique action verb]\n"
        "  * [Unique bullet 3 -- max 20 words, STAR format, unique action verb]\n\n"
        "[Next Job Title], [Company Name], [City]  [Month Year] - [Month Year]\n"
        "  * [Unique bullet -- max 20 words, different from ALL bullets above]\n"
        "  * [Unique bullet -- max 20 words, different from ALL bullets above]\n\n"
        "TECHNICAL SKILLS\n"
        "  * Web: [comma-separated technologies]\n"
        "  * Backend: [comma-separated technologies]\n"
        "  * Databases: [comma-separated technologies]\n"
        "  * Tools: [comma-separated tools]\n"
        "  * Languages: [comma-separated languages]\n\n"
        "PROJECTS\n"
        "[Project Name]  [Year]\n"
        "  * [What it does, tech stack, scale/impact]\n\n"
        "INTERPERSONAL SKILLS\n"
        "  * [skill 1]\n"
        "  * [skill 2]\n"
        "  * [skill 3]\n\n"
        "---IMPROVEMENTS---\n"
        "- [Specific improvement 1]\n"
        "- [Specific improvement 2]\n"
        "- [Specific improvement 3]\n"
        "- [Specific improvement 4]\n"
        "- [Specific improvement 5]\n"
    )

    logger.info("Requesting Gemini resume optimization...")

    try:
        full_text = await _call_gemini_api(prompt)
    except RuntimeError:
        raise
    except Exception as e:
        logger.error("Gemini call failed: %s", e)
        raise RuntimeError(f"AI generation failed: {e}") from e

    # Split at the improvements separator
    if "---IMPROVEMENTS---" in full_text:
        parts = full_text.split("---IMPROVEMENTS---", 1)
        resume_text = parts[0].strip()
        improvements = [
            line.lstrip("- ").strip()
            for line in parts[1].strip().split("\n")
            if line.strip() and line.strip() != "-"
        ][:6]
    else:
        resume_text = full_text
        improvements = [
            "Optimized resume for ATS compatibility",
            "Integrated job description keywords throughout",
            "Rewrote experience bullets using STAR format",
            "Enhanced career objective for target role",
            "Reorganized skills section for relevance",
        ]

    logger.info("Resume optimization complete. Length: %d chars", len(resume_text))
    return resume_text, improvements
