from datetime import datetime, timezone

from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.db.session import async_engine

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    db_status = "ok"
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        db_status = f"error: {exc}"

    overall = "ok" if db_status == "ok" else "degraded"
    return {
        "status": overall,
        "db": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "llm_provider": settings.llm_provider,
        "version": "0.2.0",
    }
