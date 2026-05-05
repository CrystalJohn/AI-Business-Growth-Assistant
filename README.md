# HR ChatBI — AI-Powered HR Analytics Assistant

A **secure AI ChatBI** application for HR Managers at Vietnamese SMB companies (~80–200 employees). Ask HR questions in plain language and receive answers, SQL queries, charts and tables — with PII masking and audit trail built in.

> **Status**: Week 3 — Tool Layer. 15 tools active. LLM is mocked.  
> **Domain**: HR (nhân viên, lương, chấm công, nghỉ phép, đánh giá hiệu suất)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| Data Display | TanStack Table v8, Recharts |
| Backend | FastAPI, Pydantic v2, SQLAlchemy 2.0 (async) |
| DB Migrations | Alembic 1.13 |
| Database | PostgreSQL 16 |
| Seed Data | Faker `vi_VN` — 150 Vietnamese employees |
| SQL Validation | sqlglot |
| LLM | Mock provider → Gemini Flash / Groq (pluggable, Week 3+) |

---

## Quick Start (Docker)

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Start everything — runs Alembic migrations + seed automatically
docker-compose up -d

# 3. Open the app
#   Frontend : http://localhost:3000
#   API docs : http://localhost:8000/docs
#   Health   : http://localhost:8000/health
```

On first start the API container runs:
1. `alembic upgrade head` — creates 7 HR tables + SQL views
2. `python -m scripts.seed_data` — seeds 150 Vietnamese employees (idempotent)
3. `uvicorn main:app --reload`

---

## Local Development (without Docker)

### Backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example .env     # edit DATABASE_URL to point to your local PG

# Run migrations
alembic upgrade head

# Seed data
python -m scripts.seed_data

# Start API
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd apps/web
npm install
cp .env.local.example .env.local
npm run dev
```

### Tests

