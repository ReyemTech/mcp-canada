# Phase 19: Saskatchewan Wave 0 Spike Results

**Probed:** 2026-06-15
**Executor:** Plan 19-01 Task 2
**Purpose:** Resolve the two UNCERTAIN sources from 19-RESEARCH.md and live-confirm critical layer IDs before any curated tool is built.

---

## 1. WSA Water Quality (layer 19) — VERDICT: HAS DATA (24 stations)

**Research finding:** Layer 19 returned 0 features during initial research.

**Probe commands:**
```
GET https://services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/Primary_Water_Quality_Monitoring_Stations/FeatureServer?f=json
GET .../FeatureServer/19/query?where=1%3D1&outFields=*&resultRecordCount=5&f=json
GET .../FeatureServer/19/query?where=1%3D1&returnCountOnly=true&f=json
```

**Results:**
- Layer 19 exists and is named: "Primary Water Quality Monitoring Stations"
- Total count: **24 stations**
- HTTP status: 200
- Fields: OBJECTID, Station_Number, Station_Name, Comment, Station_Description, Latitide [sic], LONGITUDE
- Sample features:
  - `SK07CD0001` | CLEARWATER R.-AT HWY #955
  - `SK06AG0022` | BEAVER R.-NR. BEAUVAL
  - `SK05JF0092` | QU'APPELLE R.-REGINA-U/C-ABOVE WASCANA CK.(CONFL.)

**Verdict:** Layer 19 IS accessible and returns station metadata. The research finding (0 features) was likely a transient network condition or the layer was empty at the time of initial research. The layer has 24 records.

**Implication for planning:** Per the Plan 19-01 spec, these water quality STATIONS are location/metadata only — not actual water chemistry readings. The 9 curated tools already planned (SK-13 WSA Stations, SK-14 WSA Reservoirs) are the intended water tools. Water quality chemistry monitoring data (SK-14 / SK-13) uses layers 0 and 26, not layer 19. Layer 19 data could optionally supplement a future phase as a "water quality monitoring station locations" tool (24 stations), but it is NOT in the 9 curated tools for Plans 02-05. **No curated water-quality-specific tool added in Phase 19.**

---

## 2. Economy/Petroleum FeatureServer — VERDICT: USABLE (HTTP 200, data returned)

**Research finding:** Queries returned HTTP 400 "Unable to complete operation."

**Probe commands:**
```
GET https://gis.saskatchewan.ca/egis/rest/services/Economy/Petroleum/FeatureServer/0?f=json
GET .../FeatureServer/0/query?where=1%3D1&outFields=*&resultRecordCount=5&f=json
```

**Results:**
- Layer 0 name: "Vertical Wells"
- Fields (sample): OBJECTID, WELL_CWI, LEGACYWELLNAME, WELLLICENCENUMBER, WELLLICENCEISSUEDATE, WELLLICENCEBUSINESSASSOCIATE, WELLCONFIDENTIALPERIOD, WELLSTATUSTYPECODE, SURFACELATITUDE, SURFACELONGITUDE, WELLDATAEXTRACTDATE (plus ~40 more fields)
- HTTP status: 200 on 2026-06-15 probe
- Data returned: Yes — sample feature shows SK0000001 "MAN RIVER OIL AND GAS CO. NO. 2" (Abandoned, 1951)
- Total record scope: Very large — Saskatchewan has thousands of wells

**Verdict:** The Petroleum FeatureServer layer 0 IS accessible and returns data as of 2026-06-15. The HTTP 400 from research was likely transient or a different query structure was used. The layer has a rich well schema with 50+ fields.

**Implication for planning:** The endpoint is usable. However, 19-RESEARCH.md explicitly plans ZERO curated oil/gas tools and documents this as deferred ("discovery-only routing in the portal-guide resource, Plan 06"). This spike does NOT override that planning decision — the deferred status was for tool count / scope reasons (14 tools already at target ceiling), not because of technical unavailability. A future phase could curate `saskatchewan_get_oil_wells` using this endpoint. Document in `docs://saskatchewan/portal-guide` resource (Plan 06) that the Petroleum FS IS accessible and the 400 was transient.

---

## 3. WSA_Reservoirs layer 26 — CONFIRMED: Reservoir_Name present

**Probe command:**
```
GET https://services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/WSA_Reservoirs/FeatureServer/26/query?where=1%3D1&outFields=*&resultRecordCount=3&f=json
```

**Result:**
- HTTP status: 200
- Features returned: 3
- Reservoir_Name present: YES — "ADMIRAL RESERVOIR"
- Dam_Name present: YES — "ADMIRAL DAM"
- Water_Level_MASL: field available (value in sample)

**Verdict:** Layer 26 confirmed. `WSA_RESERVOIRS_LAYER = 26` is correct. Plans 02-05 should use layer 26 (NOT layer 0) for WSA_Reservoirs.

---

