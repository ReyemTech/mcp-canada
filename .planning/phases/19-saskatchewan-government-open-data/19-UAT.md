---
status: complete
phase: 19-saskatchewan-government-open-data
source: [19-01-SUMMARY.md, 19-02-SUMMARY.md, 19-03-SUMMARY.md, 19-04-SUMMARY.md, 19-05-SUMMARY.md, 19-06-SUMMARY.md, 19-07-SUMMARY.md]
started: 2026-06-15T00:00:00Z
updated: 2026-06-15T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Module loads & discovery works live (the Manitoba-bug check)
expected: saskatchewan_search_datasets("crops") returns live results from geohub.saskatchewan.ca with numberMatched>0, _meta.source.api="saskatchewan-geohub".
result: pass
note: Live — 8 results, api=saskatchewan-geohub. Discovery works LIVE (startindex fix validated) — no repeat of the Manitoba 400.

### 2. Shared fix didn't break York/Alberta/Manitoba
expected: The Wave 0 shared/arcgis_hub.py offset→startindex fix leaves all prior ArcGIS Hub modules green, and repairs the latent live discovery bug.
result: pass
note: 676 York+Alberta+Manitoba+shared unit tests green (verifier) + 438 independently re-run. Only york_region calls the fixed search_hub_datasets — confirmed york discovery works LIVE now (error=False, real data from insights-york.opendata.arcgis.com). Alberta search is CKAN (q/rows/start), never affected by this bug; Manitoba builds params directly. So the live repair is York Region specifically.

### 3. Crop yields (signature agriculture)
expected: non-null Canola field; region dispatch; invalid region → INVALID_INPUT.
result: pass
note: Live — 2 records; Canola field present (keys: Region, HRSW, Durum, Oat, Barley, Canola, Mustard, Soybean). Invalid region → French INVALID_INPUT confirmed in Test 9.

### 4. Mineral mines dispatch (potash/uranium/helium/coal)
expected: dispatch by mineral; Name/Company/Status; invalid mineral → error.
result: pass
note: Live — potash 10 mines, uranium 6 mines, api=saskatchewan-geohub. Invalid mineral rejected at the Literal type layer (schema validation) before reaching the tool — valid behavior.

### 5. Fire bans — SPSA server + empty=valid
expected: SPSA separate server, scope dispatch, empty=valid success.
result: pass
note: Live — ban_scope=provincial returned count=0 (empty=valid off-season), api=saskatchewan-spsa-firebans (the separate SPSA server, distinct from geohub). Never an error.

### 6. WSA reservoirs uses layer 26 (not empty layer 0)
expected: Reservoir_Name data from WSA org layer 26.
result: pass
note: Live — 66 reservoirs; Reservoir_Name="ADMIRAL RESERVOIR", Dam_Name="ADMIRAL DAM" present, api=saskatchewan-wsa. Layer-26 correctness confirmed live (layer 0 would be empty).

### 7. Air quality (live) + WSA stations
expected: air quality with AQHI; WSA stations with Station_Number + HyperLink_Graph.
result: pass
note: Live — air_quality 6 communities (api=saskatchewan-geohub); wsa_stations 260 stations (api=saskatchewan-wsa). Both return real data.

### 8. Prompts & resources discoverable; deferred domains documented
expected: 6 prompts + 7 zero-parameter resources; portal-guide documents deferred transport+health.
result: pass
note: Live — 6 saskatchewan prompts + 7 resources in listings. portal-guide documents deferred transport (511 key-gated) + health (no SHA FeatureServer).

### 9. French language pass-through
expected: lang="fr" → _meta.lang="fr" and French messages.
result: pass
note: Live — crop_yields region="badregion" lang="fr" returned French error "Région invalide: 'badregion'. Valeurs valides: [...]".

## Summary

total: 9
passed: 9
issues: 0
pending: 0
skipped: 0

## Gaps

[none — all tests passed live]
