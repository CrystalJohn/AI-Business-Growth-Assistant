from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, SoftDeleteMixin

if TYPE_CHECKING:
    from .attendance import Attendance
    from .department import Department
    from .leave_request import LeaveRequest
    from .payroll import Payroll
    from .performance_review import PerformanceReview


class Employee(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    citizen_id: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    join_date: Mapped[date] = mapped_column(Date, nullable=False)
    job_title: Mapped[str] = mapped_column(String(100), nullable=False)
    department_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("departments.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")

    department: Mapped["Department"] = relationship(
        back_populates="employees",
        foreign_keys=[department_id],
    )
    payroll: Mapped[Optional["Payroll"]] = relationship(
        back_populates="employee", uselist=False
    )
    attendance: Mapped[List["Attendance"]] = relationship(back_populates="employee")
    leave_requests: Mapped[List["LeaveRequest"]] = relationship(
        back_populates="employee"
    )
    performance_reviews: Mapped[List["PerformanceReview"]] = relationship(
        back_populates="employee"
    )
