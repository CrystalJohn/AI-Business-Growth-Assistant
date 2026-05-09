import time

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.schemas import CurrentUser
from app.db.session import get_db
from app.middleware.db_context import set_rls_context
from app.repositories.audit_repo import AuditRepository
from app.services.pii_masking import mask_response_data
from app.tools.registry import get_tool, list_tools

router = APIRouter(prefix="/tools", tags=["tools"])


@router.get("")
async def list_all_tools():
    return {"tools": list_tools()}


@router.post("/{tool_name}")
async def execute_tool(
    tool_name: str,
    args: dict,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        tool = get_tool(tool_name)
    except ValueError as e:
        raise HTTPException(404, str(e))

    try:
        validated_args = tool.input_model(**args)
    except Exception as e:
        raise HTTPException(400, f"Invalid args: {e}")

    try:
        tool.check_access(user)
    except PermissionError as e:
        raise HTTPException(403, str(e))

    await set_rls_context(db, user.user_id, user.role, user.dept_id)

    started = time.time()
    status, blocked_reason, error_msg = "success", None, None
    result = None
    try:
        result = await tool.execute(db, user, validated_args)
        masked_data, mask_applied = mask_response_data(result.data, user.role)
        return {
            "tool": tool_name,
            "data": masked_data,
            "rows_returned": result.rows_returned,
            "chart_type": result.chart_type,
            "mask_applied": mask_applied,
        }
    except PermissionError as e:
        status, blocked_reason = "blocked", str(e)
        raise HTTPException(403, str(e))
    except Exception as e:
        status, error_msg = "error", str(e)
        raise HTTPException(500, str(e))
    finally:
        await AuditRepository(db).log_query(
            user_id=user.user_id,
            role=user.role,
            question="",
            mode="tool",
            tool_name=tool_name,
            args=validated_args.model_dump() if validated_args else None,
            rows_returned=result.rows_returned if result else 0,
            duration_ms=int((time.time() - started) * 1000),
            status=status,
            blocked_reason=blocked_reason,
            error_message=error_msg,
        )
        await db.commit()
