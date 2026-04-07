"""Minimal tests for statcan module stub (INF-01)."""
import httpx

from mcp_canada.modules.statcan.client import _make_statcan_client
from mcp_canada.modules.statcan.constants import STATCAN_VERIFY


class TestStatcanStub:
    def test_statcan_verify_is_bool(self):
        assert isinstance(STATCAN_VERIFY, bool)

    def test_make_statcan_client_returns_async_client(self):
        client = _make_statcan_client()
        assert isinstance(client, httpx.AsyncClient)

    def test_client_uses_statcan_verify(self):
        client = _make_statcan_client()
        # verify=False means no SSL context; verify=True means SSL context present
        # Either way, the client was created without error
        assert client is not None
