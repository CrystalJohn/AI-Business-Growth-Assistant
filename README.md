# AI Business Growth Assistant

A web-based **AI ChatBI** application that helps non-technical business users ask questions about their business data in plain language and receive answers, SQL queries, interactive tables, and charts.

> **Status**: Boilerplate — LLM is mocked. No paid API key required.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14, TypeScript, Tailwind CSS, shadcn/ui |
| Data Display | TanStack Table v8, Recharts |
| Backend | FastAPI, Pydantic v2 |
| Database | PostgreSQL 16 |
| SQL Validation | sqlglot (structure prepared) |
| LLM | Mock provider → Gemini Flash / Groq (pluggable) |

---

## Quick Start (Docker)

```bash
# 1. Copy environment variables
cp .env.example .env

# 2. Start everything
docker-compose up -d

# 3. Open the app
#   Frontend : http://localhost:3000
#   API docs : http://localhost:8000/docs
```

PostgreSQL schema and seed data are auto-loaded on first start.

---

## Local Development (without Docker)

### Backend

```bash
cd apps/api
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../../.env.example .env     # edit DATABASE_URL to point to your local PG
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd apps/web
npm install
cp .env.local.example .env.local
npm run dev
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service health check |
| `GET` | `/schema` | Returns DB table/column metadata |
| `POST` | `/chat/query` | Natural language → SQL + results |
| `POST` | `/sql/validate` | Validate & format a SQL string |

### POST `/chat/query`

```json
// Request
{ "question": "What are the top 5 products by revenue?" }

// Response
{
  "answer": "...",
  "sql": "SELECT ...",
  "columns": [{ "key": "product", "label": "Product", "type": "string" }, ...],
  "rows": [...],
  "chartType": "bar",
  "followUpQuestions": ["Which segment buys these products most?", ...]
}
```

---

## Project Structure

```
ai-business-growth-assistant/
├── apps/
│   ├── web/                   # Next.js 14 (App Router)
│   │   ├── app/               # Pages & layouts
│   │   ├── components/        # Chat, Results, UI primitives
│   │   ├── lib/               # API client, utils
│   │   └── types/             # Shared TypeScript types
│   └── api/                   # FastAPI
│       ├── main.py
│       └── app/
│           ├── config.py
│           ├── models.py
│           ├── routes/        # health, schema, chat, sql
│           └── services/      # mock_llm, sql_validator
├── database/
│   ├── schema.sql             # 7-table schema
│   └── seeds/seed.sql         # Demo data
├── docs/
│   ├── flowchart.md
│   └── erd.md
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Database Schema

| Table | Description |
|---|---|
| `customer_segments` | Segment definitions (Enterprise, SMB, …) |
| `customers` | Customer records linked to segments |
| `products` | Product catalog with pricing |
| `orders` | Order headers |
| `order_items` | Line items per order |
| `campaigns` | Marketing campaigns with budget/spend |
| `leads` | Lead pipeline with source and status |

---

## Extending

### Plug in a real LLM

1. Set `LLM_PROVIDER=gemini` or `LLM_PROVIDER=groq` in `.env`
2. Add your key (`GEMINI_API_KEY` / `GROQ_API_KEY`)
3. Implement `apps/api/app/services/llm_provider.py` following the interface in `mock_llm.py`

### Add new routes

Drop a new file in `apps/api/app/routes/` and register it in `main.py`.

### Add new frontend pages

Create a folder under `apps/web/app/` following Next.js App Router conventions.
