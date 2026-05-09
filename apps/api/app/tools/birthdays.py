from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class BirthdaysInput(BaseModel):
    month: int | None = None
    year: int | None = None


class BirthdaysOutput(BaseModel):
    employee_id: int
    name: str
    dept: str
    dob: str


class ListBirthdaysThisMonthTool(ToolBase):
    name = "list_birthdays_this_month"
    description = "Danh sách nhân viên có sinh nhật trong tháng"
    input_model = BirthdaysInput
    output_model = BirthdaysOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: BirthdaysInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT e.id, e.full_name, d.name, e.birth_date::text
            FROM employees e
            JOIN departments d ON d.id = e.department_id
            WHERE e.deleted_at IS NULL AND e.status = 'active'
              AND EXTRACT(MONTH FROM e.birth_date) = :month
            ORDER BY EXTRACT(DAY FROM e.birth_date)
        """), {"month": args.month or 5})
        rows = [
            {"employee_id": r[0], "name": r[1], "dept": r[2], "dob": r[3]}
            for r in result.fetchall()
        ]
        return ToolResult(data=rows, rows_returned=len(rows))