```bash
cd apps/api
# set TEST_DATABASE_URL in .env or export it
pytest tests/test_models.py -v
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health + DB connectivity check |
| `GET` | `/schema` | Returns DB table/column metadata |
| `POST` | `/chat/query` | Natural language → SQL + results |
| `POST` | `/sql/validate` | Validate & format a SQL string |

---

## Project Structure

```
apps/api/
├── alembic/                   # DB migrations (source of truth)
│   └── versions/
│       ├── 001_initial_hr_schema.py   # 6 HR tables
│       ├── 002_views_and_audit.py     # audit_log + SQL views + role
│       ├── 003_extend_audit_log.py    # audit_log + 13 security columns
│       └── 004_rls_policies.py        # RLS policies + GRANT
├── app/
│   ├── config.py              # Settings (JWT, PII masking keys)
│   ├── db/
│   │   ├── base.py            # Base, AuditMixin, SoftDeleteMixin
│   │   ├── session.py         # async_engine, get_db(), get_db_with_rls()
│   │   └── models/            # 7 SQLAlchemy ORM models
│   ├── dependencies/          # FastAPI dependencies
│   │   └── mock_user.py       # Mock user (Week 6 → JWT)
│   ├── middleware/
│   │   └── db_context.py      # set_rls_context() — SET LOCAL vars
│   ├── repositories/          # Repository Pattern
│   │   ├── base.py            # BaseRepository[T]
│   │   ├── employee_repo.py   # EmployeeRepository
│   │   └── audit_repo.py      # AuditRepository.log_query()
│   ├── schemas/               # Pydantic DTOs (query, employee)
│   ├── routes/                # FastAPI routers
│   │   ├── health.py
│   │   ├── chat.py
│   │   ├── tools.py           # GET /tools, POST /tools/{name}
│   │   ├── schema_route.py
│   │   └── sql_route.py
│   ├── services/              # Business logic + LLM mock
│   │   └── audit_decorator.py # @audited decorator
│   └── tools/                 # 15 tool catalog
│       ├── base.py            # ToolBase, ToolResult
│       ├── registry.py        # REGISTRY dict
│       └── *.py               # 15 tool implementations
├── scripts/
│   ├── seed_data.py           # Idempotent seed entry point
│   └── factories/             # Faker vi_VN factories
├── tests/
│   ├── conftest.py            # Test DB fixtures
│   ├── test_models.py         # Schema smoke tests
│   ├── test_rls.py            # RLS policy tests (8 tests)
│   ├── test_audit_repo.py     # AuditRepository tests (4 tests)
│   └── test_tools/            # Tool layer tests
│       ├── test_tool_registry.py    # Registry + RBAC tests (10 tests)
│       └── test_tool_integration.py # Integration tests (8 tests)
└── requirements.txt
```

---

## HR Database Schema (7 tables)

| Table | Description | PII Level |
|---|---|---|
| `departments` | Nhân sự / Kỹ thuật / Kinh doanh / Marketing | Public |
| `employees` | Nhân viên — tên, email, CCCD, chức danh | **Medium** |
| `payroll` | Lương cơ bản + phụ cấp theo kỳ | **High** |
| `attendance` | Chấm công hàng ngày | Low |
| `leave_requests` | Đơn nghỉ phép | Low |
| `performance_reviews` | Đánh giá hiệu suất theo kỳ | Medium |
| `audit_log` | Ghi mọi LLM query + action | Internal |

**SQL Views (security skeleton):**
- `v_employee_safe` — masks `citizen_id`
- `v_payroll_anonymized` — replaces salary with band labels
- `hr_chatbi_readonly` — Postgres role with SELECT-only on views

---

## Security Layers (Implemented)

| Layer | Status | Notes |
|---|---|---|
| L1 — Auth | 🟡 Mock | `get_mock_user()` → JWT real Week 6 |
| L2 — LLM Router | 🔴 Not started | Week 4 |
| L3 — Tool Layer | 🔴 Not started | Week 3 |
| L3b — SQL Validator | 🔴 Not started | Week 5 |
| L4 — RLS + Postgres | ✅ Done | 6 tables, 17 policies, `SET LOCAL` context |
| L5 — Audit | ✅ Done | `AuditRepository.log_query()`, append-only |

**RLS Policy Summary:**
- `employees`: HR_Manager sees all, HR_Staff sees own dept only
- `payroll`: HR_Manager only (HR_Staff blocked completely)
- `attendance`, `leave_requests`, `performance_reviews`: Manager all, Staff same dept
- Default deny: unknown role → 0 rows on all tables

---

## Tool Catalog (15 tools)

| Cluster | Tool | RBAC |
|---|---|---|
| Headcount | `get_headcount_by_department`, `get_age_distribution`, `get_gender_distribution` | Any |
| Search | `search_employees`, `get_employee_detail`, `list_tenure_top_n` | RLS-filtered |
| Compensation | `get_avg_salary_by_level`, `get_payroll_summary_by_month` | Manager only |
| Leave/Attend | `get_leave_balance`, `list_leaves_expiring_year_end`, `get_attendance_summary` | RLS-filtered |
| Performance | `list_pending_performance_reviews`, `list_birthdays_this_month` | RLS-filtered |
| Trends | `get_turnover_rate`, `list_contracts_expiring_soon` | Manager only |

Explore: `GET /tools` returns full catalog with Pydantic JSON Schema.  
Execute: `POST /tools/{name}` with JSON body matching input schema.

---

## Alembic Cheatsheet

```bash
cd apps/api

# Apply all migrations
alembic upgrade head

# Rollback one step
alembic downgrade -1

# Check current revision
alembic current

# Generate new migration (after model change)
alembic revision --autogenerate -m "describe change"
```

---

## Extending

### Plug in a real LLM

1. Set `LLM_PROVIDER=gemini` or `LLM_PROVIDER=groq` in `.env`
2. Add your key (`GEMINI_API_KEY` / `GROQ_API_KEY`)
3. Implement `apps/api/app/services/llm_provider.py` following the interface in `mock_llm.py`

### Add a new migration

```bash
# Edit a model, then:
alembic revision --autogenerate -m "add column X to employees"
alembic upgrade head
```

### Add new routes

Drop a new file in `apps/api/app/routes/` and register it in `main.py`.
