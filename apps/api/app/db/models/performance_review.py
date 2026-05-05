from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import AuditMixin, Base, SoftDeleteMixin

if TYPE_CHECKING:
    from .employee import Employee


class PerformanceReview(Base, AuditMixin, SoftDeleteMixin):
    __tablename__ = "performance_reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employee_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("employees.id"), nullable=False
    )
    period: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float] = mapped_column(Numeric(4, 2), nullable=False)
    rating: Mapped[str] = mapped_column(String(20), nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    reviewer_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    employee: Mapped["Employee"] = relationship(back_populates="performance_reviews")
