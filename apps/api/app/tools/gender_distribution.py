from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class GenderDistributionInput(BaseModel):
    by_dept: bool = False


class GenderDistributionOutput(BaseModel):
    label: str
    count: int


class GenderDistributionTool(ToolBase):
    name = "get_gender_distribution"
    description = "Phân bố giới tính nhân viên, tổng thể hoặc theo phòng ban"
    input_model = GenderDistributionInput
    output_model = GenderDistributionOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: GenderDistributionInput
    ) -> ToolResult:
        if args.by_dept:
            result = await session.execute(text("""
                SELECT
                    CONCAT(d.name, ' - ', CASE WHEN e.gender = 'M' THEN 'Nam' ELSE 'Nữ' END) AS label,
                    COUNT(*) AS count
                FROM employees e
                JOIN departments d ON d.id = e.department_id
                WHERE e.deleted_at IS NULL AND e.status = 'active'
                GROUP BY d.name, e.gender
                ORDER BY d.name, e.gender
            """))
        else:
            result = await session.execute(text("""
                SELECT
                    CASE WHEN gender = 'M' THEN 'Nam' ELSE 'Nữ' END AS label,
                    COUNT(*) AS count
                FROM employees
                WHERE deleted_at IS NULL AND status = 'active'
                GROUP BY gender
            """))
        rows = [{"label": r[0], "count": r[1]} for r in result.fetchall()]
        return ToolResult(data=rows, rows_returned=len(rows), chart_type="pie")
