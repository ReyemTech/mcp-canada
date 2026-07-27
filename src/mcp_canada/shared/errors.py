"""Classified exceptions — say whose fault a failure is at the raise site.

Phase 20.4. Four Codex findings across three PRs were one defect: an
``except ValueError -> INVALID_INPUT`` arm that captured every ``ValueError``
subclass any library happened to define. ``json.JSONDecodeError``,
``UnicodeDecodeError`` and ``pydantic.ValidationError`` all inherit from
``ValueError``, so an upstream outage was reported to the agent as the caller's
mistake. Each was fixed by intercepting one more subclass above that arm — a
deny-list that can never be complete.

The fix is to invert the default. Blame is now declared where the error is
raised, not guessed from its type in a handler:

    InvalidInput  -> INVALID_INPUT    the caller passed something wrong
    NotFound      -> NOT_FOUND        well-formed request, nothing matches
    UpstreamData  -> UPSTREAM_ERROR   the upstream sent something unusable

Anything else that is a plain ``ValueError`` — including a subclass nobody has
written yet — defaults to ``UPSTREAM_ERROR``. That is the safe direction: a
service problem misreported as a service problem is merely imprecise, while a
service problem misreported as caller error sends an agent chasing its own
arguments and fails live tests with a misleading code.

All three subclass ``ValueError`` deliberately, so any handler not yet migrated
keeps catching them. This changes classification, not control flow.
"""

from __future__ import annotations

__all__ = ["InvalidInput", "NotFound", "UpstreamData"]


class InvalidInput(ValueError):
    """The caller passed an argument this tool cannot accept.

    Use for validated enums, malformed identifiers and mutually exclusive
    options — anything the agent can fix by calling again differently::

        raise InvalidInput(f"mineral must be one of {sorted(MINES)}, got {mineral!r}")
    """


class NotFound(ValueError):
    """The request was well-formed but identifies nothing upstream.

    Distinct from :class:`InvalidInput`: the argument was plausible, the record
    simply does not exist. Do not use for an upstream outage::

        raise NotFound(f"Dataset not found: {dataset_id}")
    """


class UpstreamData(ValueError):
    """The upstream responded, but with something this client cannot use.

    An empty body, a package with no downloadable resource, an unparseable
    payload. Subclasses ``ValueError`` only so pre-migration handlers still
    catch it; it is never the caller's fault::

        raise UpstreamData("StatCan returned empty response body")
    """
