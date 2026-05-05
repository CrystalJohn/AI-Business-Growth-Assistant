# HR ChatBI — AI-Powered HR Analytics Assistant

A **secure AI ChatBI** application for HR Managers at Vietnamese SMB companies (~80–200 employees). Ask HR questions in plain language and receive answers, SQL queries, charts and tables — with PII masking and audit trail built in.

> **Status**: Week 1 — Foundation. LLM is mocked. No paid API key required.  
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
│       └── 002_views_and_audit.py     # audit_log + SQL views + role
├── app/
│   ├── config.py              # Settings (JWT, PII masking keys)
│   ├── db/
│   │   ├── base.py            # Base, AuditMixin, SoftDeleteMixin
│   │   ├── session.py         # async_engine, get_db() dependency
│   │   └── models/            # 7 SQLAlchemy ORM models
│   ├── repositories/          # Repository Pattern (BaseRepository[T])
│   ├── schemas/               # Pydantic DTOs (query, employee)
│   ├── routes/                # FastAPI routers
│   └── services/              # Business logic + LLM mock
├── scripts/
│   ├── seed_data.py           # Idempotent seed entry point
│   └── factories/             # Faker vi_VN factories
├── tests/
│   ├── conftest.py            # Test DB fixtures
│   └── test_models.py         # Schema smoke tests
└── requirements.txt
database/
├── schema.sql                 # Legacy reference — Alembic is now source of truth
└── seeds/seed.sql             # Legacy reference — replaced by scripts/seed_data.py
docs/
├── adr/                       # Architecture Decision Records
│   ├── ADR-001-choose-alembic.md
│   ├── ADR-002-layered-architecture.md
│   └── ADR-003-soft-delete-audit.md
├── erd.md                     # HR domain ERD (7 tables, Mermaid)
├── flowchart.md               # 5-layer security architecture flow
└── 03-week1-dev-log.md        # Week 1 retrospective + DoD checklist
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
