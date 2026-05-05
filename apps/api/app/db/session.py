from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings

async_engine = create_async_engine(
    settings.async_database_url,
    echo=False,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Standard DB session — no RLS context.

    Dùng cho endpoints không cần auth (health, schema, sql validate).
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_db_with_rls(
    user_id: int,
    role: str,
    dept_id: int | None = None,
) -> AsyncGenerator[AsyncSession, None]:
    """DB session với RLS context set.

    Dùng cho endpoints cần auth (chat/query, employee list).
    SET LOCAL đảm bảo vars chỉ tồn tại trong transaction này.
    """
    from app.middleware.db_context import set_rls_context

    async with AsyncSessionLocal() as session:
        try:
            await set_rls_context(session, user_id, role, dept_id)
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
