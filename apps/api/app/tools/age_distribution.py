from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class AgeDistributionInput(BaseModel):
    bucket_size: int = 5


class AgeDistributionOutput(BaseModel):
    age_range: str
    count: int


class AgeDistributionTool(ToolBase):
    name = "get_age_distribution"
    description = "Phân bố độ tuổi nhân viên theo bucket"
    input_model = AgeDistributionInput
    output_model = AgeDistributionOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: AgeDistributionInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT
                CONCAT(
                    (EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date)) / :bucket) * :bucket,
                    '-',
                    (EXTRACT(YEAR FROM AGE(CURRENT_DATE, birth_date)) / :bucket) * :bucket + :bucket - 1
                ) AS age_range,
                COUNT(*) AS count
            FROM employees
            WHERE deleted_at IS NULL AND status = 'active'
            GROUP BY age_range
            ORDER BY age_range
        """), {"bucket": args.bucket_size})
        rows = [{"age_range": r[0], "count": r[1]} for r in result.fetchall()]
        return ToolResult(data=rows, rows_returned=len(rows), chart_type="bar")
