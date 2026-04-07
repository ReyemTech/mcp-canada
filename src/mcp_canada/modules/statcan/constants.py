# SSL probe result (Phase 7, 2026-04-07)
# certifi succeeded for statcan.gc.ca — standard certifi bundle validates the certificate
STATCAN_VERIFY: bool = True

# WDS REST API base URL
BASE_URL = "https://www150.statcan.gc.ca/t1/wds/rest/"

# Probe URL used during Phase 7 SSL investigation
PROBE_URL = "https://www150.statcan.gc.ca/t1/wds/rest/getAllCubesListLite"

# Rate limiting
RATE_GROUP = "statcan"
RATE_LIMIT = 20.0  # requests per second — WDS documented limit is 25 req/s, conservative

# Timeout for large payloads (getAllCubesListLite is ~5MB)
TIMEOUT_LARGE = 90.0  # seconds — generous for slow connections

# Cache TTLs (seconds)
CACHE_TTL_CUBES = 3600       # 1 hour — cube list changes infrequently
CACHE_TTL_META = 86400       # 24 hours — cube metadata is stable
CACHE_TTL_CODESETS = 604800  # 7 days — code sets rarely change
CACHE_TTL_OBS = 3600         # 1 hour — observations refresh frequently

# API name for envelope responses
_API_NAME = "statcan-wds"

# Frequency codes (WDS frequencyCode → human-readable label)
FREQUENCY_CODES: dict[int, str] = {
    1: "Daily",
    2: "Weekly (Sunday)",
    4: "Bi-weekly",
    5: "Monthly",
    6: "Bi-monthly",
    7: "Quarterly",
    8: "Semi-annual",
    9: "Annual",
    10: "Every 2 years",
    11: "Every 3 years",
    12: "Irregular",
    13: "Every 2 years",
}

# Scalar factor codes (WDS scalarFactorCode → human-readable label)
SCALAR_FACTOR_CODES: dict[int, str] = {
    0: "units",
    1: "thousands",
    2: "millions",
    3: "billions",
    4: "trillions",
    5: "tens",
    6: "hundreds",
    7: "tens of thousands",
    8: "hundreds of thousands",
    9: "billions",
    888: "null",
}
