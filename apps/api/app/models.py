from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class TableColumn(BaseModel):
    key: str
    label: str
    type: str = "string"


class QueryRequest(BaseModel):
    question: str
    context: Optional[str] = None


class QueryResponse(BaseModel):
    answer: str
    sql: str
    columns: List[TableColumn]
    rows: List[Dict[str, Any]]
    chartType: Optional[str] = None
    followUpQuestions: List[str] = []


class ValidateRequest(BaseModel):
    sql: str


class ValidateResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    formatted: Optional[str] = None
