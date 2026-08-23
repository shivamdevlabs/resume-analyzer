"""
services/pdf_generator.py — Professional ATS-friendly two-column resume PDF generator.

Design: Premium two-column layout matching the target template.
- standard standard fonts (Helvetica, Helvetica-Bold) — fully ATS-parseable.
- Programmatic vector icons for phone, email, location, LinkedIn, GitHub, calendar.
- Left column (56%): Summary, Experience, Education.
- Right column (40%): Technical Skills, Projects, Certifications.
- Balanced padding and spacing to ensure single-page fitting.
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
from reportlab.graphics.shapes import Drawing, Rect, Circle, Line, Polygon, String

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────
#  Design tokens
# ─────────────────────────────────────────────────
BLACK = colors.HexColor("#000000")
DARK_GRAY = colors.HexColor("#222222")
MID_GRAY = colors.HexColor("#555555")
LIGHT_GRAY = colors.HexColor("#888888")
RULE_LIGHT = colors.HexColor("#CCCCCC")

PAGE_W, PAGE_H = LETTER
L_MARGIN = R_MARGIN = 0.4 * inch  # tight margins for maximum use of space
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
    "TECHNOLOGY STACK",
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

# Left column and right column section assignments
LEFT_SECTIONS = [
    "CAREER OBJECTIVE", "CAREER SUMMARY", "SUMMARY", "PROFESSIONAL SUMMARY",
    "EXECUTIVE SUMMARY", "PROFILE", "OBJECTIVE", "ABOUT",
    "EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EMPLOYMENT",
    "EMPLOYMENT HISTORY", "CAREER HISTORY", "WORK HISTORY",
    "EDUCATION", "EDUCATIONAL BACKGROUND", "ACADEMIC BACKGROUND", "ACADEMIC QUALIFICATIONS"
]

LOCATION_KEYWORDS = {
    "india", "usa", "uk", "germany", "canada", "australia",
    "noida", "delhi", "gurgaon", "bangalore", "bengaluru", "mumbai", "pune", "hyderabad", "chennai", "kolkata",
    "york", "francisco", "angeles", "chicago", "boston", "seattle", "austin", "texas", "california", "london",
    "singapore", "dubai", "ghaziabad", "meerut", "gurugram"
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
            fontSize=8,
            leading=11,
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
            fontSize=16,
            leading=18,
            textColor=BLACK,
            spaceAfter=1,
        ),
        "title": s(
            "S_Title",
            fontSize=9.5,
            leading=11.5,
            textColor=MID_GRAY,
            spaceAfter=1,
        ),
        "contact_inline": s(
            "S_ContactInline",
            fontSize=7.5,
            leading=9.5,
            textColor=MID_GRAY,
        ),
        "contact_right": s(
            "S_ContactRight",
            fontSize=7.5,
            leading=9.5,
            textColor=MID_GRAY,
            alignment=TA_RIGHT,
        ),
        # ── Section heading ──────────────────────────
        "section_heading": s(
            "S_SectionHeading",
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=BLACK,
            spaceBefore=4,
            spaceAfter=1,
        ),
        # ── Experience ──────────────────────────────
        "job_title": s(
            "S_JobTitle",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=11,
            textColor=BLACK,
            spaceBefore=3,
        ),
        "job_company": s(
            "S_JobCompany",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            textColor=MID_GRAY,
        ),
        "job_meta": s(
            "S_JobMeta",
            fontSize=7.5,
            leading=9,
            textColor=MID_GRAY,
        ),
        "job_bullet": s(
            "S_JobBullet",
            fontSize=7.5,
            leading=9.5,
            textColor=DARK_GRAY,
            leftIndent=8,
            firstLineIndent=-5,
            spaceAfter=1,
        ),
        # ── Education ───────────────────────────────
        "edu_degree": s(
            "S_EduDegree",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10.5,
            textColor=BLACK,
            spaceBefore=3,
        ),
        "edu_inst": s(
            "S_EduInst",
            fontSize=8,
            leading=10,
            textColor=DARK_GRAY,
        ),
        # ── Skills ──────────────────────────────────
        "skill_category": s(
            "S_SkillCategory",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10.5,
            textColor=BLACK,
            spaceBefore=3,
        ),
        "skill_list": s(
            "S_SkillList",
            fontSize=7.5,
            leading=9.5,
            textColor=DARK_GRAY,
        ),
        # ── Projects ────────────────────────────────
        "project_name": s(
            "S_ProjectName",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10.5,
            textColor=BLACK,
            spaceBefore=3,
        ),
        "project_stack": s(
            "S_ProjectStack",
            fontName="Helvetica-Bold",
            fontSize=7.5,
            leading=9.5,
            textColor=MID_GRAY,
        ),
        "project_bullet": s(
            "S_ProjectBullet",
            fontSize=7.5,
            leading=9.5,
            textColor=DARK_GRAY,
            leftIndent=8,
            firstLineIndent=-5,
            spaceAfter=1,
        ),
        # ── Certifications ──────────────────────────
        "cert_name": s(
            "S_CertName",
            fontName="Helvetica-Bold",
            fontSize=8.5,
            leading=10.5,
            textColor=BLACK,
            spaceBefore=3,
        ),
        "cert_provider": s(
            "S_CertProvider",
            fontName="Helvetica-Oblique",
            fontSize=7.5,
            leading=9,
            textColor=MID_GRAY,
        ),
        # ── General Body ────────────────────────────
        "body": s(
            "S_Body",
            fontSize=7.5,
            leading=9.5,
            textColor=DARK_GRAY,
        ),
    }

# ─────────────────────────────────────────────────
#  Programmatic Vector Icons
# ─────────────────────────────────────────────────
def create_icon(name: str, size: int = 10, color=colors.HexColor("#222222")) -> Drawing:
    """Draw custom crisp vector icons programmatically."""
    d = Drawing(size, size)
    if name == "phone":
        # Handset shape
        d.add(Line(2, 2, 8, 8, strokeColor=color, strokeWidth=2.2, strokeLineCap=1))
        d.add(Line(2, 2, 1, 4, strokeColor=color, strokeWidth=1.8, strokeLineCap=1))
        d.add(Line(8, 8, 9, 6, strokeColor=color, strokeWidth=1.8, strokeLineCap=1))
    elif name == "email":
        # Envelope card
        d.add(Rect(0.5, 1.5, size - 1, size - 3, strokeColor=color, fillColor=None, strokeWidth=0.8))
        d.add(Line(0.5, size - 1.5, size / 2.0, size / 2.0 - 0.5, strokeColor=color, strokeWidth=0.8))
        d.add(Line(size - 0.5, size - 1.5, size / 2.0, size / 2.0 - 0.5, strokeColor=color, strokeWidth=0.8))
    elif name == "location":
        # Map pin locator
        cx, cy = size / 2.0, size * 0.65
        r = size * 0.25
        d.add(Circle(cx, cy, r, strokeColor=color, fillColor=None, strokeWidth=0.8))
        d.add(Circle(cx, cy, 0.8, strokeColor=color, fillColor=color, strokeWidth=0.5))
        d.add(Polygon([cx - r + 0.3, cy - 0.5, cx + r - 0.3, cy - 0.5, cx, 1], strokeColor=color, fillColor=color, strokeWidth=0.5))
    elif name == "linkedin":
        # Rounded box with "in"
        d.add(Rect(0, 0, size, size, rx=1, ry=1, strokeColor=color, fillColor=color))
        d.add(String(2, 2, "in", fontName="Helvetica-Bold", fontSize=size * 0.75, fillColor=colors.white))
    elif name == "github":
        # Stylized cat icon
        cx, cy = size / 2.0, size / 2.0 - 0.5
        r = size * 0.35
        d.add(Circle(cx, cy, r, strokeColor=color, fillColor=color))
        d.add(Polygon([cx - r * 0.8, cy + r * 0.5, cx - r * 0.3, cy + r * 0.8, cx - r * 0.9, cy + r * 1.2], strokeColor=color, fillColor=color))
        d.add(Polygon([cx + r * 0.8, cy + r * 0.5, cx + r * 0.3, cy + r * 0.8, cx + r * 0.9, cy + r * 1.2], strokeColor=color, fillColor=color))
    elif name == "calendar":
        # Small calendar card
        d.add(Rect(0.5, 0.5, size - 1, size - 2, strokeColor=color, fillColor=None, strokeWidth=0.8))
        d.add(Line(0.5, size - 3.5, size - 0.5, size - 3.5, strokeColor=color, strokeWidth=0.8))
        d.add(Line(2.5, size - 2.5, 2.5, size - 0.5, strokeColor=color, strokeWidth=1))
        d.add(Line(size - 3.5, size - 2.5, size - 3.5, size - 0.5, strokeColor=color, strokeWidth=1))
    return d

# ─────────────────────────────────────────────────
#  Small Helpers & Text Formatters
# ─────────────────────────────────────────────────
def format_text(text: str) -> str:
    """Escape XML characters and convert simple markdown to HTML tags."""
    escaped = xml_escape(str(text).strip())
    # Convert **bold** to <b>bold</b>
    escaped = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", escaped)
    # Convert *italic* to <i>italic</i>
    escaped = re.sub(r"\*(.*?)\*", r"<i>\1</i>", escaped)
    return escaped

def clean_social_handle(handle: str, platform: str) -> str:
    """Remove URL schemes and prefixes to yield standard short handles."""
    h = handle.strip()
    h = re.sub(r"^https?://(www\.)?", "", h, flags=re.IGNORECASE)
    if platform == "linkedin":
        h = re.sub(r"^linkedin\.com/(in|profile)/?", "", h, flags=re.IGNORECASE)
    elif platform == "github":
        h = re.sub(r"^github\.com/?", "", h, flags=re.IGNORECASE)
    h = h.rstrip("/")
    return h

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
    """Extract trailing date from a line."""
    stripped = line.strip()
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

def is_location(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in LOCATION_KEYWORDS)

def parse_experience_line(left_text: str):
    """Parse experience title, company, and location from text."""
    parts = [p.strip() for p in left_text.split(",") if p.strip()]
    if not parts:
        return "", "", ""
    if len(parts) == 1:
        return parts[0], "", ""
    if len(parts) == 2:
        if is_location(parts[1]):
            return parts[0], "", parts[1]
        else:
            return parts[0], parts[1], ""
    if len(parts) == 3:
        return parts[0], parts[1], parts[2]
    return parts[0], parts[1], ", ".join(parts[2:])

def _hr(thickness=0.6, color=BLACK, before=1, after=3) -> HRFlowable:
    return HRFlowable(
        width="100%",
        thickness=thickness,
        color=color,
        spaceBefore=before,
        spaceAfter=after,
    )

def render_section_heading(title: str, st: dict) -> list:
    """Render a clean black section header with horizontal line."""
    return [
        Spacer(1, 4),
        Paragraph(title.upper(), st["section_heading"]),
        _hr(thickness=0.8, color=BLACK, before=1, after=3),
    ]

# ─────────────────────────────────────────────────
#  Section Parsing & Content Extraction
# ─────────────────────────────────────────────────
def parse_summary_section(sec_lines, st):
    sec_flowables = []
    text_content = " ".join([l.strip() for l in sec_lines if l.strip()])
    if text_content:
        sec_flowables.append(Paragraph(format_text(text_content), st["body"]))
    return sec_flowables

def parse_experience_section(sec_lines, st):
    sec_flowables = []
    job_entries = []
    current_job = None
    
    for line in sec_lines:
        line_str = line.strip()
        if not line_str:
            continue
        
        if line_str[:1] in "•-*◦▪–→":
            if current_job:
                bullet_text = line_str.lstrip("•-*◦▪–→ ").strip()
                current_job["bullets"].append(bullet_text)
            continue
            
        left_t, date_v = _split_date(line_str)
        if date_v or (not current_job and not line_str.startswith("*") and not line_str.startswith("•")):
            title, company, loc = parse_experience_line(left_t)
            current_job = {
                "title": title,
                "company": company,
                "location": loc,
                "date": date_v or "",
                "bullets": []
            }
            job_entries.append(current_job)
        else:
            if current_job:
                current_job["bullets"].append(line_str)
                
    for job in job_entries:
        job_flowables = []
        job_flowables.append(Paragraph(format_text(job["title"]), st["job_title"]))
        if job["company"]:
            job_flowables.append(Paragraph(format_text(job["company"]), st["job_company"]))
            
        meta_cols = []
        meta_widths = []
        if job["date"]:
            meta_cols.extend([create_icon("calendar", 9, DARK_GRAY), Paragraph(format_text(job["date"]), st["job_meta"])])
            meta_widths.extend([12, 100])
        if job["location"]:
            if meta_cols:
                meta_cols.append("")
                meta_widths.append(10)
            meta_cols.extend([create_icon("location", 9, DARK_GRAY), Paragraph(format_text(job["location"]), st["job_meta"])])
            meta_widths.extend([12, 120])
            
        if meta_cols:
            meta_table = Table([meta_cols], colWidths=meta_widths)
            meta_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 1),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                    ]
                )
            )
            job_flowables.append(meta_table)
            
        for bullet in job["bullets"]:
            job_flowables.append(Paragraph(f"• {format_text(bullet)}", st["job_bullet"]))
            
        sec_flowables.extend(job_flowables)
    return sec_flowables

def parse_education_section(sec_lines, st):
    sec_flowables = []
    edu_entries = []
    for line in sec_lines:
        line_str = line.strip()
        if not line_str:
            continue
        left_t, date_v = _split_date(line_str)
        parts = [p.strip() for p in left_t.split(",") if p.strip()]
        if parts:
            degree = parts[0]
            inst = parts[1] if len(parts) > 1 else ""
            city = parts[2] if len(parts) > 2 else ""
            edu_entries.append({
                "degree": degree,
                "institution": inst,
                "city": city,
                "date": date_v or ""
            })
            
    for edu in edu_entries:
        edu_flowables = []
        edu_flowables.append(Paragraph(format_text(edu["degree"]), st["edu_degree"]))
        inst_text = edu["institution"]
        if edu["city"]:
            inst_text += f", {edu['city']}"
        if inst_text:
            edu_flowables.append(Paragraph(format_text(inst_text), st["edu_inst"]))
        if edu["date"]:
            date_table = Table(
                [[create_icon("calendar", 9, DARK_GRAY), Paragraph(format_text(edu["date"]), st["job_meta"])]],
                colWidths=[12, 100]
            )
            date_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            edu_flowables.append(date_table)
        sec_flowables.extend(edu_flowables)
    return sec_flowables

def parse_skills_section(sec_lines, st):
    sec_flowables = []
    skills_entries = []
    for line in sec_lines:
        line_str = line.strip()
        if not line_str:
            continue
        line_str = line_str.lstrip("•-*◦▪–→ ").strip()
        if ":" in line_str:
            cat, techs = line_str.split(":", 1)
            skills_entries.append({
                "category": cat.strip(),
                "skills": techs.strip()
            })
        else:
            skills_entries.append({
                "category": "",
                "skills": line_str
            })
            
    for entry in skills_entries:
        entry_flowables = []
        if entry["category"]:
            entry_flowables.append(Paragraph(format_text(entry["category"]), st["skill_category"]))
        entry_flowables.append(Paragraph(format_text(entry["skills"]), st["skill_list"]))
        sec_flowables.extend(entry_flowables)
    return sec_flowables

def parse_projects_section(sec_lines, st):
    sec_flowables = []
    project_entries = []
    current_proj = None
    
    for line in sec_lines:
        line_str = line.strip()
        if not line_str:
            continue
        if line_str[:1] in "•-*◦▪–→":
            if current_proj:
                bullet_text = line_str.lstrip("•-*◦▪–→ ").strip()
                current_proj["bullets"].append(bullet_text)
            continue
            
        left_t, date_v = _split_date(line_str)
        parts = [p.strip() for p in re.split(r"\||\s{2,}", left_t) if p.strip()]
        if parts:
            name = parts[0]
            stack = parts[1] if len(parts) > 1 else ""
            current_proj = {
                "name": name,
                "stack": stack,
                "date": date_v or "",
                "bullets": []
            }
            project_entries.append(current_proj)
        else:
            if current_proj:
                current_proj["bullets"].append(line_str)
                
    for proj in project_entries:
        proj_flowables = []
        proj_flowables.append(Paragraph(format_text(proj["name"]), st["project_name"]))
        if proj["stack"]:
            proj_flowables.append(Paragraph(format_text(proj["stack"]), st["project_stack"]))
        if proj["date"]:
            date_table = Table(
                [[create_icon("calendar", 9, DARK_GRAY), Paragraph(format_text(proj["date"]), st["job_meta"])]],
                colWidths=[12, 100]
            )
            date_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            proj_flowables.append(date_table)
        for bullet in proj["bullets"]:
            proj_flowables.append(Paragraph(f"• {format_text(bullet)}", st["project_bullet"]))
        sec_flowables.extend(proj_flowables)
    return sec_flowables

def parse_certifications_section(sec_lines, st):
    sec_flowables = []
    cert_entries = []
    i = 0
    while i < len(sec_lines):
        line = sec_lines[i].strip()
        if not line:
            i += 1
            continue
        line = line.lstrip("•-*◦▪–→ ").strip()
        provider = ""
        if i + 1 < len(sec_lines):
            next_line = sec_lines[i+1].strip()
            if next_line and not next_line.startswith(("*", "•", "-", "*")):
                if len(next_line) < 30:
                    provider = next_line
                    i += 1
        cert_entries.append({"name": line, "provider": provider})
        i += 1
        
    for cert in cert_entries:
        cert_flowables = []
        cert_flowables.append(Paragraph(format_text(cert["name"]), st["cert_name"]))
        if cert["provider"]:
            cert_flowables.append(Paragraph(format_text(cert["provider"]), st["cert_provider"]))
        sec_flowables.extend(cert_flowables)
    return sec_flowables

def parse_default_section(sec_lines, st):
    sec_flowables = []
    for line in sec_lines:
        line_str = line.strip()
        if not line_str:
            continue
        if line_str[:1] in "•-*◦▪–→":
            bullet_text = line_str.lstrip("•-*◦▪–→ ").strip()
            sec_flowables.append(Paragraph(f"• {format_text(bullet_text)}", st["body"]))
        else:
            sec_flowables.append(Paragraph(format_text(line_str), st["body"]))
    return sec_flowables

# ─────────────────────────────────────────────────
#  Main Generator
# ─────────────────────────────────────────────────
def generate_pdf(resume_text: str) -> bytes:
    """
    Convert plain-text resume into a premium, two-column PDF.
    Returns PDF bytes.
    """
    if not resume_text or len(resume_text) < 10:
        return b""

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=LETTER,
        leftMargin=L_MARGIN,
        rightMargin=R_MARGIN,
        topMargin=0.4 * inch,
        bottomMargin=0.4 * inch,
    )

    st = _styles()
    story: list = []
    lines = [l.rstrip() for l in resume_text.split("\n")]
    idx, total = 0, len(lines)

    # ── 1. Skip leading blanks ────────────────────
    while idx < total and not lines[idx].strip():
        idx += 1

    # ── 2. Name (first non-empty line) ───────────
    name_line = ""
    if idx < total:
        name_line = lines[idx].strip()
        idx += 1

    # ── 3. Contact and Title Candidate block ──────
    contact_candidate_lines = []
    while idx < total:
        line = lines[idx]
        if not line.strip():
            idx += 1
            if contact_candidate_lines:
                break
            continue
        if _is_heading(line):
            break
        contact_candidate_lines.append(line.strip())
        idx += 1

    # Determine Title and Contact Lines
    title_line = ""
    contact_lines = []
    if len(contact_candidate_lines) >= 2:
        # Check if the first line is contact info
        first_line = contact_candidate_lines[0]
        if any(c in first_line for c in ["@", "|", "github", "linkedin"]) or (any(char.isdigit() for char in first_line) and len(first_line) < 30):
            contact_lines = contact_candidate_lines
        else:
            title_line = contact_candidate_lines[0]
            contact_lines = contact_candidate_lines[1:]
    elif len(contact_candidate_lines) == 1:
        first_line = contact_candidate_lines[0]
        if any(c in first_line for c in ["@", "|", "github", "linkedin"]) or (any(char.isdigit() for char in first_line) and len(first_line) < 30):
            contact_lines = contact_candidate_lines
        else:
            title_line = contact_candidate_lines[0]

    # Parse and extract contact tokens
    tokens = []
    for line in contact_lines:
        parts = re.split(r"\||•|·|\*", line)
        for p in parts:
            p_str = p.strip()
            if p_str:
                tokens.append(p_str)

    phone = ""
    email = ""
    location = ""
    linkedin = ""
    github = ""

    assigned = set()
    for i, t in enumerate(tokens):
        if "@" in t:
            email = t
            assigned.add(i)
            break
    for i, t in enumerate(tokens):
        if i not in assigned and ("github" in t.lower() or "git" in t.lower()):
            github = clean_social_handle(t, "github")
            assigned.add(i)
            break
    for i, t in enumerate(tokens):
        if i not in assigned and ("linkedin" in t.lower() or "link" in t.lower()):
            linkedin = clean_social_handle(t, "linkedin")
            assigned.add(i)
            break
    for i, t in enumerate(tokens):
        if i not in assigned and any(c.isdigit() for c in t) and len(t.replace(' ', '').replace('-', '').replace('+', '')) < 15:
            phone = t
            assigned.add(i)
            break
    remaining = [t for i, t in enumerate(tokens) if i not in assigned]
    if remaining:
        location = remaining[0]
        if len(remaining) > 1 and not linkedin:
            linkedin = clean_social_handle(remaining[1], "linkedin")
        if len(remaining) > 2 and not github:
            github = clean_social_handle(remaining[2], "github")

    # ── 4. Parse Sections ─────────────────────────
    sections = {}
    current_sec = None

    while idx < total:
        raw = lines[idx]
        line = raw.strip()
        idx += 1

        if not line:
            continue

        if _is_rule(line):
            continue

        if _is_heading(line):
            current_sec = line.upper().strip().rstrip(":")
            sections[current_sec] = []
            continue

        if current_sec:
            sections[current_sec].append(line)

    # ── 5. Assemble Header Flowables ──────────────
    left_header_flowables = []
    if name_line:
        left_header_flowables.append(Paragraph(format_text(name_line), st["name"]))
    
    # Extract first job title as subtitle fallback if not explicitly found in header
    if not title_line:
        first_job_title = ""
        exp_sec = None
        for k in sections:
            if k in ["EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE"]:
                exp_sec = sections[k]
                break
        if exp_sec:
            for l in exp_sec:
                l_str = l.strip()
                if l_str and not l_str.startswith(("*", "•", "-")):
                    left_t, _ = _split_date(l_str)
                    title, _, _ = parse_experience_line(left_t)
                    if title:
                        first_job_title = title
                        break
        if first_job_title:
            title_line = first_job_title

    if title_line:
        left_header_flowables.append(Paragraph(format_text(title_line), st["title"]))

    if phone or email or location:
        contact_cols = []
        contact_widths = []
        
        if phone:
            contact_cols.extend([create_icon("phone", 9, DARK_GRAY), Paragraph(phone, st["contact_inline"])])
            contact_widths.extend([12, 80])
        if email:
            if contact_cols:
                contact_cols.append("")
                contact_widths.append(10)
            contact_cols.extend([create_icon("email", 9, DARK_GRAY), Paragraph(email, st["contact_inline"])])
            contact_widths.extend([12, 115])
        if location:
            if contact_cols:
                contact_cols.append("")
                contact_widths.append(10)
            contact_cols.extend([create_icon("location", 9, DARK_GRAY), Paragraph(location, st["contact_inline"])])
            contact_widths.extend([12, 115])
            
        if contact_cols:
            contact_row_table = Table([contact_cols], colWidths=contact_widths)
            contact_row_table.setStyle(
                TableStyle(
                    [
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 0),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                        ("TOPPADDING", (0, 0), (-1, -1), 0),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                    ]
                )
            )
            left_header_flowables.append(Spacer(1, 4))
            left_header_flowables.append(contact_row_table)

    right_header_flowables = []
    if linkedin:
        linkedin_table = Table(
            [[create_icon("linkedin", 9, DARK_GRAY), Paragraph(linkedin, st["contact_right"])]],
            colWidths=[12, 100],
            hAlign="RIGHT"
        )
        linkedin_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        right_header_flowables.append(linkedin_table)
        
    if github:
        github_table = Table(
            [[create_icon("github", 9, DARK_GRAY), Paragraph(github, st["contact_right"])]],
            colWidths=[12, 100],
            hAlign="RIGHT"
        )
        github_table.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        if linkedin:
            right_header_flowables.append(Spacer(1, 3))
        right_header_flowables.append(github_table)

    header_table = Table(
        [[left_header_flowables, right_header_flowables]],
        colWidths=[USABLE_W * 0.70, USABLE_W * 0.30]
    )
    header_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    story.append(header_table)
    from reportlab.platypus.flowables import KeepInFrame
    
    # ── 6. Assemble Column Flowables ─────────────
    left_column_flowables = []
    right_column_flowables = []

    for sec_name, sec_lines in sections.items():
        clean_lines = [l.strip() for l in sec_lines if l.strip()]
        if not clean_lines:
            continue

        heading_flowables = render_section_heading(sec_name, st)
        
        if sec_name in ["CAREER OBJECTIVE", "CAREER SUMMARY", "SUMMARY", "PROFESSIONAL SUMMARY", "EXECUTIVE SUMMARY", "PROFILE", "OBJECTIVE", "ABOUT"]:
            content_flowables = parse_summary_section(clean_lines, st)
        elif sec_name in ["EXPERIENCE", "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "EMPLOYMENT", "EMPLOYMENT HISTORY", "CAREER HISTORY", "WORK HISTORY"]:
            content_flowables = parse_experience_section(clean_lines, st)
        elif sec_name in ["EDUCATION", "EDUCATIONAL BACKGROUND", "ACADEMIC BACKGROUND", "ACADEMIC QUALIFICATIONS"]:
            content_flowables = parse_education_section(clean_lines, st)
        elif sec_name in ["SKILLS", "TECHNICAL SKILLS", "CORE COMPETENCIES", "KEY SKILLS", "TECHNICAL EXPERTISE", "TECHNOLOGIES", "TECHNOLOGY STACK", "TOOLS & TECHNOLOGIES"]:
            content_flowables = parse_skills_section(clean_lines, st)
        elif sec_name in ["PROJECTS", "KEY PROJECTS", "PERSONAL PROJECTS", "ACADEMIC PROJECTS"]:
            content_flowables = parse_projects_section(clean_lines, st)
        elif sec_name in ["CERTIFICATIONS", "CERTIFICATES", "LICENSES", "CERTIFICATIONS & LICENSES", "COURSES & CERTIFICATIONS"]:
            content_flowables = parse_certifications_section(clean_lines, st)
        else:
            content_flowables = parse_default_section(clean_lines, st)

        all_sec_flowables = heading_flowables + content_flowables
        
        if sec_name in LEFT_SECTIONS:
            left_column_flowables.extend(all_sec_flowables)
        else:
            right_column_flowables.extend(all_sec_flowables)

    # ── 7. Render Two-Column Table ────────────────
    columns_table = Table(
        [[left_column_flowables, Spacer(1, 1), right_column_flowables]],
        colWidths=[USABLE_W * 0.56, USABLE_W * 0.04, USABLE_W * 0.40]
    )
    columns_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ("TOPPADDING", (0, 0), (-1, -1), 0),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ]
        )
    )
    
    usable_height = PAGE_H - 0.8 * inch
    
    # Wrap the entire content in KeepInFrame to ensure it fits on 1 page and prevents LayoutError
    content_flowables = [header_table, Spacer(1, 4), _hr(thickness=1.2, color=BLACK, before=2, after=4), columns_table]
    story = [KeepInFrame(USABLE_W, usable_height, content_flowables, mode='shrink')]

    # Build document
    doc.build(story)
    data = buf.getvalue()
    buf.close()
    
    logger.info("PDF generated — %d bytes, %d lines", len(data), total)
    return data
