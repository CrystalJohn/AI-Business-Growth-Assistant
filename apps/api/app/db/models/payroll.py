from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, SoftDeleteMixin

if TYPE_CHECKING:
    from .employee import Employee


class Payroll(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "payroll"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id"), unique=True, nullable=False
    )
    base_salary: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    allowance: Mapped[float] = mapped_column(
        Numeric(15, 2), nullable=False, default=0
    )
    effective_date: Mapped[date] = mapped_column(Date, nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)

    employee: Mapped["Employee"] = relationship(back_populates="payroll")
