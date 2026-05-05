from fastapi import APIRouter

from app.schemas.query import ValidateRequest, ValidateResponse

router = APIRouter()


@router.post("/validate", response_model=ValidateResponse)
def validate_sql(request: ValidateRequest) -> ValidateResponse:
    try:
        import sqlglot

        parsed = sqlglot.parse(request.sql)
        if not parsed:
            return ValidateResponse(valid=False, error="Could not parse SQL — empty result.")

        formatted = sqlglot.transpile(request.sql, pretty=True)[0]
        return ValidateResponse(valid=True, formatted=formatted)
    except Exception as exc:
        return ValidateResponse(valid=False, error=str(exc))
