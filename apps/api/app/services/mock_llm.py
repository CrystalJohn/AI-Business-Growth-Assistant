"""
Mock LLM provider.

Returns realistic pre-canned responses based on keyword matching.
Replace this module with a real LLM provider when ready.
"""

from app.schemas.query import QueryResponse, TableColumn

# ---------------------------------------------------------------------------
# HR Response catalogue — 6 use cases mapped from docs/erd.md section 5
# ---------------------------------------------------------------------------

_RESPONSES: list[dict] = [
    {
        "keywords": ["headcount", "nhân viên", "phòng ban", "department", "bao nhiêu người", "số lượng"],
        "answer": (
            "Tổng headcount hiện tại là **150 nhân viên** phân bố trên 4 phòng ban. "
            "**Kỹ thuật** dẫn đầu với 42 người, tiếp theo là **Kinh doanh** (38), "
            "**Marketing** (37) và **Nhân sự** (33). Tỉ lệ nam/nữ tổng thể là 60/40."
        ),
        "sql": """\
SELECT
  d.name                  AS phong_ban,
  COUNT(e.id)             AS so_nhan_vien,
  SUM(CASE WHEN e.gender = 'M' THEN 1 ELSE 0 END) AS nam,
  SUM(CASE WHEN e.gender = 'F' THEN 1 ELSE 0 END) AS nu
FROM employees e
JOIN departments d ON d.id = e.department_id
WHERE e.deleted_at IS NULL
  AND e.status = 'active'
GROUP BY d.name
ORDER BY so_nhan_vien DESC;""",
        "columns": [
            {"key": "phong_ban",      "label": "Phòng ban",   "type": "string"},
            {"key": "so_nhan_vien",   "label": "Tổng",        "type": "number"},
            {"key": "nam",            "label": "Nam",         "type": "number"},
            {"key": "nu",             "label": "Nữ",          "type": "number"},
        ],
        "rows": [
            {"phong_ban": "Kỹ thuật",   "so_nhan_vien": 42, "nam": 28, "nu": 14},
            {"phong_ban": "Kinh doanh", "so_nhan_vien": 38, "nam": 24, "nu": 14},
            {"phong_ban": "Marketing",  "so_nhan_vien": 37, "nam": 20, "nu": 17},
            {"phong_ban": "Nhân sự",    "so_nhan_vien": 33, "nam": 16, "nu": 17},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "Tỉ lệ nam/nữ theo từng phòng ban?",
            "Headcount thay đổi như thế nào trong 12 tháng qua?",
            "Phòng ban nào có tỉ lệ nghỉ việc cao nhất?",
        ],
    },
    {
        "keywords": ["sinh nhật", "birthday", "tháng này", "tháng", "kỷ niệm"],
        "answer": (
            "Tháng này có **8 nhân viên** có sinh nhật. "
            "Gửi lời chúc sớm để tạo gắn kết nhé! "
            "Danh sách được sắp theo ngày sinh nhật tăng dần."
        ),
        "sql": """\
SELECT
  full_name,
  TO_CHAR(birth_date, 'DD/MM')   AS ngay_sinh_nhat,
  job_title,
  d.name                          AS phong_ban
FROM employees e
JOIN departments d ON d.id = e.department_id
WHERE EXTRACT(MONTH FROM birth_date) = EXTRACT(MONTH FROM CURRENT_DATE)
  AND e.deleted_at IS NULL
  AND e.status = 'active'
ORDER BY EXTRACT(DAY FROM birth_date);""",
        "columns": [
            {"key": "full_name",       "label": "Họ và tên",     "type": "string"},
            {"key": "ngay_sinh_nhat",  "label": "Ngày sinh",     "type": "string"},
            {"key": "job_title",       "label": "Chức danh",     "type": "string"},
            {"key": "phong_ban",       "label": "Phòng ban",     "type": "string"},
        ],
        "rows": [
            {"full_name": "Nguyễn Thị Lan",   "ngay_sinh_nhat": "03/05", "job_title": "Chuyên viên marketing",    "phong_ban": "Marketing"},
            {"full_name": "Trần Văn Minh",     "ngay_sinh_nhat": "07/05", "job_title": "Lập trình viên Backend",   "phong_ban": "Kỹ thuật"},
            {"full_name": "Lê Thị Hương",      "ngay_sinh_nhat": "10/05", "job_title": "Chuyên viên tuyển dụng",  "phong_ban": "Nhân sự"},
            {"full_name": "Phạm Quốc Bảo",     "ngay_sinh_nhat": "14/05", "job_title": "Chuyên viên kinh doanh",  "phong_ban": "Kinh doanh"},
            {"full_name": "Hoàng Thị Mai",     "ngay_sinh_nhat": "18/05", "job_title": "Chuyên viên nội dung",    "phong_ban": "Marketing"},
            {"full_name": "Đặng Văn Hùng",     "ngay_sinh_nhat": "21/05", "job_title": "Kỹ sư DevOps",            "phong_ban": "Kỹ thuật"},
            {"full_name": "Vũ Thị Thu",        "ngay_sinh_nhat": "25/05", "job_title": "Chuyên viên C&B",         "phong_ban": "Nhân sự"},
            {"full_name": "Bùi Đức Thắng",     "ngay_sinh_nhat": "29/05", "job_title": "Quản lý tài khoản",       "phong_ban": "Kinh doanh"},
        ],
        "chartType": None,
        "followUpQuestions": [
            "Sinh nhật tháng sau có những ai?",
            "Nhân viên nào sắp kỷ niệm ngày vào làm?",
        ],
    },
    {
        "keywords": ["lương", "salary", "level", "mức lương", "thu nhập", "lương trung bình"],
        "answer": (
            "Lương trung bình toàn công ty là **28.4 triệu VND/tháng**. "
            "Manager có mức cao nhất (**57.2M**), Junior thấp nhất (**11.3M**). "
            "Phòng Kỹ thuật có lương trung bình cao nhất trong 4 phòng ban."
        ),
        "sql": """\
SELECT
  p.level,
  COUNT(*)                              AS so_nhan_vien,
  ROUND(AVG(p.base_salary) / 1000000, 1) AS luong_tb_trieu,
  ROUND(MIN(p.base_salary) / 1000000, 1) AS luong_min_trieu,
  ROUND(MAX(p.base_salary) / 1000000, 1) AS luong_max_trieu
FROM payroll p
JOIN employees e ON e.id = p.employee_id
WHERE p.deleted_at IS NULL
  AND e.deleted_at IS NULL
GROUP BY p.level
ORDER BY luong_tb_trieu DESC;""",
        "columns": [
            {"key": "level",           "label": "Level",        "type": "string"},
            {"key": "so_nhan_vien",    "label": "Số NV",        "type": "number"},
            {"key": "luong_tb_trieu",  "label": "TB (triệu)",   "type": "number"},
            {"key": "luong_min_trieu", "label": "Min (triệu)",  "type": "number"},
            {"key": "luong_max_trieu", "label": "Max (triệu)",  "type": "number"},
        ],
        "rows": [
            {"level": "Manager", "so_nhan_vien": 15, "luong_tb_trieu": 57.2, "luong_min_trieu": 40.5, "luong_max_trieu": 79.0},
            {"level": "Lead",    "so_nhan_vien": 22, "luong_tb_trieu": 38.6, "luong_min_trieu": 30.0, "luong_max_trieu": 49.5},
            {"level": "Senior",  "so_nhan_vien": 53, "luong_tb_trieu": 21.4, "luong_min_trieu": 15.0, "luong_max_trieu": 29.5},
            {"level": "Junior",  "so_nhan_vien": 60, "luong_tb_trieu": 11.3, "luong_min_trieu":  8.0, "luong_max_trieu": 14.5},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "Lương trung bình theo phòng ban?",
            "Bao nhiêu nhân viên đang ở mức lương trên 30 triệu?",
            "So sánh lương nam và nữ cùng level?",
        ],
    },
    {
        "keywords": ["nghỉ phép", "leave", "phép", "nghỉ", "đơn nghỉ", "xin nghỉ"],
        "answer": (
            "Hiện có **23 đơn nghỉ phép đang chờ duyệt**. "
            "Loại nghỉ phổ biến nhất là **Nghỉ phép năm** (14 đơn). "
            "Phòng Kỹ thuật có nhiều đơn pending nhất (8 đơn)."
        ),
        "sql": """\
SELECT
  lr.leave_type,
  lr.status,
  COUNT(*)          AS so_don,
  e.full_name,
  d.name            AS phong_ban,
  lr.start_date,
  lr.end_date
FROM leave_requests lr
JOIN employees e    ON e.id = lr.employee_id
JOIN departments d  ON d.id = e.department_id
WHERE lr.status = 'pending'
  AND lr.deleted_at IS NULL
ORDER BY lr.created_at DESC
LIMIT 10;""",
        "columns": [
            {"key": "full_name",   "label": "Nhân viên",    "type": "string"},
            {"key": "phong_ban",   "label": "Phòng ban",    "type": "string"},
            {"key": "leave_type",  "label": "Loại nghỉ",   "type": "string"},
            {"key": "start_date",  "label": "Từ ngày",     "type": "string"},
            {"key": "end_date",    "label": "Đến ngày",    "type": "string"},
        ],
        "rows": [
            {"full_name": "Nguyễn Văn An",   "phong_ban": "Kỹ thuật",   "leave_type": "Nghỉ phép năm",  "start_date": "2026-05-05", "end_date": "2026-05-07"},
            {"full_name": "Trần Thị Bích",   "phong_ban": "Marketing",  "leave_type": "Nghỉ ốm",        "start_date": "2026-05-06", "end_date": "2026-05-06"},
            {"full_name": "Lê Quang Đức",    "phong_ban": "Kinh doanh", "leave_type": "Nghỉ phép năm",  "start_date": "2026-05-08", "end_date": "2026-05-10"},
            {"full_name": "Phạm Thị Cúc",    "phong_ban": "Nhân sự",    "leave_type": "Nghỉ thai sản",  "start_date": "2026-05-10", "end_date": "2026-07-10"},
            {"full_name": "Hoàng Văn Tân",   "phong_ban": "Kỹ thuật",   "leave_type": "Nghỉ phép năm",  "start_date": "2026-05-12", "end_date": "2026-05-14"},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "Tổng số ngày phép đã dùng theo phòng ban?",
            "Nhân viên nào còn nhiều phép nhất?",
            "Tháng nào có nhiều đơn nghỉ nhất trong năm?",
        ],
    },
    {
        "keywords": ["đánh giá", "performance", "review", "điểm", "hiệu suất", "kết quả"],
        "answer": (
            "Kỳ đánh giá **2024-H2** vừa hoàn thành với điểm trung bình **3.72/5**. "
            "**42%** nhân viên đạt xếp loại *Tốt* hoặc *Xuất sắc*. "
            "Phòng Kỹ thuật có điểm trung bình cao nhất (3.91)."
        ),
        "sql": """\
SELECT
  d.name                              AS phong_ban,
  COUNT(pr.id)                        AS so_danh_gia,
  ROUND(AVG(pr.score), 2)            AS diem_trung_binh,
  SUM(CASE WHEN pr.rating IN ('Xuất sắc','Tốt') THEN 1 ELSE 0 END) AS dat_tot_tro_len,
  ROUND(
    SUM(CASE WHEN pr.rating IN ('Xuất sắc','Tốt') THEN 1 ELSE 0 END)::numeric
    / COUNT(pr.id) * 100, 1
  )                                   AS pct_tot_tro_len
FROM performance_reviews pr
JOIN employees e   ON e.id = pr.employee_id
JOIN departments d ON d.id = e.department_id
WHERE pr.period = '2024-H2'
  AND pr.deleted_at IS NULL
GROUP BY d.name
ORDER BY diem_trung_binh DESC;""",
        "columns": [
            {"key": "phong_ban",        "label": "Phòng ban",       "type": "string"},
            {"key": "so_danh_gia",      "label": "Số đánh giá",     "type": "number"},
            {"key": "diem_trung_binh",  "label": "Điểm TB",         "type": "number"},
            {"key": "pct_tot_tro_len",  "label": "% Tốt+",          "type": "number"},
        ],
        "rows": [
            {"phong_ban": "Kỹ thuật",   "so_danh_gia": 42, "diem_trung_binh": 3.91, "pct_tot_tro_len": 48.0},
            {"phong_ban": "Kinh doanh", "so_danh_gia": 38, "diem_trung_binh": 3.74, "pct_tot_tro_len": 42.0},
            {"phong_ban": "Marketing",  "so_danh_gia": 37, "diem_trung_binh": 3.68, "pct_tot_tro_len": 40.0},
            {"phong_ban": "Nhân sự",    "so_danh_gia": 33, "diem_trung_binh": 3.55, "pct_tot_tro_len": 36.0},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "Ai có điểm đánh giá cao nhất kỳ 2024-H2?",
            "So sánh điểm trung bình 2024-H1 vs 2024-H2?",
            "Nhân viên nào cần cải thiện (điểm dưới 2.5)?",
        ],
    },
    {
        "keywords": ["thâm niên", "tenure", "lâu nhất", "lâu năm", "ngày vào làm", "kỷ niệm công tác"],
        "answer": (
            "Top 5 nhân viên có thâm niên cao nhất đều trên **4 năm** công tác. "
            "**Nguyễn Văn Thành** dẫn đầu với gần 5 năm. "
            "Trung bình toàn công ty là **2.3 năm**."
        ),
        "sql": """\
SELECT
  e.full_name,
  d.name                                                  AS phong_ban,
  e.job_title,
  e.join_date,
  ROUND(
    EXTRACT(EPOCH FROM (CURRENT_DATE - e.join_date)) / 86400 / 365, 1
  )                                                       AS tham_nien_nam
FROM employees e
JOIN departments d ON d.id = e.department_id
WHERE e.deleted_at IS NULL
  AND e.status = 'active'
ORDER BY e.join_date ASC
LIMIT 10;""",
        "columns": [
            {"key": "full_name",      "label": "Họ và tên",    "type": "string"},
            {"key": "phong_ban",      "label": "Phòng ban",    "type": "string"},
            {"key": "job_title",      "label": "Chức danh",    "type": "string"},
            {"key": "join_date",      "label": "Ngày vào",     "type": "string"},
            {"key": "tham_nien_nam",  "label": "Thâm niên (năm)", "type": "number"},
        ],
        "rows": [
            {"full_name": "Nguyễn Văn Thành",  "phong_ban": "Kỹ thuật",   "job_title": "Trưởng nhóm kỹ thuật",    "join_date": "2021-06-01", "tham_nien_nam": 4.9},
            {"full_name": "Trần Thị Ngọc",     "phong_ban": "Nhân sự",    "job_title": "Trưởng phòng nhân sự",    "join_date": "2021-08-15", "tham_nien_nam": 4.7},
            {"full_name": "Lê Minh Khoa",      "phong_ban": "Kinh doanh", "job_title": "Giám đốc KD khu vực",     "join_date": "2021-09-03", "tham_nien_nam": 4.7},
            {"full_name": "Phạm Thị Thu Hà",   "phong_ban": "Marketing",  "job_title": "Giám đốc marketing",      "join_date": "2021-11-20", "tham_nien_nam": 4.5},
            {"full_name": "Hoàng Đức Long",    "phong_ban": "Kỹ thuật",   "job_title": "Kiến trúc sư hệ thống",   "join_date": "2022-01-10", "tham_nien_nam": 4.3},
        ],
        "chartType": "bar",
        "followUpQuestions": [
            "Phân bố thâm niên theo phòng ban?",
            "Bao nhiêu nhân viên sắp tròn 5 năm công tác?",
            "Tỉ lệ nghỉ việc theo nhóm thâm niên?",
        ],
    },
]

