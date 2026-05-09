from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class LeavesExpiringInput(BaseModel):
    year: int | None = None


class LeavesExpiringOutput(BaseModel):
    employee_id: int
    name: str
    days_left: int


class ListLeavesExpiringYearEndTool(ToolBase):
    name = "list_leaves_expiring_year_end"
    description = "Danh sách nhân viên còn phép năm sắp hết hạn cuối năm"
    input_model = LeavesExpiringInput
    output_model = LeavesExpiringOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: LeavesExpiringInput
    ) -> ToolResult:
        year = args.year or 2026
        result = await session.execute(text("""
            SELECT e.id, e.full_name,
                   12 - COALESCE(SUM(
                       CASE WHEN lr.status = 'approved' THEN
                           (lr.end_date - lr.start_date + 1) ELSE 0 END
                   ), 0) AS days_left
            FROM employees e
            LEFT JOIN leave_requests lr ON lr.employee_id = e.id
                AND lr.deleted_at IS NULL
                AND EXTRACT(YEAR FROM lr.start_date) = :year
            WHERE e.deleted_at IS NULL AND e.status = 'active'
            GROUP BY e.id, e.full_name
            HAVING 12 - COALESCE(SUM(
                CASE WHEN lr.status = 'approved' THEN
                    (lr.end_date - lr.start_date + 1) ELSE 0 END
            ), 0) > 0
            ORDER BY days_left DESC
        """), {"year": year})
        rows = [
            {"employee_id": r[0], "name": r[1], "days_left": int(r[2])}
            for r in result.fetchall()
        ]
        return ToolResult(data=rows, rows_returned=len(rows))
