from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class AvgSalaryByLevelInput(BaseModel):
    dept_id: int | None = None


class AvgSalaryByLevelOutput(BaseModel):
    level: str
    avg: float
    min: float
    max: float
    count: int


class GetAvgSalaryByLevelTool(ToolBase):
    name = "get_avg_salary_by_level"
    description = "Lương trung bình, min, max theo cấp bậc (Manager only)"
    input_model = AvgSalaryByLevelInput
    output_model = AvgSalaryByLevelOutput
    required_role = "HR_Manager"

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: AvgSalaryByLevelInput
    ) -> ToolResult:
        if args.dept_id:
            result = await session.execute(text("""
                SELECT p.level,
                       ROUND(AVG(p.base_salary)) AS avg_sal,
                       MIN(p.base_salary) AS min_sal,
                       MAX(p.base_salary) AS max_sal,
                       COUNT(*) AS cnt
                FROM payroll p
                JOIN employees e ON e.id = p.employee_id
                WHERE p.deleted_at IS NULL AND e.deleted_at IS NULL
                  AND e.department_id = :dept_id
                GROUP BY p.level
                ORDER BY avg_sal DESC
            """), {"dept_id": args.dept_id})
        else:
            result = await session.execute(text("""
                SELECT p.level,
                       ROUND(AVG(p.base_salary)) AS avg_sal,
                       MIN(p.base_salary) AS min_sal,
                       MAX(p.base_salary) AS max_sal,
                       COUNT(*) AS cnt
                FROM payroll p
                WHERE p.deleted_at IS NULL
                GROUP BY p.level
                ORDER BY avg_sal DESC
            """))
        rows = [
            {"level": r[0], "avg": float(r[1]), "min": float(r[2]),
             "max": float(r[3]), "count": r[4]}
            for r in result.fetchall()
        ]
        return ToolResult(data=rows, rows_returned=len(rows), chart_type="bar")
