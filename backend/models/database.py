"""
models/database.py — Async MongoDB connection using Motor.
Provides a single shared client and database instance, with a local JSON mock DB fallback.
"""

import logging
import json
import os
import base64
from datetime import datetime
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure

from config import settings
from utils.helpers import generate_analysis_id

logger = logging.getLogger(__name__)

# Module-level client (initialized on startup)
_client: Optional[AsyncIOMotorClient] = None
_use_mock_db: bool = False


class MockCursor:
    def __init__(self, docs):
        self.docs = docs
        self.index = 0

    def sort(self, key, direction=-1):
        reverse = (direction == -1)
        self.docs = sorted(self.docs, key=lambda x: x.get(key, datetime.utcnow()), reverse=reverse)
        return self

    def __aiter__(self):
        self.index = 0
        return self

    async def __anext__(self):
        if self.index >= len(self.docs):
            raise StopAsyncIteration
        doc = self.docs[self.index]
        self.index += 1
        return doc


class MockCollection:
    def __init__(self, name: str):
        self.name = name
        self.filepath = os.path.join(os.path.dirname(__file__), "..", "db_mock.json")

    def _load_data(self) -> dict:
        if not os.path.exists(self.filepath):
            return {"users": [], "analyses": []}
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"users": [], "analyses": []}

    def _save_data(self, data: dict):
        try:
            class DateTimeEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    return super().default(obj)
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, cls=DateTimeEncoder, indent=2)
        except Exception as e:
            logger.warning("Mock DB save failed: %s", e)

    def _encode_val(self, val):
        if isinstance(val, bytes):
            return {"__bytes__": base64.b64encode(val).decode("utf-8")}
        elif isinstance(val, dict):
            return {k: self._encode_val(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [self._encode_val(v) for v in val]
        elif isinstance(val, datetime):
            return val.isoformat()
        return val

    def _decode_val(self, val):
        if isinstance(val, dict) and "__bytes__" in val:
            return base64.b64decode(val["__bytes__"])
        elif isinstance(val, dict):
            return {k: self._decode_val(v) for k, v in val.items()}
        elif isinstance(val, list):
            return [self._decode_val(v) for v in val]
        elif isinstance(val, str) and (val.endswith("Z") or "T" in val):
            try:
                clean_val = val.replace("Z", "+00:00")
                return datetime.fromisoformat(clean_val)
            except Exception:
                pass
        return val

    async def insert_one(self, doc: dict):
        if "_id" not in doc:
            doc["_id"] = generate_analysis_id()
        
        doc_copy = self._encode_val(doc)
        data = self._load_data()
        data[self.name].append(doc_copy)
        self._save_data(data)
        
        class InsertOneResult:
            def __init__(self, inserted_id):
                self.inserted_id = inserted_id
        return InsertOneResult(doc["_id"])

    async def find_one(self, query: dict, projection: Optional[dict] = None) -> Optional[dict]:
        data = self._load_data()
        docs = data.get(self.name, [])
        for doc in docs:
            match = True
            for k, v in query.items():
                if k == "$or":
                    or_match = False
                    for sub_query in v:
                        sub_match = True
                        for sk, sv in sub_query.items():
                            if doc.get(sk) != sv:
                                sub_match = False
                                break
                        if sub_match:
                            or_match = True
                            break
                    if not or_match:
                        match = False
                        break
                elif doc.get(k) != v:
                    match = False
                    break
            if match:
                return self._decode_val(doc)
        return None

    def find(self, query: dict) -> MockCursor:
        data = self._load_data()
        docs = data.get(self.name, [])
        matched_docs = []
        for doc in docs:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                matched_docs.append(self._decode_val(doc))
        return MockCursor(matched_docs)


def get_client() -> AsyncIOMotorClient:
    """Return the shared Motor client, initializing it if necessary."""
    global _client
    if _client is None:
        logger.info("Initializing MongoDB client lazily...")
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
        )
    return _client


def get_database():
    """Return the careercraft database instance."""
    return get_client()[settings.MONGODB_DB_NAME]


def get_analyses_collection():
    """Return the 'analyses' collection."""
    global _use_mock_db
    if _use_mock_db:
        return MockCollection("analyses")
    return get_database()["analyses"]


def get_users_collection():
    """Return the 'users' collection."""
    global _use_mock_db
    if _use_mock_db:
        return MockCollection("users")
    return get_database()["users"]


async def connect():
    """Open the MongoDB connection. Called in FastAPI lifespan startup."""
    global _client, _use_mock_db
    try:
        _client = AsyncIOMotorClient(
            settings.MONGODB_URI,
            serverSelectionTimeoutMS=5000,
        )
        # Verify connection is reachable
        await _client.admin.command("ping")
        _use_mock_db = False
        logger.info(
            "✅ MongoDB connected: %s / %s",
            settings.MONGODB_URI,
            settings.MONGODB_DB_NAME,
        )
    except Exception as e:
        _use_mock_db = True
        logger.warning(
            "⚠️  MongoDB connection failed (%s: %s). Falling back to local mock JSON database.",
            type(e).__name__,
            e
        )


async def disconnect():
    """Close the MongoDB connection. Called in FastAPI lifespan shutdown."""
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed.")
