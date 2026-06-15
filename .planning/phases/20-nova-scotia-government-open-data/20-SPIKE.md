# Phase 20 — Wave 0 Spike: Nova Scotia Uncertain Dataset Shapes

**Probed:** 2026-06-15  
**Domain:** data.novascotia.ca (Socrata SODA API, keyless)  
**Status:** All 5 items resolved via live probes

---

## 1. Rockweed leases (exhe-htib) — VERDICT: has tabular fields (NOT geometry-only)

**Probe commands:**

```bash
# Column list
curl -s "https://data.novascotia.ca/api/views/exhe-htib.json" | jq '.columns[] | {fieldName, dataTypeName, name}'

# Sample rows (excluding geometry)
curl -s "https://data.novascotia.ca/resource/exhe-htib.json?$select=ownership,lease_le,hectares&$limit=3"
```

**Column list (4 columns):**

| fieldName | dataTypeName | name |
|-----------|-------------|------|
| the_geom | multipolygon | the_geom |
| ownership | text | Ownership |
| lease_le | text | Lease_Le |
| hectares | number | Hectares |

**Sample rows:**
```json
[
  {"ownership": "Acadian Seaplants Ltd.", "lease_le": "6025", "hectares": "2353.51607014"},
  {"ownership": "Scotia Garden Seafoods Inc.", "lease_le": "6024", "hectares": "76677.6703098"},
  {"ownership": "Scotia Garden Seafoods Inc.", "lease_le": "6028", "hectares": "982.53570995"}
]
```

**Verdict:** Dataset `exhe-htib` **has tabular fields** (ownership, lease_le, hectares), not geometry-only.
However, with only 3 attribute fields (ownership, lease reference, area in hectares) and no county/species/location details,
it provides minimal agent value compared to marine leases (`h57h-p9mm`).

**Decision for Plan 01:** `DS_ROCKWEED_LEASES = "exhe-htib"` is included in constants as a discoverable dataset.
No dedicated curated tool. Agents can discover it via `ns_search_datasets` and query it via `ns_query_dataset`.
The conftest fixture for rockweed can be minimal (just ownership/lease_le/hectares row).

---

## 2. Boil-water active filter — ACTIVE_ADVISORY_FILTER: IS NULL (NULL count=82, empty count=ERROR)

**Probe commands:**

```bash
# IS NULL count
curl -s "https://data.novascotia.ca/resource/7t68-9xmm.json?$select=count(*)&$where=date_advisory_removed%20IS%20NULL"

# IS NOT NULL count (for reference — resolved advisories)
curl -s "https://data.novascotia.ca/resource/7t68-9xmm.json?$select=count(*)&$where=date_advisory_removed%20IS%20NOT%20NULL"

# Empty string attempt
curl -s "https://data.novascotia.ca/resource/7t68-9xmm.json?$select=count(*)&$where=date_advisory_removed%3D''"
```

**Results:**
- `IS NULL` count: **82** (current active advisories as of 2026-06-15)
- `IS NOT NULL` count: **2553** (resolved/lifted advisories)
- `= ''` (empty string): **ERROR** — `query.soql.type-mismatch` — date field does NOT support empty string comparison

**Verdict:** `date_advisory_removed IS NULL` is the correct active advisory filter. The empty string approach
causes a type-mismatch error (date column stores NULL, not empty string, for active advisories).

**ACTIVE_ADVISORY_FILTER = "date_advisory_removed IS NULL"**

This constant is used by Plan 04's `fetch_boil_water_advisories(active_only=True)` implementation.

---

## 3. Chronic-disease zone field map

**Probe commands:**

```bash
# For each disease, get 1 row to see keys
for id in 24qf-ntke cumi-sw99 ua9e-4pss sztc-sewr 2bih-5dgk; do
  echo "=== $id ==="
  curl -s "https://data.novascotia.ca/resource/$id.json?$limit=1" | jq '.[0] | keys'
done
```

**Field name map (live-confirmed 2026-06-15):**

| Disease | Dataset ID | zone field | age field | prevalence field | extra notes |
|---------|-----------|-----------|-----------|-----------------|-------------|
| AMI | 24qf-ntke | `health_zone` | `age_group` | `crude_prevalence_rate` | **NO sex field**; year is plain string ("2000") |
| Diabetes | cumi-sw99 | `zone` | `agegroup` | `crude_prevalence_rate` | sex present; year is ISO timestamp ("2000-01-01T00:00:00.000") |
| COPD | ua9e-4pss | `zone` | `agegroup` | `crude_prevalence_rate` | sex present; year is ISO timestamp |
| Hypertension | sztc-sewr | `zone` | `age_group` | `prevalence_rate` (**different!**) | sex present; uses `hypertension_count` not `prevalence`; year is ISO timestamp |
| Asthma | 2bih-5dgk | `zone` | `age_group` | `crude_prevalence_rate` | sex present; year is ISO timestamp |

**Verdict — zone field normalization:**

