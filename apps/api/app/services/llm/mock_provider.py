from app.services.llm.base import LLMProvider, LLMResponse, ToolCall

_SQL_TEMPLATES: list[dict] = [
    {
        "keywords": ["vào làm", "join_date", "tháng", "năm"],
        "sql": (
            "SELECT full_name, job_title, join_date, department_name "
            "FROM v_employee_safe "
            "WHERE join_date >= '2023-01-01' "
            "ORDER BY join_date DESC LIMIT 50"
        ),
    },
    {
        "keywords": ["nghỉ phép", "leave", "ngày nghỉ", "tháng"],
        "sql": (
            "SELECT full_name, department_name, leave_type, total_days, status "
            "FROM v_leave_overview "
            "WHERE status = 'approved' "
            "ORDER BY start_date DESC LIMIT 50"
        ),
    },
    {
        "keywords": ["chấm công", "attendance", "vắng mặt", "đi trễ"],
        "sql": (
            "SELECT full_name, department_name, work_date, status "
            "FROM v_attendance_daily "
            "ORDER BY work_date DESC LIMIT 50"
        ),
    },
    {
        "keywords": ["đánh giá", "performance", "điểm", "rating"],
        "sql": (
            "SELECT full_name, department_name, period, score, rating "
            "FROM v_performance_summary "
            "ORDER BY score DESC LIMIT 50"
        ),
    },
]

KEYWORD_MAP: dict[str, list[str]] = {
    "get_headcount_by_department": ["headcount", "nhân viên", "phòng ban", "department", "bao nhiêu người", "số lượng"],
    "list_birthdays_this_month": ["sinh nhật", "birthday", "tháng này"],
    "get_avg_salary_by_level": ["lương", "salary", "level", "mức lương", "thu nhập", "lương trung bình"],
    "get_leave_balance": ["nghỉ phép", "leave", "phép", "nghỉ", "đơn nghỉ", "xin nghỉ"],
    "list_pending_performance_reviews": ["đánh giá", "performance", "review", "điểm", "hiệu suất", "kết quả"],
    "list_tenure_top_n": ["thâm niên", "tenure", "lâu nhất", "lâu năm", "ngày vào làm", "kỷ niệm công tác"],
    "search_employees": ["tìm kiếm", "search", "tìm nhân viên", "ai là"],
    "get_gender_distribution": ["giới tính", "gender", "nam nữ", "tỉ lệ nam"],
    "get_age_distribution": ["độ tuổi", "age", "tuổi", "phân bố tuổi"],
    "list_leaves_expiring_year_end": ["phép sắp hết", "phép năm", "còn phép"],
    "get_attendance_summary": ["chấm công", "attendance", "đi làm", "vắng mặt", "đi trễ"],
    "get_turnover_rate": ["nghỉ việc", "turnover", "tỉ lệ nghỉ", "attrition"],
    "list_contracts_expiring_soon": ["hợp đồng", "contract", "sắp hết hạn"],
    "get_payroll_summary_by_month": ["quỹ lương", "payroll", "tổng lương"],
    "get_employee_detail": ["chi tiết nhân viên", "thông tin nhân viên", "profile"],
}


