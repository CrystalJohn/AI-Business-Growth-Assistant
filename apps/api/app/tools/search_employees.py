from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class SearchEmployeesInput(BaseModel):
    query: str
    limit: int = 20


class SearchEmployeesOutput(BaseModel):
    id: int
    name: str
    dept: str
    level: str | None = None
    joined_at: str


class SearchEmployeesTool(ToolBase):
    name = "search_employees"
    description = "Tìm kiếm nhân viên theo tên, email hoặc mã nhân viên"
    input_model = SearchEmployeesInput
    output_model = SearchEmployeesOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: SearchEmployeesInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT e.id, e.full_name, d.name, e.job_title, e.join_date::text
            FROM employees e
            JOIN departments d ON d.id = e.department_id
            WHERE e.deleted_at IS NULL
              AND (e.full_name ILIKE :q OR e.email ILIKE :q OR e.employee_code ILIKE :q)
            ORDER BY e.full_name
            LIMIT :lim
        """), {"q": f"%{args.query}%", "lim": args.limit})
        rows = [
            {"id": r[0], "name": r[1], "dept": r[2], "level": r[3], "joined_at": r[4]}
            for r in result.fetchall()
        ]
        return ToolResult(data=rows, rows_returned=len(rows))
