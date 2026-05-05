from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def set_rls_context(
    session: AsyncSession,
    user_id: int,
    role: str,
    dept_id: int | None = None,
) -> None:
    """SET LOCAL session vars cho RLS policies đọc.

    Dùng SET LOCAL (transaction-scoped) thay vì SET (session-scoped)
    vì connection pool reuse sessions → transaction-scoped đảm bảo isolation.
    """
    await session.execute(text(f"SET LOCAL app.user_id = '{user_id}'"))
    await session.execute(text(f"SET LOCAL app.role = '{role}'"))
    if dept_id is not None:
        await session.execute(text(f"SET LOCAL app.dept_id = '{dept_id}'"))