class MockProvider(LLMProvider):
    name = "mock"

    async def generate_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: list[dict],
    ) -> LLMResponse:
        q = user_message.lower()

        for tool_name, keywords in KEYWORD_MAP.items():
            if any(kw in q for kw in keywords):
                return LLMResponse(
                    tool_call=ToolCall(name=tool_name, args={}),
                    finish_reason="tool_call",
                )

        return LLMResponse(
            tool_call=None,
            raw_text="Em chưa hiểu câu hỏi này. Thử hỏi: 'Headcount theo phòng ban?' hoặc 'Lương trung bình theo level?'",
            finish_reason="no_match",
        )

    async def generate_sql(
        self,
        question: str,
        view_schema: str,
    ) -> str | None:
        q = question.lower()
        for template in _SQL_TEMPLATES:
            if any(kw in q for kw in template["keywords"]):
                return template["sql"]
        return (
            "SELECT full_name, job_title, department_name, join_date "
            "FROM v_employee_safe "
            "ORDER BY full_name LIMIT 50"
        )

    async def summarize(
        self,
        question: str,
        data: list[dict],
        max_words: int = 100,
    ) -> str:
        if not data:
            return "Không tìm thấy kết quả phù hợp."

        n = len(data)
        first = data[0]
        keys = set(first.keys())

        # Headcount by department: {phong_ban, so_nhan_vien, nam, nu}
        if "phong_ban" in keys and "so_nhan_vien" in keys:
            parts = [f"{r['phong_ban']} ({r['so_nhan_vien']})" for r in data]
            total = sum(r.get("so_nhan_vien", 0) for r in data)
            return (
                f"Headcount theo {n} phòng ban: {', '.join(parts)}. "
                f"Tổng cộng {total} nhân viên."
            )

        # Salary by level: {level, avg, min, max, count}
        if "level" in keys and "avg" in keys and "min" in keys:
            parts = [f"{r['level']}: {r['avg'] / 1_000_000:.1f}M" for r in data]
            return f"Lương trung bình theo cấp bậc — {', '.join(parts)} (VND/tháng)."

        # Birthdays: {employee_id, name, dept, dob}
        if "dob" in keys and "name" in keys and "dept" in keys:
            names = [r["name"] for r in data[:5]]
            extra = f" và {n - 5} người khác" if n > 5 else ""
            return f"Có {n} nhân viên có sinh nhật tháng này: {', '.join(names)}{extra}."

        # Gender / age distribution (small list): {label, count}
        if "label" in keys and "count" in keys:
            parts = [f"{r['label']}: {r['count']}" for r in data]
            total = sum(r.get("count", 0) for r in data)
            return f"Phân bổ ({total} người): {', '.join(parts)}."

        # Age distribution: {age_range, count}
        if "age_range" in keys and "count" in keys:
            parts = [f"{r['age_range']} tuổi: {r['count']}" for r in data]
            return f"Phân bổ độ tuổi theo {n} nhóm: {', '.join(parts)}."

        # Tenure top N: {name, dept, years}
        if "years" in keys and "dept" in keys and "name" in keys:
            parts = [f"{r['name']} ({r['years']} năm, {r['dept']})" for r in data[:5]]
            extra = f" và {n - 5} người khác" if n > 5 else ""
            return f"Top {n} nhân viên thâm niên cao nhất: {', '.join(parts)}{extra}."

        # Performance reviews: {employee_id, name, rating}
        if "rating" in keys and "name" in keys:
            parts = [f"{r['name']} (điểm {r.get('rating', '?')})" for r in data[:5]]
            extra = f" và {n - 5} người khác" if n > 5 else ""
            return f"Có {n} kết quả đánh giá hiệu suất xuất sắc: {', '.join(parts)}{extra}."

        # Payroll summary: {dept, total_gross, headcount}
        if "total_gross" in keys and "dept" in keys:
            total = sum(r.get("total_gross", 0) for r in data)
            parts = [f"{r['dept']}: {r['total_gross'] / 1_000_000:.0f}M" for r in data]
            return f"Tổng quỹ lương {total / 1_000_000:.0f}M VND — chi tiết: {', '.join(parts)}."

        # Contracts expiring: {employee_id, name, contract_end, days_left}
        if "contract_end" in keys and "name" in keys:
            parts = [f"{r['name']} (còn {r.get('days_left', '?')} ngày)" for r in data[:5]]
            extra = f" và {n - 5} người khác" if n > 5 else ""
            return f"Có {n} hợp đồng sắp hết hạn: {', '.join(parts)}{extra}."

        # Leaves expiring: {employee_id, name, days_left}
        if "days_left" in keys and "name" in keys and "contract_end" not in keys:
            parts = [f"{r['name']} ({r.get('days_left', '?')} ngày)" for r in data[:5]]
            extra = f" và {n - 5} người khác" if n > 5 else ""
            return f"Có {n} nhân viên có ngày phép sắp hết năm: {', '.join(parts)}{extra}."

        # Leave balance (single): {name, annual_left, used, pending}
        if "annual_left" in keys and "name" in keys:
            r = first
            return (
                f"{r['name']} còn {r['annual_left']} ngày phép "
                f"(đã dùng {r['used']}, chờ duyệt {r['pending']})."
            )

        # Turnover rate (single): {leavers, avg_headcount, rate}
        if "leavers" in keys and "rate" in keys:
            r = first
            return (
                f"Tỷ lệ nghỉ việc: {r['rate']}% "
                f"({r['leavers']} người nghỉ / {r['avg_headcount']} nhân sự bình quân)."
            )

        # Attendance summary (single): {name, days_present, absent, late}
        if "days_present" in keys and "absent" in keys and "name" in keys:
            r = first
            return (
                f"{r['name']}: có mặt {r['days_present']} ngày, "
                f"vắng {r['absent']} ngày, đi trễ {r['late']} ngày."
            )

        # Search / employee list: {id, name, dept, level, joined_at}
        if "name" in keys and ("dept" in keys or "department" in keys):
            dept_key = "dept" if "dept" in keys else "department"
            parts = [f"{r['name']} ({r.get(dept_key, '?')})" for r in data[:5]]
            extra = f" và {n - 5} người khác" if n > 5 else ""
            return f"Tìm thấy {n} nhân viên: {', '.join(parts)}{extra}."

        # Generic fallback
        if n == 1:
            return "Tìm thấy 1 kết quả."
        return f"Tìm thấy {n} kết quả."
