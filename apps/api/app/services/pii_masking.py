from __future__ import annotations

import re
from typing import Any


def _mask_citizen_id(value: str) -> str:
    """***123 — giữ 3 số cuối."""
    if len(value) <= 3:
        return "***"
    return "***" + value[-3:]


def _mask_phone(value: str) -> str:
    """***789 — giữ 3 số cuối."""
    digits = re.sub(r"\D", "", value)
    if len(digits) <= 3:
        return "***"
    return "***" + digits[-3:]


SALARY_FIELDS = {"base_salary", "allowance", "total_salary", "avg_salary", "total_gross", "total_net"}
PII_FIELDS = {
    "citizen_id": _mask_citizen_id,
    "citizen_id_masked": None,
    "phone": _mask_phone,
}


def mask_response_data(
    data: Any,
    role: str,
) -> tuple[Any, bool]:
    """Mask PII/salary fields based on role.

    Returns (masked_data, mask_applied).
    """
    if not data:
        return data, False

    mask_applied = False

    if isinstance(data, list):
        result = []
        for item in data:
            masked_item, applied = _mask_dict(item, role)
            result.append(masked_item)
            if applied:
                mask_applied = True
        return result, mask_applied

    if isinstance(data, dict):
        return _mask_dict(data, role)

    return data, False


def _mask_dict(item: dict[str, Any], role: str) -> tuple[dict[str, Any], bool]:
    """Mask fields in a single dict."""
    if not isinstance(item, dict):
        return item, False

    masked = dict(item)
    mask_applied = False

    # Salary fields — only HR_Manager sees
    if role != "HR_Manager":
        for field in SALARY_FIELDS:
            if field in masked and masked[field] is not None:
                masked[field] = "***"
                mask_applied = True

    # PII fields — mask for all non-HR_Manager
    if role not in ("HR_Manager", "HR_Staff"):
        for field, mask_fn in PII_FIELDS.items():
            if field in masked and masked[field] is not None:
                if mask_fn and isinstance(masked[field], str):
                    masked[field] = mask_fn(masked[field])
                    mask_applied = True
                elif field == "citizen_id_masked":
                    pass  # already masked by view

    return masked, mask_applied
