from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser
from app.tools.base import ToolBase, ToolResult


class PendingReviewsInput(BaseModel):
    period: str


class PendingReviewsOutput(BaseModel):
    employee_id: int
    name: str
    reviewer_id: int | None = None
    rating: str


class ListPendingPerformanceReviewsTool(ToolBase):
    name = "list_pending_performance_reviews"
    description = "Danh sách đánh giá hiệu suất theo kỳ"
    input_model = PendingReviewsInput
    output_model = PendingReviewsOutput
    required_role = None

    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: PendingReviewsInput
    ) -> ToolResult:
        result = await session.execute(text("""
            SELECT pr.employee_id, e.full_name, pr.reviewer_id, pr.rating
            FROM performance_reviews pr
            JOIN employees e ON e.id = pr.employee_id
            WHERE pr.deleted_at IS NULL AND pr.period = :period
            ORDER BY pr.score DESC
        """), {"period": args.period})
        rows = [
            {
                "employee_id": r[0], "name": r[1],
                "reviewer_id": r[2], "rating": r[3],
            }
            for r in result.fetchall()
        ]
        return ToolResult(data=rows, rows_returned=len(rows))
