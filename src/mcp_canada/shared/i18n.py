"""Bilingual labels and translation helper for en/fr error messages."""

from typing import Any

LABELS: dict[str, dict[str, str]] = {
    "error.rate_limited": {
        "en": "Rate limit exceeded. Please retry after {retry_after} seconds.",
        "fr": "Limite de taux dépassée. Veuillez réessayer dans {retry_after} secondes.",
    },
    "error.api_unavailable": {
        "en": "The upstream API is temporarily unavailable. Please try again later.",
        "fr": "L'API en amont est temporairement indisponible. Veuillez réessayer plus tard.",
    },
    "error.invalid_input": {
        "en": "Invalid input: {detail}",
        "fr": "Entrée invalide : {detail}",
    },
    "error.upstream_error": {
        "en": "An upstream error occurred: {detail}",
        "fr": "Une erreur en amont s'est produite : {detail}",
    },
    "error.not_found": {
        "en": "The requested resource was not found.",
        "fr": "La ressource demandée est introuvable.",
    },
}


def t(key: str, lang: str = "en", **kwargs: Any) -> str:
    """Look up a bilingual label and apply interpolation.

    Args:
        key: Dot-separated label key (e.g. 'error.rate_limited').
        lang: Language code ('en' or 'fr'). Falls back to 'en' if lang not found.
        **kwargs: Format variables to interpolate into the message.

    Returns:
        Translated and interpolated string, or key itself if not found.
    """
    entry = LABELS.get(key)
    if entry is None:
        return key

    template = entry.get(lang) or entry.get("en") or key
    try:
        return template.format(**kwargs)
    except KeyError:
        return template
