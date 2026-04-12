"""Example module demonstrating the 7-file pattern.

Private fixture — the ``_`` prefix excludes this module from production
registration in ``server._build_providers``. It is loaded only by tests that
point a ``FileSystemProvider`` directly at this directory (``tests/test_registry.py``,
``tests/test_discovery.py``, ``tests/test_server.py``) and by ``test_quality.py``
which exercises the BM25 docstring enforcement on a minimal fixture.

The 7 files it demonstrates are: ``__init__.py``, ``constants.py``, ``schemas.py``,
``client.py``, ``tools.py``, ``prompts.py``, ``resources.py`` — the pattern
established in Phase 40 and used by every production module since. For a
full-featured reference, see ``src/mcp_canada/modules/british_columbia/`` or
``src/mcp_canada/modules/quebec/``.
"""

MODULE_NAME = "example"
MODULE_DESCRIPTION = "Example module for testing auto-registry (private fixture, not production)"
