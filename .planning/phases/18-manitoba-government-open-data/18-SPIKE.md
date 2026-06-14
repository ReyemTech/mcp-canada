# Phase 18: Wave 0 Spike — Manitoba Open Questions

**Spike date:** 2026-06-14
**Purpose:** Resolve 4 open questions from 18-RESEARCH.md before writing constants, so Task 2 hardcodes concrete URLs.

---

## 1. Manitoba 511 key — VERDICT: gated (account required + key request)

**What was probed:**

- `https://www.manitoba511.ca/api/v3/get/events` (no key) → HTTP 400, body: `<Error><Message>Invalid Key</Message></Error>`
- `https://www.manitoba511.ca/developers/doc` (HTML) → Page confirms: "A registered account is needed before you can sign up for a Developer API key."

**Findings:**

- The API strictly requires a `key` query parameter. Without it: HTTP 400, XML error.
- Registration is a two-step process: (1) create a free account at `/my511/register`, (2) request a developer API key (not auto-provisioned — must be explicitly requested via the developer panel after login).
- The word "free" appears in the page context only for "Free Apps", not for the API key. Key provisioning appears to involve a manual review/issuance step.
- Rate limit: 10 calls/60 seconds (documented).

**Verdict:** GATED — requires account signup + explicit API key request. Key is NOT instantly provisioned without registration. This is an auth-gated endpoint under mcp-canada project policy (similar to DataStream).

**Implementation consequence for Plan 06:**
- Include 3 transport tools (`manitoba_get_road_events`, `manitoba_get_winter_road_conditions`, `manitoba_get_traffic_cameras`) as planned.
- Each tool reads key from `os.environ.get("MANITOBA_511_KEY", "")`.
- If key absent: return `make_error("NOT_CONFIGURED", "Manitoba 511 API key required. Register at https://www.manitoba511.ca/my511/register then request a developer key.", lang=lang)`.
- Tests mock the key via `monkeypatch.setenv("MANITOBA_511_KEY", "test-key-123")`.

**Re-probe command (if policy changes):**

```bash
curl -s "https://www.manitoba511.ca/api/v3/get/events?key=YOUR_KEY&format=json" \
  -H "User-Agent: mcp-canada/1.0"
```

---

## 2. Rural Health Care Facilities FS — RESOLVED

**Probe method:**

```bash
# 1. Hub Search found: Web Mapping Application (id=0494058c6d8d437d8cd31c22b4253285)
curl -s "https://geoportal.gov.mb.ca/api/search/v1/collections/all/items?q=rural+health+care+facilities&limit=5" \
  -H "User-Agent: mcp-canada/1.0"
# Result: 1 item — Web Mapping Application, not a FeatureServer item directly

# 2. Inspect app's data config to find underlying FeatureServer
curl -s "https://www.arcgis.com/sharing/rest/content/items/0494058c6d8d437d8cd31c22b4253285/data?f=json" \
  -H "User-Agent: mcp-canada/1.0"
# Found FeatureServer URL in app config
```

**Result:** RESOLVED — live-verified.

| Property | Value |
|----------|-------|
| **FeatureServer URL** | `https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/Rural_Health_Care_Facilities_in_Manitoba/FeatureServer` |
| **Layer ID** | `0` |
| **Layer name** | `Rural_Health_Care_Facilities_in_Manitoba` |
| **Max records** | 2000 |
| **Auth required** | None |

**Confirmed fields (first 10):** `OBJECTID`, `Community_Name`, `Facility_Name`, `Lat`, `Long`, `Emergency_Department_Availabili`, `Percentage_of_Time_Open__2015_`, `Nearest_Alternate_Emergency_Dep`, `Acute_Care_Availability`, `Acute_Care_Number_of_Beds`

Note: Field names are truncated (ArcGIS 30-char limit). `Emergency_Department_Availabili` = Emergency Department Availability. Full field list likely includes Transitional Care, Diagnostic Services, PCH per research.

