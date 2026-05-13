"""
services/keyword_extractor.py — ATS keyword extraction from job descriptions.

Uses regex + curated pattern sets (no heavy NLP models required).
Identifies: programming languages, frameworks, tools, cloud, soft skills,
certifications, and action verbs commonly used in ATS systems.
"""

import re
import logging
from typing import List, Tuple

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
#  Curated keyword libraries
# ─────────────────────────────────────────────────────────────

TECH_KEYWORDS = {
    # Languages
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#", "Go", "Rust",
    "Ruby", "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "SQL", "Bash",
    "Shell", "Perl", "Dart", "Elixir", "Haskell",

    # Frontend
    "React", "React.js", "Next.js", "Vue", "Vue.js", "Angular", "Svelte",
    "HTML", "CSS", "SCSS", "Sass", "Tailwind", "Bootstrap", "Redux", "GraphQL",
    "REST APIs", "RESTful", "WebSockets", "Webpack", "Vite", "Babel",

    # Backend
    "FastAPI", "Flask", "Django", "Node.js", "Express", "Spring Boot",
    "Rails", "Laravel", "ASP.NET", "Gin", "Fiber", "NestJS",

    # Databases
    "MongoDB", "PostgreSQL", "MySQL", "SQLite", "Redis", "Elasticsearch",
    "DynamoDB", "Cassandra", "Oracle", "SQL Server", "Firebase", "Supabase",
    "Neo4j", "InfluxDB",

    # Cloud & DevOps
    "AWS", "Azure", "GCP", "Google Cloud", "Docker", "Kubernetes", "Terraform",
    "Ansible", "Jenkins", "GitHub Actions", "CircleCI", "Travis CI", "CI/CD",
    "Helm", "ArgoCD", "Prometheus", "Grafana", "Datadog", "New Relic",

    # AI / ML
    "Machine Learning", "Deep Learning", "NLP", "Computer Vision",
    "TensorFlow", "PyTorch", "Keras", "scikit-learn", "Pandas", "NumPy",
    "Hugging Face", "LangChain", "OpenAI", "LLM", "RAG", "Fine-tuning",
    "Spark", "Hadoop", "Airflow", "MLflow", "Kubeflow",

    # Tools & Practices
    "Git", "GitHub", "GitLab", "Bitbucket", "Jira", "Confluence", "Agile",
    "Scrum", "Kanban", "TDD", "BDD", "Microservices", "Serverless",
    "API Gateway", "Message Queue", "Kafka", "RabbitMQ", "gRPC",

    # Security
    "OAuth", "JWT", "SAML", "SSO", "OWASP", "Penetration Testing", "SOC 2",

    # Mobile
    "iOS", "Android", "React Native", "Flutter", "Xamarin",
}

SOFT_SKILL_KEYWORDS = {
    "Leadership", "Communication", "Problem-Solving", "Teamwork", "Collaboration",
    "Critical Thinking", "Time Management", "Project Management", "Mentoring",
    "Stakeholder Management", "Cross-functional", "Strategic Planning",
    "Analytical", "Detail-oriented", "Self-motivated", "Adaptable",
}

CERTIFICATION_KEYWORDS = {
    "AWS Certified", "Google Certified", "Azure Certified", "PMP", "Scrum Master",
    "CPA", "CFA", "CISSP", "CISA", "CompTIA", "Oracle Certified", "Certified",
}

# Combined for fast lookup
ALL_KEYWORDS = TECH_KEYWORDS | SOFT_SKILL_KEYWORDS | CERTIFICATION_KEYWORDS


# ─────────────────────────────────────────────────────────────
#  Extraction logic
# ─────────────────────────────────────────────────────────────

def extract_keywords(job_description: str) -> Tuple[List[str], int]:
    """
    Extract ATS-relevant keywords from a job description.

    Returns:
        Tuple of (matched_keyword_list, total_candidate_count)
    """
    if not job_description:
        return [], 0

    jd_lower = job_description.lower()
    found = set()

    # 1. Match against our curated library (case-insensitive whole-word)
    for kw in ALL_KEYWORDS:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, jd_lower):
            found.add(kw)

    # 2. Extract additional terms using regex patterns for common formats
    # Years of experience patterns → extract the technology/skill name
    exp_pattern = re.compile(
        r"(\d+\+?\s+years?\s+(?:of\s+)?(?:experience\s+(?:with|in|using)\s+)?)([A-Z][a-zA-Z.+#/\s]{1,30})",
        re.IGNORECASE
    )
    for match in exp_pattern.finditer(job_description):
        candidate = match.group(2).strip().rstrip(".,;:")
        if 2 <= len(candidate) <= 35 and candidate not in found:
            # Validate it looks like a tech term (not a generic word)
            if _is_tech_term(candidate):
                found.add(candidate)

    # 3. Bullet-point listed skills (e.g. "• Python, React, AWS")
    bullet_pattern = re.compile(r"[•\-\*]\s+(.+)")
    for match in bullet_pattern.finditer(job_description):
        line = match.group(1)
        # Split by commas and check each fragment
        for fragment in line.split(","):
            fragment = fragment.strip().rstrip(".,;:")
            if 1 < len(fragment) <= 30 and _is_tech_term(fragment):
                found.add(fragment)

    # Total candidate pool = all unique keywords found in JD +
    # a fixed baseline of the most critical tech terms to check against
    total = max(len(found), 15)

    logger.info("Extracted %d keywords from job description", len(found))
    return sorted(found), total


def get_missing_keywords(resume_text: str, jd_keywords: List[str]) -> List[str]:
    """Return keywords from JD that are NOT present in the resume."""
    resume_lower = resume_text.lower()
    missing = []
    for kw in jd_keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if not re.search(pattern, resume_lower):
            missing.append(kw)
    return missing


def get_matched_keywords(resume_text: str, jd_keywords: List[str]) -> List[str]:
    """Return keywords from JD that ARE already present in the resume."""
    resume_lower = resume_text.lower()
    matched = []
    for kw in jd_keywords:
        pattern = r"\b" + re.escape(kw.lower()) + r"\b"
        if re.search(pattern, resume_lower):
            matched.append(kw)
    return matched


# ─────────────────────────────────────────────────────────────
#  Internal helpers
# ─────────────────────────────────────────────────────────────

_COMMON_WORDS = {
    "the", "and", "for", "with", "from", "this", "that", "will", "have",
    "been", "your", "our", "are", "not", "you", "can", "all", "any",
    "experience", "years", "ability", "strong", "excellent", "good", "work",
    "team", "must", "required", "preferred", "including", "etc", "plus",
}

def _is_tech_term(term: str) -> bool:
    """Heuristic: is this word/phrase likely a technology or skill?"""
    t = term.strip().lower()
    if t in _COMMON_WORDS:
        return False
    if len(t) < 2 or len(t) > 40:
        return False
    # Allow terms with dots, +, # (e.g. "C++", "ASP.NET", "C#")
    if re.match(r"^[a-z0-9][a-z0-9\s\.\+\#\/\-]*$", t):
        return True
    return False
