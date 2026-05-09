from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class ContractsExpiringInput(BaseModel):
    days_ahead: int = 30


class ContractsExpiringOutput(BaseModel):
    employee_id: int
    name: str
    contract_end: str
    days_left: int


class ListContractsExpiringSoonTool(ToolBase):
    name = "list_contracts_expiring_soon"
    description = "Danh sách hợp đồng sắp hết hạn trong N ngày tới (Manager only)"
    input_model = ContractsExpiringInput
    output_model = ContractsExpiringOutput
    required_role = "HR_Manager"

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: ContractsExpiringInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT e.id, e.full_name, e.join_date::text,
                   (e.join_date + INTERVAL '1 year' * 3) AS contract_end,
                   EXTRACT(DAY FROM (e.join_date + INTERVAL '1 year' * 3 - CURRENT_DATE)) AS days_left
            FROM employees e
            WHERE e.deleted_at IS NULL AND e.status = 'active'
              AND (e.join_date + INTERVAL '1 year' * 3) BETWEEN CURRENT_DATE
                  AND CURRENT_DATE + INTERVAL '1 day' * :days
            ORDER BY days_left ASC
        """), {"days": args.days_ahead})
        rows = [
            {
                "employee_id": r[0], "name": r[1],
                "contract_end": str(r[3]), "days_left": int(r[4]),
            }
            for r in result.fetchall()
        ]
        return ToolResult(data=rows, rows_returned=len(rows))
