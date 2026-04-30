# Frontend — Next.js

## Yêu cầu
- **Node.js 18+**
- Backend API đang chạy tại `http://localhost:8000` (xem `apps/api/README.md`)

---

## Lần đầu chạy

```powershell
# 1. Vào thư mục
cd apps/web

# 2. Cài dependencies
npm install

# 3. Tạo file env (copy từ example)
copy .env.local.example .env.local

# 4. Chạy dev server
npm run dev
```

App chạy tại: **http://localhost:3000**

---

## Các lần sau

```powershell
cd apps/web
npm run dev
```

---

## Biến môi trường

File `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Trang

| URL | Mô tả |
|-----|--------|
| `/` | Landing page |
| `/chat` | Chat với AI Assistant |
| `/chat?q=...` | Mở chat với câu hỏi sẵn có trong URL |

---

## Build production

```powershell
npm run build
npm run start
```

---

## Lưu ý

- Frontend cần backend chạy trước mới gọi API được
- Lint errors trong IDE là bình thường trước khi `npm install`
- Swagger UI của backend: **http://localhost:8000/docs**
