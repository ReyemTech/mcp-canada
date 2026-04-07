"""Constants for the datastore module."""

import re
from pathlib import Path

# Default database file location — ~/.mcp-canada/datastore.db
DB_PATH = Path.home() / ".mcp-canada" / "datastore.db"

# Identifier regex: must start with letter or underscore, then letters/digits/underscores
# Maximum total length = 1 leading char + up to 63 more = 64 chars
IDENTIFIER_RE = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$")

# Maximum rows returned by run_query
MAX_QUERY_ROWS = 1000

# SQL prefixes allowed in run_query (case-insensitive check)
ALLOWED_QUERY_PREFIXES = ("SELECT", "PRAGMA", "EXPLAIN", "CREATE INDEX")
