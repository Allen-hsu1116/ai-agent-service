import re

from fastapi import HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session as SQLAlchemySession

READ_ONLY_PREFIXES = ("select", "with", "pragma", "explain")


def ensure_read_only_query(query: str) -> None:
    normalized = query.strip().lower()
    if not normalized.startswith(READ_ONLY_PREFIXES):
        raise HTTPException(
            status_code=400,
            detail="Only read-only SELECT, WITH, PRAGMA, or EXPLAIN queries are allowed.",
        )

    if ";" in normalized.rstrip(";"):
        raise HTTPException(status_code=400, detail="Only one SQL statement is allowed.")

    forbidden = re.compile(
        r"(insert|update|delete|drop|alter|create|replace|truncate|attach|detach|vacuum)",
        re.IGNORECASE,
    )
    if forbidden.search(normalized):
        raise HTTPException(
            status_code=400,
            detail="Only read-only SELECT, WITH, PRAGMA, or EXPLAIN queries are allowed.",
        )


def run_read_only_query(db: SQLAlchemySession, query: str) -> tuple[list[str], list[dict[str, object]]]:
    ensure_read_only_query(query)
    result = db.execute(text(query))
    columns = list(result.keys())
    rows = [dict(row._mapping) for row in result.fetchall()]
    return columns, rows
