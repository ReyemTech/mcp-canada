"""Pydantic v2 models for the datastore module."""

from pydantic import BaseModel


class ColumnDef(BaseModel):
    """Definition of a single SQLite column."""

    name: str
    type: str
    notnull: bool = False
    pk: bool = False


class QueryResult(BaseModel):
    """Result of a SELECT/PRAGMA/EXPLAIN query."""

    columns: list[str]
    rows: list[dict]
    row_count: int
    truncated: bool


class TableInfo(BaseModel):
    """Summary info for a single table."""

    name: str
    column_count: int