```python
# Per-dataset zone field name mapping for _normalize_zone_field in Plan 05
CHRONIC_DISEASE_ZONE_FIELD = {
    "ami": "health_zone",        # DIFFERENT — must be renamed to "zone" in output
    "diabetes": "zone",          # same as target
    "copd": "zone",              # same as target
    "hypertension": "zone",      # same as target
    "asthma": "zone",            # same as target
}

# Per-dataset age group field name mapping
CHRONIC_DISEASE_AGE_FIELD = {
    "ami": "age_group",
    "diabetes": "agegroup",      # DIFFERENT — no underscore
    "copd": "agegroup",          # DIFFERENT — no underscore
    "hypertension": "age_group",
    "asthma": "age_group",
}
```

**Additional schema differences for Plan 05:**

1. **AMI has NO `sex` field** — the tool's `sex` filter must be skipped for disease="ami"
2. **Hypertension uses different field names** for the prevalence count (`hypertension_count`) and rate (`prevalence_rate` not `crude_prevalence_rate`)
3. **Year format varies** — AMI uses plain string year ("2000"), others use ISO timestamp ("2000-01-01T00:00:00.000"). Filter accordingly.
4. **Normalization target** — output should normalize to `zone` (not `health_zone`) and `age_group` (not `agegroup`) for consistent schema

**NovaScotiaChronicDiseaseRow schema** in schemas.py should use nullable fields for differences:
```python
class NovaScotiaChronicDiseaseRow(BaseModel):
    disease: str
    year: str
    zone: str                          # normalized from health_zone (AMI) or zone (others)
    sex: str | None = None             # None for AMI (no sex field)
    age_group: str | None = None       # normalized from age_group or agegroup
    population: float | None = None
    prevalence: float | None = None    # None for hypertension (uses hypertension_count)
    crude_prevalence_rate: float | None = None  # None for hypertension (uses prevalence_rate)
    # hypertension-specific:
    hypertension_count: float | None = None
    prevalence_rate: float | None = None
```

---

## 4. categories= param — VERDICT: resultSetSize=0 (workaround required)

**Probe command:**

```bash
curl -s "https://data.novascotia.ca/api/catalog/v1?domains=data.novascotia.ca&categories=Fishing+and+Aquaculture"
```

**Result:** `resultSetSize: 0` — the `categories=` parameter is broken on this Socrata instance.

**Contrast with working q= search:**
```bash
curl -s "https://data.novascotia.ca/api/catalog/v1?domains=data.novascotia.ca&q=aquaculture&limit=3"
# → resultSetSize: 114
```

**Verdict:** Confirmed broken. All tools that need category-filtered results must use `q=` keyword search
and filter client-side on `classification.domain_category`. Do NOT expose a `category=` tool parameter
without live-testing it first.

---

## 5. Geometry exclusion via $select — VERDICT: the_geom NOT present when excluded

**Probe command:**

```bash
curl -s "https://data.novascotia.ca/resource/h57h-p9mm.json?$select=license_le,county&$limit=1"
```

**Result:**
```json
[{"license_le": "MRL-001", "county": "Inverness"}]
```

**Keys present:** `['license_le', 'county']`  
**`the_geom` present?** `False`

**Verdict:** The `$select` strategy correctly excludes `the_geom` from responses.
All curated tools that fetch from geometry-enabled datasets (marine leases h57h-p9mm, protected areas ticv-5du5)
MUST include explicit `$select` field lists to exclude `the_geom` and control response size.
The `include_geometry` parameter on `fetch_query_dataset` (Plan 03) optionally adds `the_geom` to the `$select` list.

---

## Summary of Verdicts for Plans 02-05

| Item | Verdict | Impact |
|------|---------|--------|
| Rockweed `exhe-htib` | Has tabular fields (3 attributes) but thin — no curated tool | Keep `DS_ROCKWEED_LEASES` in constants; discovery-only via ns_search_datasets/ns_query_dataset |
| Boil-water active filter | `date_advisory_removed IS NULL` (82 active, empty string = type error) | `ACTIVE_ADVISORY_FILTER = "date_advisory_removed IS NULL"` in constants.py |
| AMI zone field | `health_zone` (not `zone`) | `_normalize_zone_field` in Plan 05 renames to `zone` |
| AMI sex field | **ABSENT** | `sex` filter must be skipped for disease="ami" |
| AMI year format | Plain string ("2000") | Year filter: `year='2000'` for AMI, year field in ISO timestamp for others |
| Diabetes zone | `zone` (same as target) | No rename needed |
| Diabetes age field | `agegroup` (no underscore) | Normalize to `age_group` |
| COPD zone | `zone` | No rename needed |
| COPD age field | `agegroup` | Normalize to `age_group` |
| Hypertension zone | `zone` | No rename needed |
| Hypertension age field | `age_group` | Same as target |
| Hypertension rate fields | `hypertension_count` + `prevalence_rate` (not standard names) | Passthrough; schema model uses nullable fields |
| Asthma zone | `zone` | No rename needed |
| Asthma age field | `age_group` | Same as target |
| `categories=` param | Broken — returns 0 results | Use `q=` + client-side `domain_category` filter |
| `$select` strips geometry | Confirmed — `the_geom` absent when not in $select | All curated geometry-dataset tools must use explicit $select |
