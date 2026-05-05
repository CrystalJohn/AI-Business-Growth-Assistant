from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class EmployeeBase(BaseModel):
    employee_code: str
    full_name: str
    email: str
    phone: Optional[str] = None
    birth_date: date
    gender: str
    join_date: date
    job_title: str
    department_id: int
    status: str = "active"


class EmployeeCreate(EmployeeBase):
    citizen_id: Optional[str] = None


class EmployeeRead(EmployeeBase):
    id: int
    department_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeSafe(BaseModel):
    id: int
    employee_code: str
    full_name: str
    email: str
    phone: Optional[str] = None
    citizen_id_masked: Optional[str] = None
    birth_date: date
    gender: str
    join_date: date
    job_title: str
    department_id: int
    department_name: Optional[str] = None
    status: str

    model_config = {"from_attributes": True}
