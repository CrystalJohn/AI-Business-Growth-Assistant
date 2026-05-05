from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.mock_user import MockUser
from app.tools.base import ToolBase, ToolResult


class LeaveBalanceInput(BaseModel):
    employee_id: int


class LeaveBalanceOutput(BaseModel):
    employee_id: int
    name: str
    annual_left: int
    used: int
    pending: int


class GetLeaveBalanceTool(ToolBase):
    name = "get_leave_balance"
    description = "Xem số ngày phép còn lại, đã dùng và đang chờ duyệt của nhân viên"
    input_model = LeaveBalanceInput
    output_model = LeaveBalanceOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: MockUser, args: LeaveBalanceInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT
                e.id, e.full_name,
                COALESCE(SUM(CASE WHEN lr.status = 'approved' THEN
                    (lr.end_date - lr.start_date + 1) ELSE 0 END), 0) AS used,
                COALESCE(SUM(CASE WHEN lr.status = 'pending' THEN
                    (lr.end_date - lr.start_date + 1) ELSE 0 END), 0) AS pending
            FROM employees e
            LEFT JOIN leave_requests lr ON lr.employee_id = e.id
                AND lr.deleted_at IS NULL
                AND EXTRACT(YEAR FROM lr.start_date) = EXTRACT(YEAR FROM CURRENT_DATE)
            WHERE e.id = :emp_id AND e.deleted_at IS NULL
            GROUP BY e.id, e.full_name
        """), {"emp_id": args.employee_id})
        row = result.fetchone()
        if not row:
            return ToolResult(data={}, rows_returned=0)
        annual_total = 12
        used = int(row[2])
        pending = int(row[3])
        data = {
            "employee_id": row[0], "name": row[1],
            "annual_left": max(0, annual_total - used - pending),
            "used": used, "pending": pending,
        }
        return ToolResult(data=data, rows_returned=1)
