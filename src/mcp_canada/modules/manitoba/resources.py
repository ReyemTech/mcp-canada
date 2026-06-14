"""Manitoba module resources.

All @resource definitions are added by Plan 07.
This file exists to satisfy FileSystemProvider discovery.

Resource naming convention: URI prefix data://manitoba/, docs://manitoba/, template://manitoba/.
Every @resource must have ZERO function parameters (lang param would promote to ResourceTemplate).
data:// resources return json.dumps(...). docs:// return markdown strings.
"""

import json  # noqa: F401 — used by Plan 07

from fastmcp.resources import resource  # noqa: F401 — used by Plan 07

# Resource definitions added by Plan 07.
