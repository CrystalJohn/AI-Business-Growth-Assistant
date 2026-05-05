import time
from functools import wraps

from app.repositories.audit_repo import AuditRepository


def audited(tool_name: str):
    """Decorator auto-log tool execution vào audit_log."""

    def decorator(func):
        @wraps(func)
        async def wrapper(self, session, user, args, *rest, **kwargs):
            started = time.time()
            status, blocked_reason, error_msg = "success", None, None
            result = None
            try:
                result = await func(self, session, user, args, *rest, **kwargs)
                return result
            except PermissionError as e:
                status, blocked_reason = "blocked", str(e)
                raise
            except Exception as e:
                status, error_msg = "error", str(e)
                raise
            finally:
                await AuditRepository(session).log_query(
                    user_id=user.user_id,
                    role=user.role,
                    question="",
                    mode="tool",
                    tool_name=tool_name,
                    args=args.model_dump() if args else None,
                    rows_returned=result.rows_returned if result else 0,
                    duration_ms=int((time.time() - started) * 1000),
                    status=status,
                    blocked_reason=blocked_reason,
                    error_message=error_msg,
                )
                await session.commit()

        return wrapper

    return decorator
