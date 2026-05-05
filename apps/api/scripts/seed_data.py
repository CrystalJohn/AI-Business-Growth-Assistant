"""
Entry point: python -m scripts.seed_data
Idempotent — skips seed if departments already exist.
"""
from __future__ import annotations

import asyncio
import random
import sys
import os
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from faker import Faker
from sqlalchemy import text

from app.db.session import AsyncSessionLocal
from app.db.models.attendance import Attendance
from app.db.models.leave_request import LeaveRequest
from app.db.models.performance_review import PerformanceReview
from scripts.factories.employee_factory import (
    DEPARTMENTS,
    make_departments,
    make_employee,
)
from scripts.factories.payroll_factory import make_payroll

fake_vn = Faker("vi_VN")
Faker.seed(42)
random.seed(42)

LEAVE_TYPES = ["Nghỉ phép năm", "Nghỉ ốm", "Nghỉ thai sản", "Nghỉ không lương"]
LEAVE_STATUSES = ["approved", "approved", "approved", "pending", "rejected"]
REVIEW_RATINGS = ["Xuất sắc", "Tốt", "Đạt yêu cầu", "Cần cải thiện"]
REVIEW_PERIODS = ["2023-H1", "2023-H2", "2024-H1", "2024-H2"]
ATTENDANCE_STATUSES = ["present", "present", "present", "present", "absent", "late"]


async def seed() -> None:
    async with AsyncSessionLocal() as session:
        dept_check = await session.execute(
            text("SELECT COUNT(*) FROM departments")
        )
        count = dept_check.scalar_one()
        if count > 0:
            print(f"[seed] Already seeded ({count} departments found). Skipping.")
            return

        print("[seed] Creating 4 departments...")
        departments = make_departments()
        session.add_all(departments)
        await session.flush()

        dept_map = {d.name: d.id for d in departments}
        dept_names = list(dept_map.keys())

        print("[seed] Creating 150 employees + payroll...")
        employees_meta: list[tuple[int, str, int, int]] = []
        for i in range(150):
            dept_name = dept_names[i % len(dept_names)]
            dept_id = dept_map[dept_name]
            emp, level, sal_min, sal_max = make_employee(dept_id, dept_name)
            session.add(emp)
            await session.flush()
            employees_meta.append((emp.id, level, sal_min, sal_max))

            payroll = make_payroll(emp.id, level, sal_min, sal_max)
            session.add(payroll)

        await session.flush()
        emp_ids = [m[0] for m in employees_meta]

        print("[seed] Creating ~4500 attendance records (30 days × 150)...")
        today = date.today()
        for emp_id in emp_ids:
            for day_offset in range(30):
                work_date = today - timedelta(days=day_offset + 1)
                if work_date.weekday() >= 5:
                    continue
                status = random.choices(ATTENDANCE_STATUSES, weights=[70, 70, 70, 70, 5, 15], k=1)[0]
                check_in = check_out = None
                if status in ("present", "late"):
                    hour_in = 8 if status == "present" else random.randint(9, 10)
                    check_in = datetime(
                        work_date.year, work_date.month, work_date.day,
                        hour_in, random.randint(0, 59), tzinfo=timezone.utc
                    )
                    check_out = datetime(
                        work_date.year, work_date.month, work_date.day,
                        17, random.randint(0, 59), tzinfo=timezone.utc
                    )
                session.add(
                    Attendance(
                        employee_id=emp_id,
                        work_date=work_date,
                        check_in=check_in,
                        check_out=check_out,
                        status=status,
                    )
                )

        print("[seed] Creating ~200 leave requests...")
        for _ in range(200):
            emp_id = random.choice(emp_ids)
            start = fake_vn.date_between(start_date="-1y", end_date="today")
            duration = random.randint(1, 5)
            end = start + timedelta(days=duration)
            session.add(
                LeaveRequest(
                    employee_id=emp_id,
                    leave_type=random.choice(LEAVE_TYPES),
                    start_date=start,
                    end_date=end,
                    status=random.choice(LEAVE_STATUSES),
                    reason=fake_vn.sentence(nb_words=8),
                )
            )

        print("[seed] Creating ~300 performance reviews...")
        for _ in range(300):
            emp_id = random.choice(emp_ids)
            score = round(random.uniform(1.0, 5.0), 2)
            if score >= 4.5:
                rating = "Xuất sắc"
            elif score >= 3.5:
                rating = "Tốt"
            elif score >= 2.5:
                rating = "Đạt yêu cầu"
            else:
                rating = "Cần cải thiện"
            session.add(
                PerformanceReview(
                    employee_id=emp_id,
                    period=random.choice(REVIEW_PERIODS),
                    score=score,
                    rating=rating,
                    comment=fake_vn.sentence(nb_words=12),
                )
            )

        await session.commit()
        print("[seed] Done. DB seeded with HR data.")


if __name__ == "__main__":
    asyncio.run(seed())