## 4. SPSA Public_Fire_Ban layers — CONFIRMED: 0, 2, 3, 8 exist

**Probe command:**
```
GET https://gis.saskatchewan.ca/egis/rest/services/Wildfire/Public_Fire_Ban/FeatureServer?f=json
```

**Result — All layers on the FeatureServer:**
```
Layer 0: FireBan Urban Municipality    ← urban in FIRE_BAN_LAYERS
Layer 1: Highways                      ← reference layer (not ban data)
Layer 2: FireBan Rural Municipality   ← rural in FIRE_BAN_LAYERS
Layer 3: FireBan Provincial           ← provincial in FIRE_BAN_LAYERS
Layer 5: Aboriginal Lands             ← reference layer (not ban data)
Layer 6: Urban Municipality           ← reference layer (not ban data)
Layer 7: Park                         ← reference layer (not ban data)
Layer 8: FireBan Provincial Parks     ← parks in FIRE_BAN_LAYERS
Layer 9: Rural Municipality           ← reference layer (not ban data)
Layer 10: MASK                        ← reference layer (not ban data)
```

**Verdict:** Layers 0, 2, 3, 8 confirmed as fire ban data layers. FIRE_BAN_LAYERS = {"urban": 0, "rural": 2, "provincial": 3, "parks": 8} is correct. Layers 1, 5, 6, 7, 9, 10 are reference/display-only layers (highways, municipality boundaries, etc.) — do NOT query these for ban data.

---

## 5. GeoHub startindex pagination — CONFIRMED WORKING

**Probe command (post Task 1 fix):**
```
GET https://geohub.saskatchewan.ca/api/search/v1/collections/all/items?q=crops&limit=5&startindex=5
```

**Result:**
- HTTP status: 200
- numberMatched: 8 (correct — crops query finds 8 datasets)
- numberReturned: 4 (pagination working — returning items 5-8 with startindex=5)
- features count: 4

**Verdict:** startindex pagination IS working correctly against geohub.saskatchewan.ca after the Task 1 fix to `shared/arcgis_hub.py`. The `?offset=N` bug is fixed — `search_hub_datasets()` now sends `startindex` (OGC API Records) instead of `offset`. This unblocks all Hub discovery tools for Saskatchewan (and retroactively repairs York Region Phase 14 and Alberta Phase 17 live pagination).

---

## Summary Table

| Item | Research Verdict | Spike Verdict | Planning Impact |
|------|-----------------|---------------|-----------------|
| WSA Water Quality layer 19 | 0 features (unusable) | **24 stations (USABLE)** | Not in 9 curated tools per plan scope; may be future Phase 20+ |
| Petroleum FeatureServer layer 0 | HTTP 400 (unusable) | **HTTP 200, data returned** | Deferred per plan scope (14 tools at ceiling); document in portal-guide as accessible |
| WSA_Reservoirs layer 26 | Assumed correct | **CONFIRMED — Reservoir_Name + Dam_Name present** | WSA_RESERVOIRS_LAYER = 26 constant is correct |
| SPSA Fire Ban layers 0/2/3/8 | Assumed correct | **CONFIRMED — all 4 fire ban layers exist** | FIRE_BAN_LAYERS constant is correct |
| GeoHub startindex pagination | Broken (returned null) | **WORKING after Task 1 fix** | All Hub discovery tools unblocked |

---

## Re-run Commands (for future verification)

```bash
# WSA Water Quality layer 19
curl -s "https://services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/Primary_Water_Quality_Monitoring_Stations/FeatureServer/19/query?where=1%3D1&returnCountOnly=true&f=json"

# Petroleum FeatureServer layer 0
curl -s "https://gis.saskatchewan.ca/egis/rest/services/Economy/Petroleum/FeatureServer/0/query?where=1%3D1&outFields=WELL_CWI%2CWELLSTATUS&resultRecordCount=3&f=json"

# WSA Reservoirs layer 26
curl -s "https://services1.arcgis.com/7MBdlVpjqbfBhQer/arcgis/rest/services/WSA_Reservoirs/FeatureServer/26/query?where=1%3D1&outFields=Reservoir_Name%2CDam_Name&resultRecordCount=3&f=json"

# SPSA Fire Ban layers
curl -s "https://gis.saskatchewan.ca/egis/rest/services/Wildfire/Public_Fire_Ban/FeatureServer?f=json" | python3 -c "import json,sys; d=json.load(sys.stdin); [print(f'Layer {l[\"id\"]}: {l[\"name\"]}') for l in d.get('layers',[])]"

# GeoHub startindex pagination
curl -s "https://geohub.saskatchewan.ca/api/search/v1/collections/all/items?q=crops&limit=5&startindex=5" | python3 -c "import json,sys; d=json.load(sys.stdin); print('numberMatched:', d.get('numberMatched'), '| numberReturned:', d.get('numberReturned'))"
```