**Constant to hardcode:**

```python
RURAL_HEALTH_FACILITIES_FS_URL: Final[str] = (
    f"{HUB_ORG_BASE}/Rural_Health_Care_Facilities_in_Manitoba/FeatureServer"
)
```

---

## 3. Hog prices FS — UNRESOLVED — fall back to discovery

**Probe method:**

```bash
# 1. Full service list from mMUesHYPkXjaFGfS org (82 total services)
curl -s "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services?f=json" \
  -H "User-Agent: mcp-canada/1.0"

# 2. Hub search
curl -s "https://geoportal.gov.mb.ca/api/search/v1/collections/all/items?q=hog+prices&limit=10" \
  -H "User-Agent: mcp-canada/1.0"
curl -s "https://geoportal.gov.mb.ca/api/search/v1/collections/all/items?q=hog+market+price&limit=10" \
  -H "User-Agent: mcp-canada/1.0"
```

**Findings:**

- The `mMUesHYPkXjaFGfS` org lists 82 services. None contain "hog", "pig", or "swine" in the service name.
- Hub searches for "hog prices", "hog market price", and "livestock price" all return only `MB_Cattle_Prices_Current_year` — no separate hog prices service found.
- Research noted the hog prices service on Open Canada (dataset `f650f572`) but the underlying ArcGIS service name is not resolvable from sandbox (Open Canada HTML page does not expose the FeatureServer URL directly).

**Verdict:** UNRESOLVED — no `MB_Hog_Prices_*` service found in the `mMUesHYPkXjaFGfS` org under any variant name. The hog prices dataset may be:
  1. On a different ArcGIS org (e.g., `agrimaps.gov.mb.ca/arcgis/rest/services/AGRIMAPS/`)
  2. Published as a table within `MB_Cattle_Prices_Current_year` with a `livestock` type field that covers both cattle and hogs
  3. In a private/unlisted service not in the public services directory

**Fallback strategy:** Plan 04 should:
1. First check if `MB_Cattle_Prices_Current_year` layer contains rows for both cattle and hogs (query with `where=1=1&outFields=Parameter,Measure&resultRecordCount=10` to inspect).
2. If mixed: `manitoba_get_livestock_prices` dispatches by filtering `Parameter LIKE '%hog%'` or `Parameter LIKE '%cattle%'`.
3. If cattle-only: implement `livestock: Literal["cattle"]` only, document hog prices as NOT_FOUND in tool docstring with link to Open Canada dataset `f650f572`.

**Re-probe command:**

```bash
# Check if cattle prices table also has hog data
curl -s "https://services.arcgis.com/mMUesHYPkXjaFGfS/arcgis/rest/services/MB_Cattle_Prices_Current_year/FeatureServer/0/query?where=1%3D1&outFields=Parameter%2CMeasure%2CAuction&resultRecordCount=20&f=json" \
  -H "User-Agent: mcp-canada/1.0"

# Check AgriMaps for hog prices
curl -s "https://agrimaps.gov.mb.ca/arcgis/rest/services/AGRIMAPS?f=json" \
  -H "User-Agent: mcp-canada/1.0" | python3 -c "import sys,json; d=json.load(sys.stdin); [print(s['name']) for s in d.get('services',[]) if 'hog' in s['name'].lower() or 'livestock' in s['name'].lower()]"
```

**Constant to hardcode:**

```python
# Hog prices: unresolved in Wave 0 spike — Plan 04 resolves via cattle layer inspection
# HOG_PRICES_FS_URL: None  # UNRESOLVED — see 18-SPIKE.md § 3
# Sentinel: use cattle service as starting point; Plan 04 adds HOG_PRICES_FS_URL if separate service found
HOG_PRICES_FS_URL: Final[str | None] = None  # UNRESOLVED — fall back to discovery
```

---

