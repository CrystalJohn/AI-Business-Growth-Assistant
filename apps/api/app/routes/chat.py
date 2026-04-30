from fastapi import APIRouter

from app.models import QueryRequest, QueryResponse
from app.services.mock_llm import get_mock_response

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def chat_query(request: QueryRequest) -> QueryResponse:
    return get_mock_response(request.question)
