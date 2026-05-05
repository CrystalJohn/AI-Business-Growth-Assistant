from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.models.employee import Employee
from app.repositories.base import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    model = Employee

    async def get_with_department(self, id: int) -> Optional[Employee]:
        stmt = (
            select(Employee)
            .where(Employee.id == id, Employee.deleted_at.is_(None))
            .options(selectinload(Employee.department))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_department(self, department_id: int) -> List[Employee]:
        stmt = (
            select(Employee)
            .where(
                Employee.department_id == department_id,
                Employee.deleted_at.is_(None),
            )
            .options(selectinload(Employee.department))
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_name(self, name: str, limit: int = 50) -> List[Employee]:
        stmt = (
            select(Employee)
            .where(
                Employee.full_name.ilike(f"%{name}%"),
                Employee.deleted_at.is_(None),
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_active(self) -> int:
        from sqlalchemy import func

        stmt = (
            select(func.count())
            .select_from(Employee)
            .where(Employee.deleted_at.is_(None), Employee.status == "active")
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()
