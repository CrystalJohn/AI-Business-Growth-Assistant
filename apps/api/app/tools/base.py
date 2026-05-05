from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.mock_user import MockUser


@dataclass
class ToolResult:
    data: list[dict[str, Any]] | dict[str, Any]
    rows_returned: int
    sql_debug: str | None = None
    chart_type: str | None = None  # "bar"|"pie"|"line"|None


class ToolBase(ABC):
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    required_role: str | None = None  # "HR_Manager" | None (any role)

    def check_access(self, user: MockUser) -> None:
        if self.required_role and user.role != self.required_role:
            raise PermissionError(
                f"Tool {self.name} requires role {self.required_role}"
            )

    @abstractmethod
    async def execute(
        self, session: AsyncSession, user: MockUser, args: BaseModel
    ) -> ToolResult:
        ...
