# Entity Relationship Diagram — HR Domain

ERD của HR ChatBI assistant cho persona HR Manager công ty SMB Việt Nam (~80-200 người). Schema được viết bằng SQLAlchemy 2.0 ORM tại `apps/api/app/db/models/` và là **source of truth**. Tài liệu này phản ánh chính xác code hiện tại.

---

## 1. Tổng quan

| Bảng | Mục đích | PII Level | Mixin |
|---|---|---|---|
| `departments` | Phòng ban (Nhân sự, Kỹ thuật, Kinh doanh, Marketing) | Public | Audit + SoftDelete |
| `employees` | Nhân viên — bảng trung tâm, FK ra mọi bảng khác | **Medium-High** | Audit + SoftDelete |
| `payroll` | Lương cơ bản + phụ cấp theo kỳ hiệu lực | **High** | Audit + SoftDelete |
| `attendance` | Chấm công hàng ngày | Low | Audit + SoftDelete |
| `leave_requests` | Đơn nghỉ phép | Low | Audit + SoftDelete |
| `performance_reviews` | Đánh giá hiệu suất theo kỳ (Q1/Q2/...) | Medium | Audit + SoftDelete |
| `audit_log` | Ghi mọi action LLM/user thực hiện | Internal | — (immutable) |

> **Quy ước Mixin** (xem `apps/api/app/db/base.py`):
> - `AuditMixin` → cột `created_at`, `updated_at`, `created_by`
> - `SoftDeleteMixin` → cột `deleted_at` + classmethod `active()` để filter

---

## 2. ERD

```mermaid
erDiagram
    departments {
        int id PK
        varchar name
        text description
        int manager_id
        timestamptz created_at
        timestamptz updated_at
        int created_by
        timestamptz deleted_at
    }

    employees {
        int id PK
        varchar employee_code UK
        varchar full_name
        varchar email UK
        varchar phone
        varchar citizen_id
        date birth_date
        varchar gender
        date join_date
        varchar job_title
        int department_id FK
        varchar status
        timestamptz created_at
        timestamptz updated_at
        int created_by
        timestamptz deleted_at
    }

    payroll {
        int id PK
        int employee_id FK UK
        numeric base_salary
        numeric allowance
        date effective_date
        varchar level
        timestamptz created_at
        timestamptz updated_at
        int created_by
        timestamptz deleted_at
    }

    attendance {
        int id PK
        int employee_id FK
        date work_date
        timestamptz check_in
        timestamptz check_out
        varchar status
        timestamptz created_at
        timestamptz updated_at
        int created_by
        timestamptz deleted_at
    }

    leave_requests {
        int id PK
        int employee_id FK
        varchar leave_type
        date start_date
        date end_date
        varchar status
        text reason
        timestamptz created_at
        timestamptz updated_at
        int created_by
        timestamptz deleted_at
    }

    performance_reviews {
        int id PK
        int employee_id FK
        varchar period
        numeric score
        varchar rating
        text comment
        int reviewer_id
        timestamptz created_at
        timestamptz updated_at
        int created_by
        timestamptz deleted_at
    }

    audit_log {
        int id PK
        varchar table_name
        varchar action
        text query_text
        int user_id
        varchar ip_address
        timestamptz timestamp
    }

    departments ||--o{ employees : "has"
    employees   ||--|| payroll   : "has"
    employees   ||--o{ attendance : "records"
    employees   ||--o{ leave_requests : "submits"
    employees   ||--o{ performance_reviews : "receives"
```

---

## 3. PII Classification & Masking Rules

Bảng phân loại để chuẩn bị cho **Layer 5 (PII Masking)** ở Week 6:

| Column | Bảng | Level | HR_Manager | HR_Staff (cùng phòng) | HR_Staff (khác phòng) |
|---|---|---|---|---|---|
| `citizen_id` | employees | **HIGH** | full | last 4 digits | masked `XXX-XXX-XXXX` |
| `base_salary` | payroll | **HIGH** | full | masked `***` | masked `***` |
| `allowance` | payroll | **HIGH** | full | masked `***` | masked `***` |
| `birth_date` | employees | Medium | full | day/month only | day/month only |
| `comment` | performance_reviews | Medium | full | redacted | hidden |
| `phone` | employees | Medium | full | full | full (HR cần liên hệ) |
| `email` | employees | Low | full | full | full |
| `full_name` | employees | Low | full | full | full |

---

## 4. Key Relationships

| Relationship | Cardinality | Notes |
|---|---|---|
| `departments` → `employees` | 1:N | Mỗi nhân viên thuộc 1 phòng ban |
| `employees` → `payroll` | **1:1** | `payroll.employee_id` UNIQUE |
| `employees` → `attendance` | 1:N | Mỗi ngày 1 record |
| `employees` → `leave_requests` | 1:N | Nhân viên có nhiều đơn nghỉ phép |
| `employees` → `performance_reviews` | 1:N | Nhiều kỳ đánh giá theo `period` |

---

## 5. Analytics Queries Enabled

10 use case HR Manager hỏi (mapping → bảng):

| Câu hỏi | Bảng tham gia | Pattern |
|---|---|---|
| "Tổng headcount theo phòng ban?" | `employees + departments` | Tool: `get_headcount_by_department` |
| "Ai sắp hết phép năm nay?" | `leave_requests + employees` | Tool: `get_leave_balance` |
| "Turnover rate Q3 vs Q2?" | `employees` (status, deleted_at) | Constrained SQL |
| "Sinh nhật tháng này?" | `employees.birth_date` | Tool: `get_birthdays_this_month` |
| "Lương trung bình theo level?" | `payroll` | Tool: `get_salary_by_level` (mask cho Staff) |
| "Top 10 thâm niên?" | `employees.join_date` | Tool: `get_top_tenure` |
| "Phân bố độ tuổi?" | `employees.birth_date` | Tool: `get_age_distribution` |
| "Performance review chưa hoàn thành?" | `performance_reviews + employees` | Tool: `get_pending_reviews` |
| "Đi muộn tuần này?" | `attendance.status='late'` | Constrained SQL |
| "Phép năm còn lại?" | `leave_requests + employees` | Tool: `get_leave_balance` |

---

## 6. Pending Extensions (Week 2-3)

ERD sẽ mở rộng khi triển khai security layer:

| Bảng | Field sẽ thêm | Lý do |
|---|---|---|
| `audit_log` | `mode`, `tool_name`, `sql_executed`, `args` (JSONB), `rows_returned`, `duration_ms`, `status`, `blocked_reason`, `role` | Phục vụ research RQ2/RQ3 — track chi tiết LLM action |
| `employees` | `manager_id` (FK self-ref) | Hỗ trợ org chart, line manager queries |
| `employees` | `termination_date` | Phục vụ turnover analysis |
| Views `v_*` | `v_employee_safe`, `v_payroll_anonymized`, `v_performance_redacted` | LLM chỉ thấy views, không thấy raw tables |

> Mọi thay đổi schema sẽ qua **Alembic migration** (xem `docs/03-week1-dev-log.md`).