# ---------------------------------------------------------------------------
# Default fallback — HR overview
# ---------------------------------------------------------------------------

_DEFAULT_RESPONSE: dict = {
    "answer": (
        "Tôi có thể trả lời các câu hỏi HR như: headcount theo phòng ban, "
        "sinh nhật nhân viên, phân tích lương, đơn nghỉ phép, đánh giá hiệu suất và thâm niên. "
        "Thử hỏi: *'Tổng headcount theo phòng ban?'* hoặc *'Lương trung bình theo level?'*"
    ),
    "sql": """\
SELECT 'departments'        AS table_name, COUNT(*) AS row_count FROM departments
UNION ALL
SELECT 'employees',         COUNT(*) FROM employees WHERE deleted_at IS NULL
UNION ALL
SELECT 'payroll',           COUNT(*) FROM payroll WHERE deleted_at IS NULL
UNION ALL
SELECT 'attendance',        COUNT(*) FROM attendance WHERE deleted_at IS NULL
UNION ALL
SELECT 'leave_requests',    COUNT(*) FROM leave_requests WHERE deleted_at IS NULL
UNION ALL
SELECT 'performance_reviews', COUNT(*) FROM performance_reviews WHERE deleted_at IS NULL;""",
    "columns": [
        {"key": "table_name", "label": "Bảng",        "type": "string"},
        {"key": "row_count",  "label": "Số bản ghi",  "type": "number"},
    ],
    "rows": [
        {"table_name": "departments",         "row_count":   4},
        {"table_name": "employees",           "row_count": 150},
        {"table_name": "payroll",             "row_count": 150},
        {"table_name": "attendance",          "row_count": 3200},
        {"table_name": "leave_requests",      "row_count": 200},
        {"table_name": "performance_reviews", "row_count": 300},
    ],
    "chartType": "bar",
    "followUpQuestions": [
        "Tổng headcount theo phòng ban?",
        "Lương trung bình theo level?",
        "Có bao nhiêu đơn nghỉ phép đang pending?",
        "Điểm performance trung bình kỳ 2024-H2?",
        "Top 10 nhân viên có thâm niên cao nhất?",
    ],
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_mock_response(question: str) -> QueryResponse:
    q = question.lower()

    for resp in _RESPONSES:
        if any(kw in q for kw in resp["keywords"]):
            return QueryResponse(
                answer=resp["answer"],
                sql=resp["sql"],
                columns=[TableColumn(**c) for c in resp["columns"]],
                rows=resp["rows"],
                chartType=resp.get("chartType"),
                followUpQuestions=resp.get("followUpQuestions", []),
            )

    return QueryResponse(
        answer=_DEFAULT_RESPONSE["answer"],
        sql=_DEFAULT_RESPONSE["sql"],
        columns=[TableColumn(**c) for c in _DEFAULT_RESPONSE["columns"]],
        rows=_DEFAULT_RESPONSE["rows"],
        chartType=_DEFAULT_RESPONSE.get("chartType"),
        followUpQuestions=_DEFAULT_RESPONSE.get("followUpQuestions", []),
    )
