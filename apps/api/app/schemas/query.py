from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TableColumn(BaseModel):
    key: str
    label: str
    type: str = "string"


class QueryRequest(BaseModel):
    question: str
    context: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    data: List[Dict[str, Any]] | Dict[str, Any] = []
    rows: int = 0
    tool: Optional[str] = None
    chart_type: Optional[str] = None


class ValidateRequest(BaseModel):
    sql: str


class ValidateResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    formatted: Optional[str] = None
