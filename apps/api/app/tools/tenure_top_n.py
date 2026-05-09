from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class TenureTopNInput(BaseModel):
    n: int = 10


class TenureTopNOutput(BaseModel):
    name: str
    dept: str
    years: float


class ListTenureTopNTool(ToolBase):
    name = "list_tenure_top_n"
    description = "Top N nhân viên có thâm niên cao nhất"
    input_model = TenureTopNInput
    output_model = TenureTopNOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: TenureTopNInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT e.full_name, d.name,
                   ROUND(EXTRACT(EPOCH FROM (CURRENT_DATE - e.join_date)) / 86400 / 365, 1) AS years
            FROM employees e
            JOIN departments d ON d.id = e.department_id
            WHERE e.deleted_at IS NULL AND e.status = 'active'
            ORDER BY e.join_date ASC
            LIMIT :n
        """), {"n": args.n})
        rows = [{"name": r[0], "dept": r[1], "years": r[2]} for r in result.fetchall()]
        return ToolResult(data=rows, rows_returned=len(rows), chart_type="bar")
