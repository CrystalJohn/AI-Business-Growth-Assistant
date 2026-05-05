from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    model: Type[T]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, id: int) -> Optional[T]:
        return await self.session.get(self.model, id)

    async def list_active(self, limit: int = 100) -> List[T]:
        stmt = (
            select(self.model)
            .where(self.model.deleted_at.is_(None))  # type: ignore[attr-defined]
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, obj: T) -> T:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def delete_soft(self, obj: T) -> None:
        from datetime import datetime, timezone

        obj.deleted_at = datetime.now(timezone.utc)  # type: ignore[attr-defined]
        self.session.add(obj)
        await self.session.flush()
