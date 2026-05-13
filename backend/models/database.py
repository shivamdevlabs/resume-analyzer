"""
models/database.py — Async MongoDB connection using Motor.
Provides a single shared client and database instance.
"""

import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config import settings

logger = logging.getLogger(__name__)

# Module-level client (initialized on startup)
_client: Optional[AsyncIOMotorClient] = None


def get_client() -> AsyncIOMotorClient:
    """Return the shared Motor client (must call connect() first)."""
    if _client is None:
        raise RuntimeError("MongoDB client not initialized. Call connect() during app startup.")
    return _client


def get_database():
    """Return the careercraft database instance."""
    return get_client()[settings.MONGODB_DB_NAME]


def get_analyses_collection():
    """Return the 'analyses' collection."""
    return get_database()["analyses"]


async def connect():
    """Open the MongoDB connection. Called in FastAPI lifespan startup."""
    global _client
    _client = AsyncIOMotorClient(
        settings.MONGODB_URI,
        serverSelectionTimeoutMS=5000,
    )
    # Verify connection is reachable
    try:
        await _client.admin.command("ping")
        logger.info("✅ MongoDB connected: %s / %s", settings.MONGODB_URI, settings.MONGODB_DB_NAME)
    except ConnectionFailure as e:
        logger.warning("⚠️  MongoDB connection failed: %s — running without DB persistence.", e)


async def disconnect():
    """Close the MongoDB connection. Called in FastAPI lifespan shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed.")
