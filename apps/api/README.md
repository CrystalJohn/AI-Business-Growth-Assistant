# Backend — FastAPI

## Yêu cầu
- **Python 3.12** (không dùng 3.13/3.14 — chưa có pre-built wheels)
- Cài Python 3.12: `winget install Python.Python.3.12`

---

## Lần đầu chạy

```powershell
# 1. Vào thư mục
cd apps/api

# 2. Tạo virtual environment với Python 3.12
py -3.12 -m venv .venv

# 3. Kích hoạt venv (PowerShell)
.\.venv\Scripts\Activate.ps1

# Nếu bị lỗi ExecutionPolicy, chạy lệnh này trước:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 4. Cài dependencies
pip install --prefer-binary -r requirements.txt

# 5. Chạy server
uvicorn main:app --reload
```

Server chạy tại: **http://localhost:8000**

---

## Các lần sau

```powershell
cd apps/api
.\.venv\Scripts\Activate.ps1
uvicorn main:app --reload
```

---

## Test API

Mở browser: **http://localhost:8000/docs** (Swagger UI tự động)

Hoặc dùng curl trên PowerShell:

```powershell
# Health check
curl.exe http://localhost:8000/health

# Chat query
curl.exe -X POST http://localhost:8000/chat/query `
  -H "Content-Type: application/json" `
  -d '{\"question\":\"What are top 5 products by revenue?\"}'

# Schema
curl.exe http://localhost:8000/schema
```

---

## Endpoints

| Method | Path | Mô tả |
|--------|------|--------|
| GET | `/health` | Kiểm tra trạng thái API |
| GET | `/schema` | Trả về schema database |
| POST | `/chat/query` | Nhận câu hỏi, trả về SQL + kết quả |
| POST | `/sql/validate` | Validate cú pháp SQL |

---

## Lưu ý

- Đang dùng **Mock LLM** — không cần API key
- Biến môi trường xem tại `../../.env.example`
- Để đổi sang LLM thật: set `LLM_PROVIDER=gemini` trong `.env`
