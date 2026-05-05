from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.mock_user import MockUser
from app.tools.base import ToolBase, ToolResult


class EmployeeDetailInput(BaseModel):
    employee_id: int


class EmployeeDetailOutput(BaseModel):
    id: int
    employee_code: str
    full_name: str
    email: str
    phone: str | None = None
    birth_date: str
    gender: str
    join_date: str
    job_title: str
    department: str
    status: str


class GetEmployeeDetailTool(ToolBase):
    name = "get_employee_detail"
    description = "Xem chi tiết thông tin nhân viên (không bao gồm lương)"
    input_model = EmployeeDetailInput
    output_model = EmployeeDetailOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: MockUser, args: EmployeeDetailInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT e.id, e.employee_code, e.full_name, e.email, e.phone,
                   e.birth_date::text, e.gender, e.join_date::text,
                   e.job_title, d.name, e.status
            FROM employees e
            JOIN departments d ON d.id = e.department_id
            WHERE e.id = :emp_id AND e.deleted_at IS NULL
        """), {"emp_id": args.employee_id})
        row = result.fetchone()
        if not row:
            return ToolResult(data={}, rows_returned=0)
        data = {
            "id": row[0], "employee_code": row[1], "full_name": row[2],
            "email": row[3], "phone": row[4], "birth_date": row[5],
            "gender": row[6], "join_date": row[7], "job_title": row[8],
            "department": row[9], "status": row[10],
        }
        return ToolResult(data=data, rows_returned=1)
