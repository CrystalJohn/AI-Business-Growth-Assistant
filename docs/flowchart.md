# Application Flowchart — HR ChatBI Architecture

Sơ đồ luồng cho HR ChatBI Assistant. Phản ánh kiến trúc 5-layer security đã chốt trong `01-project-scope.md`. Mỗi câu hỏi của user đi qua đầy đủ 5 layer trước khi trả về kết quả.

---

## 1. Request Flow (End-to-End)

```mermaid
flowchart TD
    U([HR Manager / HR Staff<br/>nhập câu hỏi]) --> FE

    subgraph Frontend [Frontend - Next.js 14]
        FE[ChatPanel] --> QI[QuestionInput<br/>+ JWT từ localStorage]
        QI --> POST[POST /chat/query<br/>Authorization: Bearer ...]
    end

    POST --> AUTH

    subgraph Backend [Backend - FastAPI]
        AUTH{Layer 1<br/>JWT Auth + RBAC}
        AUTH -->|invalid| UNAUTH([401 Unauthorized])
        AUTH -->|valid: user, role, dept| ROUTER

        ROUTER[Layer 2<br/>LLM Router<br/>Gemini Flash]
        ROUTER --> DECIDE{Tool match?}
        DECIDE -->|yes| TOOL
        DECIDE -->|no| SQL

        TOOL[Layer 3a<br/>Tool Layer<br/>10-15 parameterized tools]
        SQL[Layer 3b<br/>Constrained Text-to-SQL<br/>chỉ thấy v_* Views]

        SQL --> AST{sqlglot AST<br/>Validator}
        AST -->|invalid| BLOCK[Block + log<br/>blocked_reason]
        AST -->|valid| EXEC

        TOOL --> EXEC[Execute on Postgres]
    end

    EXEC --> PG

    subgraph Database [Database - PostgreSQL]
        PG[(Postgres<br/>readonly role<br/>RLS active<br/>timeout 5s)]
        VIEWS[v_employee_safe<br/>v_payroll_anonymized<br/>v_performance_redacted]
        RAW[Raw tables<br/>NO direct LLM access]
        PG --- VIEWS
        PG --- RAW
    end

    PG --> RESULT[Raw rows]
    RESULT --> MASK[Layer 4<br/>PII Masking<br/>theo role + dept]
    MASK --> AUDIT[Layer 5<br/>Audit Log INSERT]
    AUDIT --> RESP[QueryResponse JSON]
    BLOCK --> AUDIT

    RESP --> RB[ResultBlock Tabs]
    RB -->|Answer/Table/Chart/SQL| U
```

---

## 2. Security Layers — Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor U as HR User
    participant FE as Next.js
    participant API as FastAPI
    participant LLM as LLM Router<br/>(Gemini Flash)
    participant V as Validator<br/>(sqlglot)
    participant PG as Postgres<br/>(readonly + RLS)
    participant A as audit_log

    U->>FE: Câu hỏi + JWT
    FE->>API: POST /chat/query

    rect rgb(240, 248, 255)
    Note right of API: Layer 1 — Auth + RBAC
    API->>API: Decode JWT → user, role, dept
    API->>API: Set session: app.current_user_id, role, dept
    end

    rect rgb(245, 245, 220)
    Note right of API: Layer 2 — LLM Router
    API->>LLM: Question + tool catalog + view schema
    LLM-->>API: {mode: tool|sql, payload}
    end

    alt mode = tool
        rect rgb(220, 255, 220)
        Note right of API: Layer 3a — Tool execution
        API->>V: Validate tool args (Pydantic)
        V-->>API: ok / validation error
        end
    else mode = sql
        rect rgb(255, 240, 220)
        Note right of API: Layer 3b — Constrained SQL
        API->>V: AST whitelist + LIMIT + tables check
        V-->>API: blocked_reason (if invalid)
        end
    end

    rect rgb(230, 230, 255)
    Note right of API: Layer 4 — DB execution
    API->>PG: SELECT (readonly user, RLS, timeout 5s)
    PG-->>API: rows
    end

    rect rgb(255, 230, 230)
    Note right of API: Layer 5 — Mask + Audit
    API->>API: Mask PII theo role
    API->>A: INSERT audit_log
    end

    API-->>FE: response (masked)
    FE-->>U: Render ResultBlock
