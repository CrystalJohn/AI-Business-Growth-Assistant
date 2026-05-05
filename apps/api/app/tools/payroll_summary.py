from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.mock_user import MockUser
from app.tools.base import ToolBase, ToolResult


class PayrollSummaryInput(BaseModel):
    year: int
    month: int


class PayrollSummaryOutput(BaseModel):
    dept: str
    total_gross: float
    headcount: int


class GetPayrollSummaryByMonthTool(ToolBase):
    name = "get_payroll_summary_by_month"
    description = "Tổng quỹ lương theo phòng ban cho tháng/năm cụ thể (Manager only)"
    input_model = PayrollSummaryInput
    output_model = PayrollSummaryOutput
    required_role = "HR_Manager"

    async def execute(
        self, session: AsyncSession, user: MockUser, args: PayrollSummaryInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT d.name AS dept,
                   SUM(p.base_salary + p.allowance) AS total_gross,
                   COUNT(*) AS headcount
            FROM payroll p
            JOIN employees e ON e.id = p.employee_id
            JOIN departments d ON d.id = e.department_id
            WHERE p.deleted_at IS NULL AND e.deleted_at IS NULL
              AND EXTRACT(YEAR FROM p.effective_date) = :year
              AND EXTRACT(MONTH FROM p.effective_date) = :month
            GROUP BY d.name
            ORDER BY total_gross DESC
        """), {"year": args.year, "month": args.month})
        rows = [
            {"dept": r[0], "total_gross": float(r[1]), "headcount": r[2]}
            for r in result.fetchall()
        ]
        return ToolResult(data=rows, rows_returned=len(rows), chart_type="bar")
