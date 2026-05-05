from __future__ import annotations

import random
from datetime import date
from typing import List

from faker import Faker

from app.db.models.department import Department
from app.db.models.employee import Employee

fake_vn = Faker("vi_VN")
Faker.seed(42)
random.seed(42)

DEPARTMENTS = [
    {"name": "Nhân sự", "description": "Quản lý nhân sự và tuyển dụng"},
    {"name": "Kỹ thuật", "description": "Phát triển sản phẩm và hạ tầng kỹ thuật"},
    {"name": "Kinh doanh", "description": "Bán hàng và phát triển thị trường"},
    {"name": "Marketing", "description": "Truyền thông và xây dựng thương hiệu"},
]

JOB_LEVELS = [
    ("Junior", 8_000_000, 15_000_000),
    ("Senior", 15_000_000, 30_000_000),
    ("Lead", 30_000_000, 50_000_000),
    ("Manager", 40_000_000, 80_000_000),
]

LEVEL_WEIGHTS = [40, 35, 15, 10]

JOB_TITLES_BY_DEPT = {
    "Nhân sự": [
        "Chuyên viên tuyển dụng",
        "Chuyên viên C&B",
        "Trưởng phòng nhân sự",
        "Giám đốc nhân sự",
        "Chuyên viên đào tạo",
    ],
    "Kỹ thuật": [
        "Lập trình viên Backend",
        "Lập trình viên Frontend",
        "Kỹ sư DevOps",
        "Kỹ sư dữ liệu",
        "Kiến trúc sư hệ thống",
        "Trưởng nhóm kỹ thuật",
    ],
    "Kinh doanh": [
        "Chuyên viên kinh doanh",
        "Quản lý tài khoản",
        "Giám đốc kinh doanh khu vực",
        "Chuyên viên phát triển đối tác",
        "Trưởng phòng kinh doanh",
    ],
    "Marketing": [
        "Chuyên viên marketing",
        "Chuyên viên nội dung",
        "Chuyên viên SEO/SEM",
        "Giám đốc marketing",
        "Chuyên viên thiết kế sáng tạo",
    ],
}


def make_departments() -> List[Department]:
    return [
        Department(name=d["name"], description=d["description"])
        for d in DEPARTMENTS
    ]


def make_employee(dept_id: int, dept_name: str) -> Employee:
    gender = "M" if random.random() < 0.60 else "F"
    level, salary_min, salary_max = random.choices(JOB_LEVELS, weights=LEVEL_WEIGHTS, k=1)[0]
    titles = JOB_TITLES_BY_DEPT.get(dept_name, ["Nhân viên"])
    job_title = random.choice(titles)

    if gender == "M":
        full_name = fake_vn.name_male()
    else:
        full_name = fake_vn.name_female()

    birth_date = fake_vn.date_of_birth(minimum_age=22, maximum_age=55)
    join_date = fake_vn.date_between(start_date="-5y", end_date="today")

    return Employee(
        employee_code=f"EMP{fake_vn.unique.numerify('####')}",
        full_name=full_name,
        email=fake_vn.unique.email(),
        phone=fake_vn.phone_number(),
        citizen_id=fake_vn.numerify("############"),
        birth_date=birth_date,
        gender=gender,
        join_date=join_date,
        job_title=job_title,
        department_id=dept_id,
        status="active",
    ), level, salary_min, salary_max
