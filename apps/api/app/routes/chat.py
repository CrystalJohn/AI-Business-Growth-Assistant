import time

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.mock_user import MockUser, get_mock_user
from app.repositories.audit_repo import AuditRepository
from app.schemas.query import QueryRequest, QueryResponse
from app.services.mock_llm import get_mock_response

router = APIRouter()


@router.post("/query", response_model=QueryResponse)
async def chat_query(
    request: QueryRequest,
    user: MockUser = Depends(get_mock_user),
    db: AsyncSession = Depends(get_db),
) -> QueryResponse:
    started = time.time()
    try:
        response = get_mock_response(request.question)
        duration_ms = int((time.time() - started) * 1000)

        await AuditRepository(db).log_query(
            user_id=user.user_id,
            role=user.role,
            question=request.question,
            mode="sql",
            sql_executed=response.sql,
            rows_returned=len(response.rows),
            duration_ms=duration_ms,
            status="success",
        )
        return response

    except Exception as e:
        duration_ms = int((time.time() - started) * 1000)
        await AuditRepository(db).log_query(
            user_id=user.user_id,
            role=user.role,
            question=request.question,
            mode="sql",
            duration_ms=duration_ms,
            status="error",
            error_message=str(e),
        )
        raise
