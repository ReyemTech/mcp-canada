import httpx

from mcp_canada import __version__
from mcp_canada.modules.statcan.constants import STATCAN_VERIFY


def _make_statcan_client() -> httpx.AsyncClient:
    """Create an httpx client scoped to StatCan with correct SSL setting.

    verify=True uses certifi (httpx default).
    verify=False is scoped to this client only — never affects shared clients.
    """
    return httpx.AsyncClient(
        verify=STATCAN_VERIFY,
        timeout=httpx.Timeout(30.0),
        headers={"User-Agent": f"mcp-canada/{__version__}"},
    )
