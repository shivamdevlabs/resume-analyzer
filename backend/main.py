"""
main.py — CareerCraft FastAPI application entry point.

Registers routes, CORS middleware, and MongoDB lifecycle hooks.
Run with: uvicorn main:app --reload
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from models import database
from services import ai_service
from routers import analyze, download

# ─────────────────────────────────────────────
#  Logging setup
# ─────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────
#  Application lifespan (startup / shutdown)
# ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup and shutdown tasks."""
    # STARTUP
    logger.info("🚀 CareerCraft backend starting…")
    logger.info("   Environment : %s", settings.APP_ENV)
    logger.info("   MongoDB URI : %s", settings.MONGODB_URI)
    logger.info(
        "   Gemini API  : %s",
        "configured ✅" if settings.GEMINI_API_KEY else "NOT SET ⚠️",
    )

    await database.connect()

    yield  # App is running

    # SHUTDOWN
    logger.info("Shutting down CareerCraft backend…")
    await database.disconnect()


# ─────────────────────────────────────────────
#  FastAPI app instance
# ─────────────────────────────────────────────
app = FastAPI(
    title="CareerCraft API",
    description="AI-powered ATS resume optimizer — generate tailored resumes using Google Gemini.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ─────────────────────────────────────────────
#  CORS — allow the React dev server
# ─────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  Routes
# ─────────────────────────────────────────────
app.include_router(analyze.router, prefix="/api", tags=["Resume Analysis"])
app.include_router(download.router, prefix="/api", tags=["Download"])


# ─────────────────────────────────────────────
#  Health check endpoint
# ─────────────────────────────────────────────
@app.get("/api/health", tags=["Health"], summary="Backend health check")
async def health():
    """Returns backend, database, and AI service status."""
    # Check MongoDB
    db_status = "disconnected"
    try:
        client = database.get_client()
        await client.admin.command("ping")
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    # Check Gemini API key + discover model
    ai_status = "not configured"
    ai_model = None
    if ai_service.is_configured():
        try:
            ai_model = await ai_service._discover_model()
            ai_status = f"configured — using {ai_model}"
        except RuntimeError as e:
            ai_status = f"error: {str(e)[:120]}"

    return JSONResponse(
        {
            "status": "ok",
            "version": "1.0.0",
            "database": db_status,
            "ai_service": ai_status,
            "ai_model": ai_model,
        }
    )


# ─────────────────────────────────────────────
#  Root redirect
# ─────────────────────────────────────────────
@app.get("/", include_in_schema=False)
async def root():
    return JSONResponse(
        {
            "message": "CareerCraft API is running!",
            "docs": "/api/docs",
            "health": "/api/health",
        }
    )


# ─────────────────────────────────────────────
#  Global exception handler
# ─────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "An internal server error occurred."},
    )
