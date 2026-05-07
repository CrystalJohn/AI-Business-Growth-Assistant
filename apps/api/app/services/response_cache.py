from cachetools import TTLCache

from app.config import settings

response_cache: TTLCache = TTLCache(
    maxsize=500,
    ttl=settings.llm_cache_ttl_seconds,
)
