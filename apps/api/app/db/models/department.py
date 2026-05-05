from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, SoftDeleteMixin

if TYPE_CHECKING:
    from .employee import Employee


class Department(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    manager_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    employees: Mapped[List["Employee"]] = relationship(
        back_populates="department",
        foreign_keys="Employee.department_id",
    )
