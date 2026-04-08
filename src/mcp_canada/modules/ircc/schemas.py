"""IRCC module schemas.

IRCC data is parsed dynamically from XLSX files where column names vary by file
and language. No Pydantic models are needed — the dataset registry in constants.py
is the schema, and each file's column headers become dict keys after normalization
via shared/parsers.py _normalize_key().

Column names differ between EN and FR files (IRCC provides fully bilingual
workbooks including headers). Always use lang="en" for datastore storage to keep
column names consistent across SQL operations.

Privacy note: IRCC suppresses values between 0–5 as '--' and rounds all other
values to the nearest multiple of 5. The parser converts '--' to None.
"""
