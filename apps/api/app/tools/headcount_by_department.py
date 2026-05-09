from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class HeadcountInput(BaseModel):
    date_snapshot: str | None = None


class HeadcountOutput(BaseModel):
    phong_ban: str
    so_nhan_vien: int
    nam: int
    nu: int


class HeadcountByDepartmentTool(ToolBase):
    name = "get_headcount_by_department"
    description = "Headcount nhân viên theo phòng ban, phân tách nam/nữ"
    input_model = HeadcountInput
    output_model = HeadcountOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: HeadcountInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT
                d.name AS phong_ban,
                COUNT(e.id) AS so_nhan_vien,
                SUM(CASE WHEN e.gender = 'M' THEN 1 ELSE 0 END) AS nam,
                SUM(CASE WHEN e.gender = 'F' THEN 1 ELSE 0 END) AS nu
            FROM employees e
            JOIN departments d ON d.id = e.department_id
            WHERE e.deleted_at IS NULL AND e.status = 'active'
            GROUP BY d.name
            ORDER BY so_nhan_vien DESC
        """))
        rows = [
            {
                "phong_ban": r[0],
                "so_nhan_vien": r[1],
                "nam": r[2],
                "nu": r[3],
            }
            for r in result.fetchall()
        ]
        return ToolResult(data=rows, rows_returned=len(rows), chart_type="bar")
