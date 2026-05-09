from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.db.session import get_db
from app.schemas.query import QueryRequest
from app.services.llm.factory import get_provider
from app.services.llm_router import LLMRouter

router = APIRouter()


@router.post("/query")
async def chat_query(
    request: QueryRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    provider = get_provider()
    llm_router = LLMRouter(provider)
    return await llm_router.route(request.question, user, db)
