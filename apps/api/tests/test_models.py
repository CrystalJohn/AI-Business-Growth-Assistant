"""Smoke tests — schema integrity and basic ORM operations."""
from datetime import date

import pytest
import pytest_asyncio
from sqlalchemy import select, text

from app.db.models.department import Department
from app.db.models.employee import Employee
from app.db.models.payroll import Payroll


@pytest.mark.asyncio
async def test_create_department(db_session):
    dept = Department(name="Test Dept", description="For testing")
    db_session.add(dept)
    await db_session.flush()
    assert dept.id is not None
    assert dept.created_at is not None


@pytest.mark.asyncio
async def test_create_employee_with_fk(db_session):
    dept = Department(name="Engineering Test", description="Dev team")
    db_session.add(dept)
    await db_session.flush()

    emp = Employee(
        employee_code="EMP9001",
        full_name="Nguyễn Văn A",
        email="nguyenvana@test.com",
        birth_date=date(1990, 1, 1),
        gender="M",
        join_date=date(2022, 3, 1),
        job_title="Lập trình viên",
        department_id=dept.id,
    )
    db_session.add(emp)
    await db_session.flush()
    assert emp.id is not None
    assert emp.department_id == dept.id


@pytest.mark.asyncio
async def test_payroll_fk_integrity(db_session):
    dept = Department(name="HR Test", description="HR team")
    db_session.add(dept)
    await db_session.flush()

    emp = Employee(
        employee_code="EMP9002",
        full_name="Trần Thị B",
        email="tranthib@test.com",
        birth_date=date(1995, 6, 15),
        gender="F",
        join_date=date(2023, 1, 10),
        job_title="Chuyên viên nhân sự",
        department_id=dept.id,
    )
    db_session.add(emp)
    await db_session.flush()

    payroll = Payroll(
        employee_id=emp.id,
        base_salary=20_000_000,
        allowance=2_000_000,
        effective_date=date(2023, 1, 10),
        level="Junior",
    )
    db_session.add(payroll)
    await db_session.flush()
    assert payroll.id is not None
    assert payroll.employee_id == emp.id


@pytest.mark.asyncio
async def test_soft_delete_mixin(db_session):
    from datetime import datetime, timezone

    dept = Department(name="Temp Dept", description="Will be soft deleted")
    db_session.add(dept)
    await db_session.flush()

    dept.deleted_at = datetime.now(timezone.utc)
    db_session.add(dept)
    await db_session.flush()

    stmt = select(Department).where(
        Department.id == dept.id, Department.deleted_at.is_(None)
    )
    result = await db_session.execute(stmt)
    assert result.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_audit_columns_auto_set(db_session):
    dept = Department(name="Audit Check Dept")
    db_session.add(dept)
    await db_session.flush()
    assert dept.created_at is not None
    assert dept.updated_at is not None
