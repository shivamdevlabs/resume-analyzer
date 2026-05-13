"""
services/pdf_generator.py — Professional ATS-friendly resume PDF generator.

Design: Clean single-column layout inspired by industry-standard ATS templates.
- Standard fonts (Helvetica) — fully ATS-parseable
- Clear visual hierarchy: name → contact → sections → entries → bullets
- Right-aligned dates via Table (ATS-safe, reader-friendly)
- Consistent spacing and alignment throughout
"""

import io
import re
import logging
from xml.sax.saxutils import escape as xml_escape

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    HRFlowable,
    Table,
    TableStyle,
    KeepTogether,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────
#  Design tokens  (single place to tweak the look)
# ─────────────────────────────────────────────────
BLACK = colors.HexColor("#000000")
DARK_GRAY = colors.HexColor("#222222")
MID_GRAY = colors.HexColor("#444444")
LIGHT_GRAY = colors.HexColor("#888888")
RULE_LIGHT = colors.HexColor("#BBBBBB")
ACCENT = colors.HexColor("#1B3A6B")  # deep navy — used ONLY for name

PAGE_W, PAGE_H = LETTER
L_MARGIN = R_MARGIN = 0.45 * inch  # tighter margins = more usable space
USABLE_W = PAGE_W - L_MARGIN - R_MARGIN


# ─────────────────────────────────────────────────
#  Section heading vocabulary
# ─────────────────────────────────────────────────
SECTION_HEADINGS = {
    "CAREER",
    "CAREER OBJECTIVE",
    "CAREER SUMMARY",
    "SUMMARY",
    "PROFESSIONAL SUMMARY",
    "EXECUTIVE SUMMARY",
    "PROFILE",
    "OBJECTIVE",
    "ABOUT",
    "EXPERIENCE",
    "WORK EXPERIENCE",
    "PROFESSIONAL EXPERIENCE",
    "EMPLOYMENT",
    "EMPLOYMENT HISTORY",
    "CAREER HISTORY",
    "WORK HISTORY",
    "EDUCATION",
    "EDUCATIONAL BACKGROUND",
    "ACADEMIC BACKGROUND",
    "ACADEMIC QUALIFICATIONS",
    "SKILLS",
    "TECHNICAL SKILLS",
    "CORE COMPETENCIES",
    "KEY SKILLS",
    "TECHNICAL EXPERTISE",
    "TECHNOLOGIES",
    "TOOLS & TECHNOLOGIES",
    "CERTIFICATIONS",
    "CERTIFICATES",
    "LICENSES",
    "CERTIFICATIONS & LICENSES",
    "COURSES & CERTIFICATIONS",
    "PROJECTS",
    "KEY PROJECTS",
    "PERSONAL PROJECTS",
    "ACADEMIC PROJECTS",
    "AWARDS",
    "ACHIEVEMENTS",
    "HONORS & AWARDS",
    "ACCOMPLISHMENTS",
    "PUBLICATIONS",
    "RESEARCH",
    "INTERPERSONAL SKILLS",
    "SOFT SKILLS",
    "VOLUNTEER",
    "VOLUNTEERING",
    "COMMUNITY SERVICE",
    "LANGUAGES",
    "INTERESTS",
    "HOBBIES",
    "REFERENCES",
    "ADDITIONAL INFORMATION",
}


# ─────────────────────────────────────────────────
#  Typography / style factory
# ─────────────────────────────────────────────────
def _styles() -> dict:
    base = getSampleStyleSheet()["Normal"]

    def s(name, **kw):
        defaults = dict(
            parent=base,
            fontName="Helvetica",
            fontSize=10,
            leading=14,
            textColor=DARK_GRAY,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
        )
        defaults.update(kw)
        return ParagraphStyle(name, **defaults)

    return {
        # ── Header ──────────────────────────────────
        "name": s(
            "S_Name",
            fontName="Helvetica-Bold",
            fontSize=17,  # reduced from 22
            leading=20,
            textColor=ACCENT,
            alignment=TA_CENTER,
            spaceAfter=1,
        ),
        "contact": s(
            "S_Contact",
            fontSize=8.5,
            leading=11,
            textColor=MID_GRAY,
            alignment=TA_CENTER,
            spaceAfter=0,
        ),
        # ── Section heading ──────────────────────────
        "heading": s(
            "S_Heading",
            fontName="Helvetica-Bold",
            fontSize=10,  # reduced from 11
            leading=12,
            textColor=BLACK,
            spaceBefore=6,  # reduced from 10
            spaceAfter=1,
        ),
        # ── Entry rows ───────────────────────────────
        "entry_title": s(
            "S_EntryTitle",
            fontName="Helvetica-Bold",
            fontSize=9.5,  # reduced from 10
            leading=12,
            textColor=DARK_GRAY,
        ),
        "entry_date": s(
            "S_EntryDate",
            fontSize=8.5,  # reduced from 9
            leading=12,
            textColor=MID_GRAY,
            alignment=TA_RIGHT,
        ),
        "entry_sub": s(
            "S_EntrySub",
            fontName="Helvetica-Oblique",
            fontSize=8.5,  # reduced from 9.5
            leading=11,
            textColor=MID_GRAY,
            spaceAfter=1,  # reduced from 2
        ),
        # ── Body content ─────────────────────────────
        "bullet": s(
            "S_Bullet",
            fontSize=9,  # reduced from 9.5
            leading=12,  # reduced from 14
            textColor=DARK_GRAY,
            leftIndent=12,
            firstLineIndent=-8,
            spaceAfter=1,
        ),
        "body": s(
            "S_Body",
            fontSize=9,
            leading=12,
            textColor=DARK_GRAY,
            spaceAfter=1,
        ),
        "skill_row": s(
            "S_SkillRow",
            fontSize=9,
            leading=12,
            textColor=DARK_GRAY,
            spaceAfter=1,
        ),
    }


