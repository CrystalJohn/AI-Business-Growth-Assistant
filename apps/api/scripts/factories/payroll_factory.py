from __future__ import annotations

import random
from datetime import date

from faker import Faker

from app.db.models.payroll import Payroll

fake_vn = Faker("vi_VN")

ALLOWANCE_RATIO = 0.10


def make_payroll(employee_id: int, level: str, salary_min: int, salary_max: int) -> Payroll:
    base_salary = round(random.uniform(salary_min, salary_max) / 500_000) * 500_000
    allowance = round(base_salary * ALLOWANCE_RATIO / 500_000) * 500_000
    effective_date = fake_vn.date_between(start_date="-3y", end_date="today")

    return Payroll(
        employee_id=employee_id,
        base_salary=base_salary,
        allowance=allowance,
        effective_date=effective_date,
        level=level,
    )
