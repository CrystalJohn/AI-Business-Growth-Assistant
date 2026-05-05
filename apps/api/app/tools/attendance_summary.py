from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.mock_user import MockUser
from app.tools.base import ToolBase, ToolResult


class AttendanceSummaryInput(BaseModel):
    employee_id: int
    period_start: str
    period_end: str


class AttendanceSummaryOutput(BaseModel):
    employee_id: int
    name: str
    days_present: int
    absent: int
    late: int


class GetAttendanceSummaryTool(ToolBase):
    name = "get_attendance_summary"
    description = "Tổng hợp chấm công nhân viên trong khoảng thời gian"
    input_model = AttendanceSummaryInput
    output_model = AttendanceSummaryOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: MockUser, args: AttendanceSummaryInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT
                e.id, e.full_name,
                SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS present,
                SUM(CASE WHEN a.status = 'absent' THEN 1 ELSE 0 END) AS absent,
                SUM(CASE WHEN a.status = 'late' THEN 1 ELSE 0 END) AS late
            FROM employees e
            LEFT JOIN attendance a ON a.employee_id = e.id
                AND a.work_date BETWEEN :start AND :end
            WHERE e.id = :emp_id AND e.deleted_at IS NULL
            GROUP BY e.id, e.full_name
        """), {
            "emp_id": args.employee_id,
            "start": args.period_start,
            "end": args.period_end,
        })
        row = result.fetchone()
        if not row:
            return ToolResult(data={}, rows_returned=0)
        data = {
            "employee_id": row[0], "name": row[1],
            "days_present": int(row[2] or 0),
            "absent": int(row[3] or 0),
            "late": int(row[4] or 0),
        }
        return ToolResult(data=data, rows_returned=1)
