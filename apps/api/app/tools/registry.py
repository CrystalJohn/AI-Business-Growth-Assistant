from app.tools.base import ToolBase
from app.tools.headcount_by_department import HeadcountByDepartmentTool
from app.tools.age_distribution import AgeDistributionTool
from app.tools.gender_distribution import GenderDistributionTool
from app.tools.search_employees import SearchEmployeesTool
from app.tools.employee_detail import GetEmployeeDetailTool
from app.tools.tenure_top_n import ListTenureTopNTool
from app.tools.avg_salary_by_level import GetAvgSalaryByLevelTool
from app.tools.payroll_summary import GetPayrollSummaryByMonthTool
from app.tools.leave_balance import GetLeaveBalanceTool
from app.tools.leaves_expiring import ListLeavesExpiringYearEndTool
from app.tools.attendance_summary import GetAttendanceSummaryTool
from app.tools.pending_reviews import ListPendingPerformanceReviewsTool
from app.tools.birthdays import ListBirthdaysThisMonthTool
from app.tools.turnover_rate import GetTurnoverRateTool
from app.tools.contracts_expiring import ListContractsExpiringSoonTool

REGISTRY: dict[str, type[ToolBase]] = {
    "get_headcount_by_department": HeadcountByDepartmentTool,
    "get_age_distribution": AgeDistributionTool,
    "get_gender_distribution": GenderDistributionTool,
    "search_employees": SearchEmployeesTool,
    "get_employee_detail": GetEmployeeDetailTool,
    "list_tenure_top_n": ListTenureTopNTool,
    "get_avg_salary_by_level": GetAvgSalaryByLevelTool,
    "get_payroll_summary_by_month": GetPayrollSummaryByMonthTool,
    "get_leave_balance": GetLeaveBalanceTool,
    "list_leaves_expiring_year_end": ListLeavesExpiringYearEndTool,
    "get_attendance_summary": GetAttendanceSummaryTool,
    "list_pending_performance_reviews": ListPendingPerformanceReviewsTool,
    "list_birthdays_this_month": ListBirthdaysThisMonthTool,
    "get_turnover_rate": GetTurnoverRateTool,
    "list_contracts_expiring_soon": ListContractsExpiringSoonTool,
}


def get_tool(name: str) -> ToolBase:
    if name not in REGISTRY:
        raise ValueError(f"Unknown tool: {name}")
    return REGISTRY[name]()


def list_tools() -> list[dict]:
    return [
        {
            "name": name,
            "description": cls.description,
            "required_role": cls.required_role,
            "input_schema": cls.input_model.model_json_schema(),
            "output_schema": cls.output_model.model_json_schema(),
        }
        for name, cls in REGISTRY.items()
    ]
