from fastapi import APIRouter

router = APIRouter(tags=["schema"])

DB_SCHEMA = {
    "tables": [
        {
            "name": "departments",
            "description": "Phòng ban (Nhân sự, Kỹ thuật, Kinh doanh, Marketing)",
            "pii_level": "public",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "name", "type": "varchar", "unique": True},
                {"name": "description", "type": "text"},
                {"name": "manager_id", "type": "integer"},
            ],
        },
        {
            "name": "employees",
            "description": "Nhân viên — bảng trung tâm, FK ra mọi bảng khác",
            "pii_level": "medium",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "employee_code", "type": "varchar", "unique": True},
                {"name": "full_name", "type": "varchar", "pii": True},
                {"name": "email", "type": "varchar", "pii": True, "unique": True},
                {"name": "phone", "type": "varchar", "pii": True},
                {"name": "citizen_id", "type": "varchar", "pii": "high"},
                {"name": "birth_date", "type": "date", "pii": True},
                {"name": "gender", "type": "varchar"},
                {"name": "join_date", "type": "date"},
                {"name": "job_title", "type": "varchar"},
                {"name": "department_id", "type": "integer", "fk": "departments.id"},
                {"name": "status", "type": "varchar"},
            ],
        },
        {
            "name": "payroll",
            "description": "Lương cơ bản + phụ cấp theo kỳ hiệu lực",
            "pii_level": "high",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "employee_id", "type": "integer", "fk": "employees.id", "unique": True},
                {"name": "base_salary", "type": "numeric", "pii": "high"},
                {"name": "allowance", "type": "numeric", "pii": "high"},
                {"name": "effective_date", "type": "date"},
                {"name": "level", "type": "varchar"},
            ],
        },
        {
            "name": "attendance",
            "description": "Chấm công hàng ngày — check in/out",
            "pii_level": "low",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "employee_id", "type": "integer", "fk": "employees.id"},
                {"name": "work_date", "type": "date"},
                {"name": "check_in", "type": "timestamptz"},
                {"name": "check_out", "type": "timestamptz"},
                {"name": "status", "type": "varchar"},
            ],
        },
        {
            "name": "leave_requests",
            "description": "Đơn nghỉ phép — loại nghỉ, ngày, trạng thái",
            "pii_level": "low",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "employee_id", "type": "integer", "fk": "employees.id"},
                {"name": "leave_type", "type": "varchar"},
                {"name": "start_date", "type": "date"},
                {"name": "end_date", "type": "date"},
                {"name": "status", "type": "varchar"},
                {"name": "reason", "type": "text"},
            ],
        },
        {
            "name": "performance_reviews",
            "description": "Đánh giá hiệu suất — kỳ, điểm, nhận xét",
            "pii_level": "medium",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "employee_id", "type": "integer", "fk": "employees.id"},
                {"name": "period", "type": "varchar"},
                {"name": "score", "type": "numeric"},
                {"name": "rating", "type": "varchar"},
                {"name": "comment", "type": "text", "pii": True},
                {"name": "reviewer_id", "type": "integer"},
            ],
        },
        {
            "name": "audit_log",
            "description": "Ghi mọi LLM query và action của user",
            "pii_level": "internal",
            "columns": [
                {"name": "id", "type": "integer", "pk": True},
                {"name": "table_name", "type": "varchar"},
                {"name": "action", "type": "varchar"},
                {"name": "query_text", "type": "text"},
                {"name": "user_id", "type": "integer"},
                {"name": "ip_address", "type": "varchar"},
                {"name": "timestamp", "type": "timestamptz"},
            ],
        },
    ],
    "views": [
        {
            "name": "v_employee_safe",
            "description": "Employees với citizen_id được mask (XXX***XXX)",
            "exposed_to_llm": True,
            "base_table": "employees",
        },
        {
            "name": "v_payroll_anonymized",
            "description": "Payroll với salary_band thay vì lương cụ thể",
            "exposed_to_llm": True,
            "base_table": "payroll",
        },
    ],
}


@router.get("/schema")
def get_schema():
    return DB_SCHEMA
