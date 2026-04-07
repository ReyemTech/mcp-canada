"""Shared fixtures for datastore module tests."""

import pytest
import aiosqlite

from mcp_canada.modules.datastore import client


@pytest.fixture
async def db():
    """In-memory SQLite connection with WAL mode and row_factory configured."""
    conn = await aiosqlite.connect(":memory:")
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    yield conn
    await conn.close()


@pytest.fixture
async def patched_db(db):
    """Patch client._db with an in-memory connection so get_db() returns it."""
    original = client._db
    client._db = db
    yield db
    client._db = original
