"""
Constrained SQL Validator — Week 5

Validates LLM-generated SQL before execution:
  1. Must be parseable by sqlglot
  2. Must be a single SELECT statement (no DML/DDL)
  3. All table/view references must be in ALLOWED_VIEWS whitelist
  4. No dangerous functions (pg_sleep, pg_read_file, COPY, lo_*)
  5. LIMIT enforced — injected as LIMIT 50 if missing, capped at 100
  6. Single statement only (no semicolons mid-query)
"""

from __future__ import annotations

import re
from dataclasses import dataclass

import sqlglot
import sqlglot.expressions as exp

ALLOWED_VIEWS: frozenset[str] = frozenset(
    {
        "v_employee_safe",
        "v_payroll_anonymized",
        "v_attendance_daily",
        "v_leave_overview",
        "v_performance_summary",
        "v_department_list",
    }
)

BLOCKED_FUNCTIONS: frozenset[str] = frozenset(
    {
        "pg_sleep",
        "pg_read_file",
        "pg_ls_dir",
        "pg_stat_file",
        "lo_import",
        "lo_export",
        "dblink",
        "copy",
    }
)

DEFAULT_LIMIT = 50
MAX_LIMIT = 100


@dataclass
class ValidationResult:
    valid: bool
    sql: str | None = None
    error: str | None = None


def validate(raw_sql: str) -> ValidationResult:
    """
    Validate and sanitise LLM-generated SQL.

    Returns ValidationResult with:
      - valid=True + sql=sanitised SQL on success
      - valid=False + error=reason on failure
    """
    sql = raw_sql.strip().rstrip(";")

    # Reject obvious multi-statement attacks
    if _has_multiple_statements(sql):
        return ValidationResult(valid=False, error="Multi-statement SQL is not allowed.")

    # Parse
    try:
        statements = sqlglot.parse(sql, dialect="postgres")
    except Exception as exc:
        return ValidationResult(valid=False, error=f"Parse error: {exc}")

    if not statements or statements[0] is None:
        return ValidationResult(valid=False, error="Could not parse SQL.")

    if len(statements) > 1:
        return ValidationResult(valid=False, error="Multi-statement SQL is not allowed.")

    stmt = statements[0]

    # Must be SELECT
    if not isinstance(stmt, exp.Select):
        kind = type(stmt).__name__
        return ValidationResult(
            valid=False,
            error=f"Only SELECT statements are allowed. Got: {kind}.",
        )

    # Check for dangerous functions
    for func in stmt.find_all(exp.Anonymous, exp.Func):
        name = (
            func.name.lower()
            if hasattr(func, "name") and func.name
            else ""
        )
        if name in BLOCKED_FUNCTIONS:
            return ValidationResult(
                valid=False, error=f"Blocked function: '{name}'."
            )

    # Check table/view whitelist
    for table in stmt.find_all(exp.Table):
        tname = table.name.lower() if table.name else ""
        if tname and tname not in ALLOWED_VIEWS:
            return ValidationResult(
                valid=False,
                error=(
                    f"Table or view '{tname}' is not allowed. "
                    f"Only these views are permitted: {sorted(ALLOWED_VIEWS)}."
                ),
            )

    # Enforce LIMIT
    stmt = _enforce_limit(stmt)

    sanitised = stmt.sql(dialect="postgres", pretty=False)
    return ValidationResult(valid=True, sql=sanitised)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _has_multiple_statements(sql: str) -> bool:
    """Detect semicolons that separate statements (not inside strings)."""
    # Strip single-quoted strings before checking
    stripped = re.sub(r"'[^']*'", "''", sql)
    return ";" in stripped


def _enforce_limit(stmt: exp.Select) -> exp.Select:
    """Ensure LIMIT exists and does not exceed MAX_LIMIT."""
    limit_node = stmt.args.get("limit")
    if limit_node is None:
        return stmt.limit(DEFAULT_LIMIT)

    # Extract the integer value from the LIMIT node robustly
    # sqlglot 25: Limit(expression=Literal(this=<int>), this=None)
    current: int | None = None
    try:
        limit_expr = limit_node.args.get("expression") or limit_node.args.get("this")
        if limit_expr is not None:
            current = int(limit_expr.this)
    except (AttributeError, ValueError, TypeError):
        pass

    if current is None:
        return stmt.limit(DEFAULT_LIMIT)
    if current > MAX_LIMIT:
        return stmt.limit(MAX_LIMIT)
    return stmt