# ─────────────────────────────────────────────────
#  Small helpers
# ─────────────────────────────────────────────────
def _e(text: str) -> str:
    """Escape XML/HTML special characters for ReportLab."""
    return xml_escape(str(text).strip())


def _is_heading(line: str) -> bool:
    return line.strip().rstrip(":").upper() in SECTION_HEADINGS


def _is_rule(line: str) -> bool:
    s = line.strip()
    return len(s) > 3 and all(c in "-=_─═—" for c in s)


_DATE_RE = re.compile(
    r"(?:"
    r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}"
    r"(?:\s*[-–—]\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|present|Current|Till\s*Date|Now))?"
    r"|\d{1,2}/\d{4}(?:\s*[-–]\s*(?:\d{1,2}/\d{4}|Present|present))?"
    r"|\d{4}\s*[-–—]\s*(?:\d{4}|Present|present|Current|Till\s*Date)"
    r")",
    re.IGNORECASE,
)


def _split_date(line: str):
    """
    Try to extract a trailing date from a line.
    Returns (left_text, date_text) or (line, None).
    """
    stripped = line.strip()
    # Look for date separated by whitespace or | at end of line
    m = re.search(
        r"(?:\s{2,}|\s*\|\s*)(" + _DATE_RE.pattern + r")\s*$",
        stripped,
        re.IGNORECASE,
    )
    if m:
        left = stripped[: m.start()].strip().rstrip("|–—- ").strip()
        if left:
            return left, m.group(1).strip()
    return stripped, None


def _two_col(left: str, right: str, st: dict) -> Table:
    """Build a left-title / right-date two-column row."""
    lw = USABLE_W * 0.70
    rw = USABLE_W * 0.30
    tbl = Table(
        [
            [
                Paragraph(_e(left), st["entry_title"]),
                Paragraph(_e(right), st["entry_date"]),
            ]
        ],
        colWidths=[lw, rw],
    )
    tbl.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    return tbl


def _hr(thickness=0.6, color=BLACK, before=1, after=3) -> HRFlowable:
    return HRFlowable(
        width="100%",
        thickness=thickness,
        color=color,
        spaceBefore=before,
        spaceAfter=after,
    )


# ─────────────────────────────────────────────────
#  Main generator
# ─────────────────────────────────────────────────
def generate_pdf(resume_text: str) -> bytes:
    """
    Convert plain-text resume into a professional, ATS-friendly PDF.
    Returns PDF bytes.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=LETTER,
        leftMargin=L_MARGIN,
        rightMargin=R_MARGIN,
        topMargin=0.4 * inch,  # reduced from 0.65
        bottomMargin=0.4 * inch,  # reduced from 0.65
    )

    st = _styles()
    story: list = []
    lines = [l.rstrip() for l in resume_text.split("\n")]
    idx, total = 0, len(lines)

    # ── 1. Skip leading blanks ────────────────────
    while idx < total and not lines[idx].strip():
        idx += 1

    # ── 2. Name (first non-empty line) ───────────
    if idx < total:
        story.append(Paragraph(_e(lines[idx].strip()), st["name"]))
        story.append(_hr(thickness=1.5, color=ACCENT, before=2, after=2))
        idx += 1

    # ── 3. Contact block ─────────────────────────
    #    Collect until blank line or section heading
    contacts = []
    while idx < total:
        line = lines[idx].strip()
        if not line:
            if contacts:
                idx += 1
                break
            idx += 1
            continue
        if _is_heading(line):
            break
        contacts.append(line)
        idx += 1

    if contacts:
        contact_str = "  |  ".join(contacts)
        story.append(Paragraph(_e(contact_str), st["contact"]))

    story.append(Spacer(1, 2))
    story.append(_hr(thickness=0.5, color=RULE_LIGHT, before=1, after=3))

    # ── 4. Body sections ─────────────────────────
    while idx < total:
        raw = lines[idx]
        line = raw.strip()
        idx += 1

        if not line:
            story.append(Spacer(1, 1))  # minimal blank-line spacer
            continue

        if _is_rule(line):
            continue

        # ── Section heading
        if _is_heading(line):
            block = [
                Paragraph(_e(line.upper()), st["heading"]),
                _hr(thickness=0.8, color=BLACK, before=1, after=3),
            ]
            story.append(KeepTogether(block))
            continue

        # ── Bullet point
        if line[:1] in "•-*◦▪–→":
            text = line.lstrip("•-*◦▪–→ ").strip()
            story.append(Paragraph(f"• {_e(text)}", st["bullet"]))
            continue

        # ── Try to split off a trailing date → two-column entry row
        left, date = _split_date(line)
        if date:
            story.append(_two_col(left, date, st))
            continue

        # ── Sub-line heuristics  (location, university subtitle, job title)
        #    Short, no date, not all-caps → render as italic sub-entry
        is_short = len(line) < 90
        has_comma = "," in line
        no_url = not any(c in line for c in ["@", "://", "\\"])
        not_allcaps = not line.isupper()
        if is_short and not_allcaps and no_url and (has_comma or line.istitle()):
            story.append(Paragraph(_e(line), st["entry_sub"]))
            continue

        # ── Default body text
        story.append(Paragraph(_e(line), st["body"]))

    doc.build(story)
    data = buf.getvalue()
    buf.close()
    logger.info("PDF generated — %d bytes, %d lines", len(data), total)
    return data
