from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.schemas import CurrentUser

ROLE_HIERARCHY = {
    "HR_Manager": 4,
    "Dept_Manager": 3,
    "HR_Staff": 2,
    "Viewer": 1,
}


@dataclass
class ToolResult:
    data: list[dict[str, Any]] | dict[str, Any]
    rows_returned: int
    sql_debug: str | None = None
    chart_type: str | None = None


class ToolBase(ABC):
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    required_role: str | None = None
    allowed_roles: list[str] | None = None

    def check_access(self, user: CurrentUser) -> None:
        if self.allowed_roles:
            if user.role not in self.allowed_roles:
                raise PermissionError(
                    f"Tool {self.name} requires one of: {', '.join(self.allowed_roles)}"
                )
            return

        if self.required_role:
            user_level = ROLE_HIERARCHY.get(user.role, 0)
            required_level = ROLE_HIERARCHY.get(self.required_role, 0)
            if user_level < required_level:
                raise PermissionError(
                    f"Tool {self.name} requires {self.required_role} or higher"
                )

    @abstractmethod
    async def execute(
        self, session: AsyncSession, user: CurrentUser, args: BaseModel
    ) -> ToolResult:
        ...
