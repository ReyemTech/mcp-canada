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
#
# Transcribed verbatim from StatCan's published code set:
#   https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets → object.frequency
# There is no code 3, 5, 8, or 10 — do not fill the gaps. Codes are NOT
# contiguous and NOT ordered by period length.
#
# Verified against live getCodeSets 2026-07-25. `sc_get_code_sets` proxies the
# same endpoint at runtime, so any drift here makes the server contradict itself;
# TestStatCanCodeSetDrift (integration) fails if upstream changes.
FREQUENCY_CODES: dict[int, str] = {
    1: "Daily",
    2: "Weekly",
    4: "Biweekly",
    6: "Monthly",
    7: "Bimonthly",
    9: "Quarterly",
    11: "Semi-annual",
    12: "Annual",
    13: "Every 2 years",
    14: "Every 3 years",
    15: "Every 4 years",
    16: "Every 5 years",
    17: "Every 10 years",
    18: "Occasional",
    19: "Occasional Quarterly",
    20: "Occasional Monthly",
    21: "Occasional Daily",
}

# ---------------------------------------------------------------------------
# SDMX REST API constants (Phase 9)
# ---------------------------------------------------------------------------

# SDMX REST base URL — separate from WDS REST API
SDMX_BASE_URL = "https://www150.statcan.gc.ca/t1/wds/sdmx/statcan/rest/"

# API name for SDMX envelope responses
_SDMX_API_NAME = "statcan-sdmx"

# XML namespaces for SDMX 2.1 structure messages
# Must be passed to every ElementTree find/findall call (Pitfall 3)
SDMX_XML_NAMESPACES: dict[str, str] = {
    "mes": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "str": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
    "com": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}

# ---------------------------------------------------------------------------
# Scalar factor codes (WDS scalarFactorCode → human-readable label)
# ---------------------------------------------------------------------------

# Scalar factor codes (WDS scalarFactorCode → human-readable label)
# Scalar factor codes (WDS scalarFactorCode → magnitude multiplier label)
#
# Transcribed verbatim from StatCan's published code set:
#   https://www150.statcan.gc.ca/t1/wds/rest/getCodeSets → object.scalar
# Code N means 10^N — the set is exactly 0-9, strictly ascending. There is no
# 888 entry. Verified against live getCodeSets 2026-07-25.
SCALAR_FACTOR_CODES: dict[int, str] = {
    0: "units",
    1: "tens",
    2: "hundreds",
    3: "thousands",
    4: "tens of thousands",
    5: "hundreds of thousands",
    6: "millions",
    7: "tens of millions",
    8: "hundreds of millions",
    9: "billions",
}
