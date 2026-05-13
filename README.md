# CareerCraft – ATS Resume Optimizer

An AI-powered full-stack web application that generates ATS-friendly resumes tailored to any job description.

## Tech Stack

| Layer    | Technology                        |
|----------|-----------------------------------|
| Frontend | React.js + Vite                   |
| Backend  | Python + FastAPI + Uvicorn        |
| Database | MongoDB (Motor async driver)      |
| AI       | Google Gemini 1.5 Flash           |
| PDF      | ReportLab                         |

---

## Project Structure

```
resume-analyzer/
├── frontend/                  ← React.js frontend (Vite)
│   ├── src/
│   │   ├── components/        Navbar, ResumeForm, ResultPanel, etc.
│   │   ├── pages/             LandingPage, AnalyzePage
│   │   ├── services/          api.js (Axios + mock fallback)
│   │   └── hooks/             useResumeAnalyzer.js
│   └── package.json
├── backend/                   ← Python FastAPI backend
│   ├── main.py                App entry point
│   ├── config.py              Settings & env vars
│   ├── requirements.txt       Python dependencies
│   ├── .env                   Environment variables (create this!)
│   ├── routers/
│   │   ├── analyze.py         POST /api/analyze
│   │   └── download.py        GET  /api/download/{id}
│   ├── services/
│   │   ├── parser.py          PDF/DOCX/TXT resume parser
│   │   ├── keyword_extractor.py  ATS keyword extraction
│   │   ├── ai_service.py      Gemini API integration
│   │   ├── scorer.py          ATS score calculator
│   │   └── pdf_generator.py   ReportLab PDF generation
│   ├── models/
│   │   ├── schemas.py         Pydantic models
│   │   └── database.py        MongoDB (Motor) connection
│   └── utils/
│       └── helpers.py         Text cleaning, ID generation
└── README.md
```

---

## Getting Started

### 1. Frontend

```bash
cd frontend
npm install
npm run dev
```
Runs at **http://localhost:5173**

> The frontend has a **built-in mock API**. If the backend isn't running, it automatically falls back to demo data.

---

### 2. Backend

#### a) Create your `.env` file

```bash
cd backend
copy .env.example .env
```

Edit `.env` and fill in:

```env
GEMINI_API_KEY=your_actual_gemini_api_key
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=careercraft
CORS_ORIGINS=http://localhost:5173
```

> Get a free Gemini API key at: https://aistudio.google.com/app/apikey

#### b) Install dependencies & run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at **http://localhost:8000**

- API docs: **http://localhost:8000/api/docs**
- Health check: **http://localhost:8000/api/health**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/api/health` | Backend + DB + AI health check |
| `POST` | `/api/analyze` | Analyze resume + JD → optimized resume |
| `GET`  | `/api/download/{id}` | Download generated resume as PDF |

### POST `/api/analyze`

**Request** (`multipart/form-data`):
```
job_description  (string, required)  Full job description
resume_text      (string, optional)  Pasted resume text
resume_file      (file, optional)    PDF / DOCX / TXT upload
```

**Response** (`JSON`):
```json
{
  "success": true,
  "analysis_id": "abc123def456",
  "generated_resume": "John Doe\n...",
  "ats_score": 87,
  "matched_keywords": ["Python", "FastAPI", "Docker"],
  "total_keywords": 20,
  "improvements": [
    "Rewrote summary to align with job requirements",
    "Added 8 missing ATS keywords naturally",
    "Converted experience bullets to STAR format"
  ]
}
```

---

## Features

- 📄 **Dual resume input** — Paste text or drag-and-drop PDF/DOCX
- 🤖 **AI-powered** — Google Gemini 1.5 Flash rewrites your resume
- 🎯 **ATS keyword matching** — Identifies and inserts missing keywords
- 📊 **Animated ATS score gauge** — Visual 0–100 compatibility score
- ✨ **STAR-format rewriting** — Quantified, impactful bullet points
- 📥 **PDF download** — Clean, professional PDF via ReportLab
- 🗄️ **MongoDB persistence** — Analysis history stored for retrieval
- 🔔 **Toast notifications** — Real-time success/error feedback
- 📱 **Fully responsive** — Mobile, tablet, and desktop
