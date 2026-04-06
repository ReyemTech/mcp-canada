"""Stub HTTP client for the example module (demonstrates the client pattern)."""


async def fetch_echo(message: str, lang: str = "en") -> dict:
    """Stub: return mock echo data without making a real HTTP request.

    In a real module, this would call an external API using the shared HTTP client.
    """
    return {
        "message": message,
        "lang": lang,
        "echoed": True,
    }