## 4. River Conditions FS — RESOLVED (CSV, not FeatureServer)

**Probe method:**

```bash
# Inspect web app item data
curl -s "https://www.arcgis.com/sharing/rest/content/items/5c57801d0efc4676a2d2c95174ef44d5/data?f=json" \
  -H "User-Agent: mcp-canada/1.0"
# Found: refers to webmap id=bbe85e66f11a44aeadf1c95fadb5871d

# Inspect the webmap
curl -s "https://www.arcgis.com/sharing/rest/content/items/bbe85e66f11a44aeadf1c95fadb5871d/data?f=json" \
  -H "User-Agent: mcp-canada/1.0"
```

**Findings:** The Manitoba River Conditions web app has **two operational layers**, both pointing to the same CSV:

| Layer title | Layer type | URL |
|-------------|-----------|-----|
| Hydrometric Station (Flood Alert) | CSV | `https://www.manitoba.ca/floodinfo/floodoutlook/forecast_centre/agol/agoldataV2.csv` |
| Flood Alerts | CSV | `https://www.manitoba.ca/floodinfo/floodoutlook/forecast_centre/agol/agoldataV2.csv` |

**There is no FeatureServer backing these layers.** The "river conditions" data is a live CSV feed published by Manitoba Infrastructure's Hydrologic Forecast Centre at `www.manitoba.ca`.

**CSV confirmed accessible** (2026-06-14 live probe). Fields (confirmed from first rows):

```
id, stationId, stationName, latitude, longitude, measurementDate,
measuredFlow, measuredLevel, forecastedFlow, forecastedLevel,
forecastedPeakDate, floodStage, bankFullCapacityFlow, bankFullCapacityLevel,
warningTriggerLevel, highWaterAdvisoryLevel, referenceYears,
alert, wscRealTimeData, dateRecorded, waterLevel, discharge,
datumAdjustment, remarks, source, province, other,
averagingPeriod, overwriteAlert, updated
```

Alert values seen: "No Current Data", "No Flooding". Other values expected: "High Water Advisory", "Flood Watch", "Flood Warning".

**Verdict:** RESOLVED — use `fetch_and_parse` (CSV) instead of `arcgis_hub.query_feature_service`.

**Constant to hardcode:**

```python
# River Conditions: CSV feed (NOT a FeatureServer)
RIVER_CONDITIONS_CSV_URL: Final[str] = (
    "https://www.manitoba.ca/floodinfo/floodoutlook/forecast_centre/agol/agoldataV2.csv"
)
# Note: RIVER_CONDITIONS_FS_URL does NOT exist — this is a CSV, not ArcGIS FeatureServer.
# Plan 03 uses: fetch_and_parse(RIVER_CONDITIONS_CSV_URL, ttl=CACHE_TTL_LIVE)
```

**Impact on schemas:** `ManitobaRiverStation` should use CSV field names (snake_case mapping):
- `station_id` (stationId), `station_name` (stationName), `latitude`, `longitude`
- `alert` (the flood status field — "No Flooding" / "High Water Advisory" / "Flood Watch" / "Flood Warning" / "No Current Data")
- `measured_level`, `measured_flow`, `flood_stage`, `warning_trigger_level`

---

## Summary

| Question | Status | Key Finding |
|----------|--------|-------------|
| Manitoba 511 key | GATED | Account + explicit key request required; tools ship with NOT_CONFIGURED fallback |
| Rural Health FeatureServer | RESOLVED | `Rural_Health_Care_Facilities_in_Manitoba/FeatureServer/0` — live-verified |
| Hog prices FeatureServer | UNRESOLVED | Not found in `mMUesHYPkXjaFGfS` org; Plan 04 investigates cattle layer or AgriMaps |
| River Conditions FeatureServer | RESOLVED (CSV) | Not a FeatureServer — live CSV at `www.manitoba.ca/floodinfo/.../agoldataV2.csv` |
