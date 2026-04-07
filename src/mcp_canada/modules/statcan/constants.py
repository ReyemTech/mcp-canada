# SSL probe result (Phase 7, 2026-04-07)
# certifi succeeded for statcan.gc.ca — standard certifi bundle validates the certificate
STATCAN_VERIFY: bool = True

# WDS REST API base URL
BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest/"

# Probe URL used during Phase 7 SSL investigation
PROBE_URL = "https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite"

# Rate limiting (Phase 8 will use these)
RATE_GROUP = "statcan"
RATE_LIMIT = 20.0  # requests per second — WDS documented limit is 25 req/s, conservative