```

---

## 3. LLM Router Decision Tree

```mermaid
flowchart TD
    Q[User question] --> LLM[LLM Router<br/>Gemini Flash]
    LLM --> CAT[Match against<br/>tool catalog 10-15 tools]

    CAT --> M1{Matches a tool<br/>with high confidence?}
    M1 -->|yes ≥0.8| T[mode = tool<br/>return tool_name + args]
    M1 -->|no| GEN

    GEN[Generate SQL<br/>using v_* views only] --> M2{SQL valid<br/>against schema?}
    M2 -->|yes| S[mode = sql<br/>return query]
    M2 -->|no| FB[mode = error<br/>fallback message]

    T --> EXE([Execute via Tool Layer])
    S --> EXE2([Execute via Constrained SQL])
    FB --> RESP([Trả về 'Tôi không hiểu câu hỏi'])
```

---

## 4. SQL Validation Flow (chi tiết Layer 3b)

```mermaid
flowchart LR
    SQL[SQL từ LLM] --> P{sqlglot.parse}
    P -->|fail| E1[Block: cannot parse]

    P -->|ok| T{Chỉ SELECT?}
    T -->|no| E2[Block: only SELECT allowed]

    T -->|yes| W{Tables ⊆<br/>whitelist v_*?}
    W -->|no| E3[Block: forbidden table]

    W -->|yes| L{LIMIT ≤ 1000?}
    L -->|no| L2[Inject LIMIT 1000]
    L -->|yes| OK
    L2 --> OK[Pass to executor]
```

---

## 5. Frontend Component Tree

```
ChatPage (Server Component)
└── AuthGuard (verify JWT, redirect /login if absent)
    └── ChatPageClient (Client — reads ?q= param + auth context)
        └── ChatPanel (Client — owns state)
            ├── RoleBadge              (HR_Manager / HR_Staff indicator)
            ├── SuggestedQuestions     (HR-specific: headcount, leave, salary…)
            ├── MessageList
            │   ├── UserBubble
            │   └── AssistantMessage
            │       ├── LoadingSteps          (while fetching)
            │       ├── BlockedQueryNotice    (if Layer 3b blocked → show reason)
            │       └── ResultBlock
            │           ├── Tabs
            │           │   ├── Answer tab
            │           │   ├── Table tab → ResultTable (TanStack)
            │           │   ├── Chart tab → ResultChart (Recharts)
            │           │   └── SQL tab   → SqlViewer
            │           ├── PIIMaskedBadge    (nếu có cột bị mask)
            │           └── FollowUpQuestions
            └── QuestionInput
```

---

## 6. Audit Log Flow

Mọi action — kể cả failed/blocked — đều ghi vào `audit_log`:

```mermaid
flowchart LR
    A[Bất kỳ action] --> B{Outcome}
    B -->|success| L1[INSERT status='success'<br/>+ rows_returned + duration_ms]
    B -->|blocked| L2[INSERT status='blocked'<br/>+ blocked_reason]
    B -->|error| L3[INSERT status='error'<br/>+ error message]

    L1 --> DB[(audit_log)]
    L2 --> DB
    L3 --> DB

    DB --> V[Audit Viewer Page<br/>chỉ HR_Manager truy cập]
```

---

## 7. Mapping Layers → Code Location

| Layer | Mục đích | Code path | Trạng thái Week 1 |
|---|---|---|---|
| L1 — Auth/RBAC | JWT verify, set RLS context | `app/middleware/auth.py` | TODO Week 6 |
| L2 — LLM Router | Tool vs SQL decision | `app/services/router.py` | TODO Week 4 |
| L3a — Tool Layer | Parameterized tools | `app/tools/*.py` | TODO Week 3 |
| L3b — Constrained SQL | sqlglot AST validator | `app/services/sql_validator.py` | TODO Week 5 |
| L4 — Mask + Exec | PostgreSQL + masking | `app/db/session.py` + `app/services/mask.py` | Foundation Week 1 ✅ |
| L5 — Audit | Insert audit_log | `app/repositories/audit_repo.py` | Foundation Week 1 ✅ |

> **Note**: Week 1 chỉ build foundation cho L4 + L5. Các layer còn lại lần lượt từ Week 3-6.
