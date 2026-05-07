from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.mock_user import MockUser, get_mock_user
from app.schemas.query import QueryRequest
from app.services.llm.factory import get_provider
from app.services.llm_router import LLMRouter

router = APIRouter()


@router.post("/query")
async def chat_query(
    request: QueryRequest,
    user: MockUser = Depends(get_mock_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    provider = get_provider()
    llm_router = LLMRouter(provider)
    return await llm_router.route(request.question, user, db)
