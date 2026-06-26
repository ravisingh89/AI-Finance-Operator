"""
In-memory store as primary with optional PostgreSQL.
Works on Render free tier which blocks outbound DB connections.
"""
import json
import os
from datetime import datetime
from collections import defaultdict

# ── In-memory store (survives the request lifetime on free tier) ──────────────
_store = {
    "reports":      {},   # user_id -> latest report dict
    "statements":   {},   # statement_id -> status
    "transactions": defaultdict(list),  # user_id -> list of txs
}

def save_report(user_id: str, statement_id: str, report: dict):
    _store["reports"][user_id] = {
        "statement_id": statement_id,
        "report": report,
        "created_at": datetime.utcnow().isoformat(),
    }
    # Also persist to /tmp so it survives across requests
    try:
        os.makedirs("/tmp/reports", exist_ok=True)
        with open(f"/tmp/reports/{user_id}.json", "w") as f:
            json.dump(_store["reports"][user_id], f)
    except Exception as e:
        print(f"[WARN] Could not persist report to disk: {e}")

def get_report(user_id: str) -> dict | None:
    # Check memory first
    if user_id in _store["reports"]:
        return _store["reports"][user_id]
    # Try disk
    try:
        path = f"/tmp/reports/{user_id}.json"
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
                _store["reports"][user_id] = data
                return data
    except Exception:
        pass
    return None

def set_status(statement_id: str, status: str):
    _store["statements"][statement_id] = status
    try:
        os.makedirs("/tmp/statements", exist_ok=True)
        with open(f"/tmp/statements/{statement_id}.txt", "w") as f:
            f.write(status)
    except Exception:
        pass

def get_status(statement_id: str) -> str:
    if statement_id in _store["statements"]:
        return _store["statements"][statement_id]
    try:
        path = f"/tmp/statements/{statement_id}.txt"
        if os.path.exists(path):
            with open(path) as f:
                return f.read().strip()
    except Exception:
        pass
    return "processing"

# ── SQLAlchemy kept for optional use — won't crash if DB unreachable ──────────
engine = None
AsyncSessionLocal = None

try:
    from app.config import settings
    if settings.DATABASE_URL and "postgresql" in settings.DATABASE_URL:
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        engine = create_async_engine(settings.DATABASE_URL, echo=False,
                                     connect_args={"timeout": 5})
        AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession,
                                         expire_on_commit=False)
        print("[INFO] PostgreSQL engine configured")
except Exception as e:
    print(f"[WARN] PostgreSQL unavailable, using in-memory store: {e}")

async def get_db():
    if AsyncSessionLocal:
        async with AsyncSessionLocal() as session:
            yield session
    else:
        yield None

# Dummy ORM classes so imports don't break
class Statement: pass
class Transaction: pass
class FinancialReport: pass
class Base:
    metadata = type('metadata', (), {'create_all': lambda *a, **k: None})()
