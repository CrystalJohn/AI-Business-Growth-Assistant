Alembic là gì? -> Git cho database schema
- giải quyết vấn đề version control cho database.
- Ví dụ code có github, DB cần Alembic.
- Nó cho phép
    - Mỗi thay đổi schema = 1 file migration (có ID, timestamp)
    - Có thể rollback, upgrade, downgrade schema
    - Theo dõi lịch sử thay đổi schema
- Như 1 standard trong production Python

1. Flow tổng quát (gồm 6 bước)
┌──────────────────────────────────────────────────┐
│ Setup (chỉ làm 1 lần khi bắt đầu project)         │
│                                                   │
│  1. alembic init alembic                          │
│     └→ tạo folder alembic/ + file alembic.ini     │
│                                                   │
│  2. Sửa alembic/env.py: trỏ tới DB + models       │
└──────────────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────────────┐
│ Workflow thường ngày (lặp lại mỗi lần đổi schema) │
│                                                   │
│  3. Bạn sửa SQLAlchemy model (Python)             │
│     VD: thêm cột `phone` vào class Employee       │
│                                                   │
│  4. alembic revision --autogenerate -m "add phone"│
│     └→ sinh file alembic/versions/abc123_add_*.py │
│                                                   │
│  5. Review file đó (đảm bảo đúng ý bạn)            │
│                                                   │
│  6. alembic upgrade head                          │
│     └→ apply migration vào DB thật                 │
└──────────────────────────────────────────────────┘
Chỉ 4 lệnh, lặp đi lặp lại.

2. Các lệnh cần nhớ

**Setup (1 lần duy nhất)**
    alembic init alembic           # tạo folder alembic/

**Workflow (lặp lại mỗi lần thay đổi schema)**
    alembic revision --autogenerate -m "add phone"  # tạo migration
    alembic upgrade head           # apply migration
    alembic current                # xem DB đang ở version nào
**Khi cần rollback**
    alembic downgrade -1           # rollback 1 bước
    alembic history                # xem lịch sử