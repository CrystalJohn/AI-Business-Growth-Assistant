from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class TurnoverRateInput(BaseModel):
    start_date: str
    end_date: str


class TurnoverRateOutput(BaseModel):
    leavers: int
    avg_headcount: int
    rate: float


class GetTurnoverRateTool(ToolBase):
    name = "get_turnover_rate"
    description = "Tỉ lệ nghỉ việc trong khoảng thời gian (Manager only)"
    input_model = TurnoverRateInput
    output_model = TurnoverRateOutput
    required_role = "HR_Manager"

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: TurnoverRateInput
    ) -> ToolResult:
        result = await session.execute(text("""
            WITH leavers AS (
                SELECT COUNT(*) AS cnt
                FROM employees
                WHERE status = 'inactive'
                  AND deleted_at IS NOT NULL
                  AND deleted_at BETWEEN :start AND :end
            ),
            headcount AS (
                SELECT COUNT(*) AS cnt
                FROM employees
                WHERE deleted_at IS NULL AND status = 'active'
            )
            SELECT leavers.cnt, headcount.cnt
            FROM leavers, headcount
        """), {"start": args.start_date, "end": args.end_date})
        row = result.fetchone()
        leavers = int(row[0] or 0)
        avg_hc = int(row[1] or 1)
        rate = round(leavers / avg_hc * 100, 2) if avg_hc > 0 else 0.0
        data = {"leavers": leavers, "avg_headcount": avg_hc, "rate": rate}
        return ToolResult(data=data, rows_returned=1)
