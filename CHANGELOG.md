# Changelog

<!-- CHANGELOG -->

## v0.12.0 (2026-08-24)

### Chores

- Sync uv.lock after release
  ([`bd47070`](https://github.com/ReyemTech/mcp-canada/commit/bd47070e2a7cbc9e149bd71b22a0d966a66755ba))

### Documentation

- **21**: Record PR #6 merge and v0.11.0 release in STATE.md
  ([`415e6ad`](https://github.com/ReyemTech/mcp-canada/commit/415e6ad2d27eec3cb2b4fd2d50600ef67a007689))

### Features

- Add static documentation site
  ([`29d6492`](https://github.com/ReyemTech/mcp-canada/commit/29d64921b8c1633d181697401a14491948fd8976))


## v0.11.0 (2026-07-31)

### Bug Fixes

- **21**: CR-01 close FILTER_REQUIRED guard bypass (whitespace + LIKE wildcards)
  ([`84192e3`](https://github.com/ReyemTech/mcp-canada/commit/84192e31cee532e1e3e75a50e67f2bc9af03211b))

- **21**: F1 reject delimiter-breaking extra_fq in NB CKAN discovery
  ([`264449c`](https://github.com/ReyemTech/mcp-canada/commit/264449c0fa62f739a06cf6cfce5ba727d8652d70))

- **21**: F2 clamp limit to [1, MAX_RECORDS] centrally in _geonb_query
  ([`3ecf46f`](https://github.com/ReyemTech/mcp-canada/commit/3ecf46f2dda7c4b85e4ec3728e390f2da9e9d84b))

- **21**: F3 reject non-positive limit in NB gnb.socrata.com queries
  ([`193c091`](https://github.com/ReyemTech/mcp-canada/commit/193c091b5d5ae37984a99e396053ed3f6f5b471d))

- **21**: F4 include Latitude/Longitude in nb_get_contaminated_sites
  ([`6e81ebe`](https://github.com/ReyemTech/mcp-canada/commit/6e81ebe7b1b5b3a6400ce2e6fad8bce785eafd6b))

- **21**: F5 include LATITUDE/LONGITUDE/COUNTY/PID in nb_get_civic_addresses
  ([`4964e77`](https://github.com/ReyemTech/mcp-canada/commit/4964e779329115da5fece5e372fabec5a4fe2b05))

- **21**: G1 scope package_show to the NB organization
  ([`b5120aa`](https://github.com/ReyemTech/mcp-canada/commit/b5120aa70a56440428a879eae3ec4c3103089a1e))

- **21**: G2 cap fetch_query_dataset limit at MAX_RECORDS
  ([`820855a`](https://github.com/ReyemTech/mcp-canada/commit/820855a795914b63b8d17dafaa13509eb54eedab))

- **21**: G3 update stale MODULE_DESCRIPTION for four upstream surfaces
  ([`af307ec`](https://github.com/ReyemTech/mcp-canada/commit/af307ec0a322ab2376e02a3f001e99df14690d52))

- **21**: G4 correct nb_flood_risk_assessment's unexecutable workflow
  ([`9c24fae`](https://github.com/ReyemTech/mcp-canada/commit/9c24faebdc689869483cdbf73d00fe68b3e57768))

- **21**: IN-01 import schemas.py into client.py, matching sibling-module noqa convention
  ([`734f54b`](https://github.com/ReyemTech/mcp-canada/commit/734f54b4873735b13e0e751b9fd4beadd7bb7d2a))

- **21**: Make nb_crown_land_report's county argument executable
  ([`533c69f`](https://github.com/ReyemTech/mcp-canada/commit/533c69f787d9d2ac32851a404886567be63fb06a))

- **21**: Treat whitespace-only extra_fq as absent, not a malformed Lucene clause
  ([`499a76c`](https://github.com/ReyemTech/mcp-canada/commit/499a76cc53dbcd1c303711b5376d213fd103a75f))

- **21**: WR-01 parenthesize fq conjunction so NB org scope can't be escaped by operator precedence
  ([`791f30b`](https://github.com/ReyemTech/mcp-canada/commit/791f30b52f9d6eabc063a9f7dfa8ebb04fd5c18a))

- **21**: WR-02 echo clamped limit/offset actually sent upstream, not caller's raw values
  ([`f9626dd`](https://github.com/ReyemTech/mcp-canada/commit/f9626ddff9e0f8f135c8480a6b3396ba388be7fa))

- **21**: WR-03 reject non-positive limit in nb_query_dataset before any network call
  ([`2ff6931`](https://github.com/ReyemTech/mcp-canada/commit/2ff69315489377e8cfe99d96dd2b1f32a47344e5))

- **21**: WR-04 strengthen nb_ tool-name guard beyond bare startswith check
  ([`a32b398`](https://github.com/ReyemTech/mcp-canada/commit/a32b39878947493430004802f78bc8bc391b3495))

### Chores

- Sync uv.lock after release
  ([`d92c6a9`](https://github.com/ReyemTech/mcp-canada/commit/d92c6a9041ef447a4e679305452a8a72c1835dc3))

### Documentation

- **21**: Add code review fix report
  ([`ba73712`](https://github.com/ReyemTech/mcp-canada/commit/ba7371231150f7b879446adfddf6ea9f7d420969))

- **21**: Add code review report
  ([`72e5c97`](https://github.com/ReyemTech/mcp-canada/commit/72e5c979cefb27f3e474d3f317bc833089ad7518))

- **21**: Add round-2 code review fix report
  ([`90434c1`](https://github.com/ReyemTech/mcp-canada/commit/90434c169b24d0d9590da78a8040c5e176295158))

- **21**: Add validation strategy
  ([`ddefa28`](https://github.com/ReyemTech/mcp-canada/commit/ddefa280b37ebd9bda8921608cc032aed547c25d))

- **21**: Context for New Brunswick Government Open Data
  ([`6aee36c`](https://github.com/ReyemTech/mcp-canada/commit/6aee36c97d31203c077febcb5b9d415fe78e5c68))

- **21**: Create phase plan
  ([`5c62b79`](https://github.com/ReyemTech/mcp-canada/commit/5c62b798d84ab5ac8c912a688c716553e454a963))

- **21**: Plan New Brunswick phase — 7 plans, 6 waves, 22 tools
  ([`71d8459`](https://github.com/ReyemTech/mcp-canada/commit/71d84594472cbc68319c544258b4d655cbd27e04))

- **21**: Reopen and re-close T-21-03/T-21-04 after Codex review of PR #6
  ([`5660496`](https://github.com/ReyemTech/mcp-canada/commit/5660496c88a57764b1431c09547e9b4729a94003))

- **21**: Research New Brunswick Government Open Data
  ([`e2d4dd9`](https://github.com/ReyemTech/mcp-canada/commit/e2d4dd93956fafc81cbf9b5c29171847127eabb7))

- **21-01**: Add plan 01 summary
  ([`d6de3de`](https://github.com/ReyemTech/mcp-canada/commit/d6de3de5d0fe4f1ad22fa25db28e30fb55d5c21b))

- **21-01**: Append self-check results to plan 01 summary
  ([`25c3ab9`](https://github.com/ReyemTech/mcp-canada/commit/25c3ab9dc4da146f4103b78323d66c142ca74810))

- **21-01**: Complete New Brunswick wave 0 scaffold plan
  ([`a7db209`](https://github.com/ReyemTech/mcp-canada/commit/a7db2093aad5026d115de5766675f07ec4b847cf))

- **21-01**: Live-verify all 11 curated GeoNB layer ids in 21-SPIKE.md
  ([`52ce8b0`](https://github.com/ReyemTech/mcp-canada/commit/52ce8b0ac42f96f2816aee5cb0b360b3b790fa0a))

- **21-02**: Complete federal CKAN discovery plan
  ([`2af864d`](https://github.com/ReyemTech/mcp-canada/commit/2af864d8f849671e6005eb5864e5b8c7324b28a4))

- **21-03**: Complete New Brunswick prompts and resources plan
  ([`def7e19`](https://github.com/ReyemTech/mcp-canada/commit/def7e19135853cf0de7cdcc51ac3004c89593ef1))

- **21-04**: Complete GeoNB discovery + flood/water plan
  ([`5ddd3ea`](https://github.com/ReyemTech/mcp-canada/commit/5ddd3eaa79a42435f02c2b106c71285bcbacf82e))

- **21-05**: Complete parcels and civic addresses plan
  ([`a3a5bc8`](https://github.com/ReyemTech/mcp-canada/commit/a3a5bc880be27701640dcdea1fae6a50935cd4e0))

- **21-06**: Complete health/education/transport plan
  ([`2c28893`](https://github.com/ReyemTech/mcp-canada/commit/2c2889344d52713ec9d9706da46fd6903dc8ea62))

- **21-07**: Complete New Brunswick integration coverage and docs sync plan
  ([`2e475fd`](https://github.com/ReyemTech/mcp-canada/commit/2e475fd7efaf3ae750a7cb4641d625b0d30ca212))

- **21-07**: Register NB-01..NB-25 requirements and resolve COVERAGE.md Surface 5
  ([`898a68e`](https://github.com/ReyemTech/mcp-canada/commit/898a68e34991615703a1be7a9b5de51407f1c849))

- **21-07**: Sync catalogue and correct New Brunswick documentation
  ([`bf2b9d5`](https://github.com/ReyemTech/mcp-canada/commit/bf2b9d5d6b50b7283d70259edd50ad0b64e9dde1))

- **phase-21**: Add security threat verification
  ([`5ffea24`](https://github.com/ReyemTech/mcp-canada/commit/5ffea247ea3e22d1c7eb8cb5abf9272e55e1157b))

- **phase-21**: Complete phase execution
  ([`a5bb452`](https://github.com/ReyemTech/mcp-canada/commit/a5bb45246638efd9650e966cf0a6f907e53d483c))

- **phase-21**: Evolve PROJECT.md after phase completion
  ([`5f52caa`](https://github.com/ReyemTech/mcp-canada/commit/5f52caa4be24572d75bc9caba8bd4462df958cbf))

- **phase-21**: Resolve stale STATE.md checkpoint and focus entries
  ([`60b4113`](https://github.com/ReyemTech/mcp-canada/commit/60b4113a474b3b12f240b6fc1812f88eef544f20))

- **planning**: Backfill PLAN and SUMMARY for phases 20.2-20.4
  ([`1217bd4`](https://github.com/ReyemTech/mcp-canada/commit/1217bd4dbd6d2bb8d55d5d85027ebc39a58c81a9))

- **planning**: Re-stamp 20.2-20.4 verification dates
  ([`6883130`](https://github.com/ReyemTech/mcp-canada/commit/6883130e18b4058638f9abd61eacd06672b82ab4))

- **state**: Close Phase 20.4 — merged to main
  ([`45871d7`](https://github.com/ReyemTech/mcp-canada/commit/45871d7ba7de9c478b43c7ee3678ab364d9508c4))

### Features

- **21-01**: Expand new_brunswick scaffold to full contract surface
  ([`625f128`](https://github.com/ReyemTech/mcp-canada/commit/625f12832734086b8cda737f45f893e2b1f78a7e))

- **21-01**: Extend shared/arcgis_hub.py with bare ArcGIS Server directory enumeration
  ([`978aae1`](https://github.com/ReyemTech/mcp-canada/commit/978aae19b076a774082c9c224b75e8f90aa748d3))

- **21-01**: Tracer — nb_get_crown_land end-to-end through GeoNB ArcGIS Server
  ([`95fd2ba`](https://github.com/ReyemTech/mcp-canada/commit/95fd2bac90c20d54217fc573aeed9ccd39c8f85f))

- **21-02**: Add five nb_ federal CKAN discovery tools (Task 2)
  ([`ee218b5`](https://github.com/ReyemTech/mcp-canada/commit/ee218b5eef42fbdc5ce530c939c84a697673988a))

- **21-02**: Add gnb.socrata.com discovery surface (Task 3, checkpoint option-a)
  ([`d14de80`](https://github.com/ReyemTech/mcp-canada/commit/d14de80bb9a1b326d7ec11c462a5a5bec0d45d75))

- **21-02**: Implement federal CKAN discovery client functions (Task 1)
  ([`7da90e2`](https://github.com/ReyemTech/mcp-canada/commit/7da90e2fd3462e952457a8856051b3cf2a568306))

- **21-03**: Add 6 bilingual nb_ prompts — 3 guided workflows + 3 quick lookups
  ([`9baae12`](https://github.com/ReyemTech/mcp-canada/commit/9baae12fa03f295594a4c5bba2a99724b5d81762))

- **21-03**: Add 7 zero-parameter nb_ resources — GeoNB catalogue, static data, guides
  ([`3b70258`](https://github.com/ReyemTech/mcp-canada/commit/3b702580371b21dd6c198fcdf1f8795ed2cc884e))

- **21-04**: Flood — hazard index and historical flood limits
  ([`fa8ad43`](https://github.com/ReyemTech/mcp-canada/commit/fa8ad43c662682e4f918c15cd35c8059e52b7306))

- **21-04**: GeoNB discovery trio — stands in for the 401-ing Hub Search API
  ([`5c7e718`](https://github.com/ReyemTech/mcp-canada/commit/5c7e718042adbae3e24480e88cbe7f74a0f55e75))

- **21-04**: Water — wetlands (filter-required) and contaminated sites
  ([`9adaaf8`](https://github.com/ReyemTech/mcp-canada/commit/9adaaf895a62737b8bee33f986a6c42c86ae4c10))

- **21-05**: Parcels and civic addresses — NB's geocoding pair, both filter-required
  ([`910727b`](https://github.com/ReyemTech/mcp-canada/commit/910727b223d46f1fb1d458f6a5e167001a683c8c))

- **21-06**: Health facilities and public schools — layer-dispatch tools
  ([`29de32e`](https://github.com/ReyemTech/mcp-canada/commit/29de32eca75f291ad747e9e218c8cf6bb5a2e19b))

- **21-06**: NB 511 — three key-gated transport tools + manifest integrity test
  ([`dbd3b23`](https://github.com/ReyemTech/mcp-canada/commit/dbd3b23aaed86fa62128b554d136e69a111e7696))

### Testing

- **21**: Assert live field presence for F4/F5 out_fields widenings
  ([`5edda91`](https://github.com/ReyemTech/mcp-canada/commit/5edda919e90051023fcd887a507e2b2ff1c3ddec))

- **21-01**: Add failing tests for GeoNB ArcGIS Server directory enumeration
  ([`a206b9d`](https://github.com/ReyemTech/mcp-canada/commit/a206b9d1857d34260939da193534822304c44ae1))

- **21-07**: Live MCP-layer integration coverage for all 22 New Brunswick tools
  ([`79729f1`](https://github.com/ReyemTech/mcp-canada/commit/79729f17f8bdac3f53212bd31e0fd334dcd74f35))


## v0.10.4 (2026-07-27)

### Bug Fixes

- **errors**: Invert the ValueError default — caller error is now opt-in
  ([`9a4952a`](https://github.com/ReyemTech/mcp-canada/commit/9a4952a591c038739b098fef1130e8eb030cd81c))

- **york_region**: Honour the classified markers in _call_client
  ([`777fa44`](https://github.com/ReyemTech/mcp-canada/commit/777fa44026d945d851346d5afe6ef6b006072a73))

### Chores

- Sync uv.lock after release
  ([`d73c49a`](https://github.com/ReyemTech/mcp-canada/commit/d73c49a1d327a7d72833b011b9c4c6c836f26d34))

### Documentation

- **20.4**: Record live validation and the Codex york_region finding
  ([`0ac161f`](https://github.com/ReyemTech/mcp-canada/commit/0ac161ffff71f59724ba61467f25b39999bd3c4a))

- **20.4**: Roadmap, ERR-06/07, verification report, and the corrected rule
  ([`5131cb5`](https://github.com/ReyemTech/mcp-canada/commit/5131cb5597a49870cb5756122db4af27fe34ef84))


## v0.10.3 (2026-07-27)

### Bug Fixes

- **errors**: Route every shared portal client through the decode guard
  ([`74c5095`](https://github.com/ReyemTech/mcp-canada/commit/74c50951d9329c727c68214ecad2b1c109fd7256))

- **errors**: Treat undecodable bytes as upstream failure, not caller error
  ([`30352d4`](https://github.com/ReyemTech/mcp-canada/commit/30352d4cdf81837172c4e636c61db28b1bcb766e))

### Chores

- Sync uv.lock after release
  ([`199c78e`](https://github.com/ReyemTech/mcp-canada/commit/199c78e1474f1f1d1707ce1db6478d15428e281e))

### Documentation

- **20.3**: Roadmap entry, ERR-05, and the corrected decode rule
  ([`09b101a`](https://github.com/ReyemTech/mcp-canada/commit/09b101a5f749e6ef62da62dd08c6778a5c1e3aec))

- **20.3**: Verification report; retire the stale Drug/Nutrient caveat
  ([`bd8e9aa`](https://github.com/ReyemTech/mcp-canada/commit/bd8e9aae490fa39d5277be27e395983494762f9a))

- **state**: Close Phase 20.2 — merged to main
  ([`ad7c962`](https://github.com/ReyemTech/mcp-canada/commit/ad7c962d8fadc8d7018b62cc01099d6d65c617e8))


## v0.10.2 (2026-07-26)

### Bug Fixes

- **errors**: Give every tool catch-all coverage; stop mislabelling bad JSON
  ([`d4167a6`](https://github.com/ReyemTech/mcp-canada/commit/d4167a6ecf4da4d4db17c759ba39f3022adeb229))

- **errors**: Make upstream_guard a real catch-all; classify schema drift
  ([`7d834c8`](https://github.com/ReyemTech/mcp-canada/commit/7d834c82753da01353667f0376a4ad5192b7c0b7))

### Chores

- Sync uv.lock after release
  ([`fcd80ac`](https://github.com/ReyemTech/mcp-canada/commit/fcd80acfe68d4b74bb9c43665d008e72e88d182e))

### Continuous Integration

- Test on Python 3.14; correct the version classifiers
  ([`9e2c843`](https://github.com/ReyemTech/mcp-canada/commit/9e2c843bbb41dc555923ccd02e4f130cf0e48521))

### Documentation

- **20.2**: Add ERR-01..ERR-04 requirements and traceability
  ([`54cac7c`](https://github.com/ReyemTech/mcp-canada/commit/54cac7cc0045377f4a33e5c0dee14581724d0d7e))

- **20.2**: Record live validation and close the state item
  ([`3521196`](https://github.com/ReyemTech/mcp-canada/commit/35211960ce9392311c7740168e855870320bd284))

- **20.2**: Record the catch-all rule and the JSONDecodeError trap
  ([`2ac1952`](https://github.com/ReyemTech/mcp-canada/commit/2ac19525a39ba50ea5f48e98209f6eb9e9d5f9d5))

- **20.2**: Verification report
  ([`e7c0c83`](https://github.com/ReyemTech/mcp-canada/commit/e7c0c83dd55f8d934af748f169087a0f41f3f95d))


## v0.10.1 (2026-07-26)

### Bug Fixes

- **arcgis**: Coerce where=None to "1=1" instead of dropping the parameter
  ([`0c27994`](https://github.com/ReyemTech/mcp-canada/commit/0c27994c92fa540432712b72629a8ddaf970e8c6))

- **ci**: Regenerate stale tool catalog; drop redundant fixture import
  ([`75994ac`](https://github.com/ReyemTech/mcp-canada/commit/75994ac8767486c47db68cb71c656fd91b32b5db))

- **envelope**: Classify malformed upstream JSON as UPSTREAM_ERROR
  ([`50b314b`](https://github.com/ReyemTech/mcp-canada/commit/50b314bf5e87724b11099a50c3ad80736df74c10))

- **hub,york-region**: Omit empty q; case-insensitive LIKE filters; de-mask YR+AB
  ([`f0af03e`](https://github.com/ReyemTech/mcp-canada/commit/f0af03e42db536f5648c5ed09ab67d246582abee))

- **statcan**: Correct FREQUENCY_CODES and SCALAR_FACTOR_CODES against published set
  ([`30f1123`](https://github.com/ReyemTech/mcp-canada/commit/30f112343d268570dc4a285f06ff7556283de257))

- **statcan**: Decode UOM label on series info; close 3 resolved debug sessions
  ([`3d59926`](https://github.com/ReyemTech/mcp-canada/commit/3d599269698ac2a43b6317cbe126c062faaeb248))

- **statcan**: Handle empty coordinates and malformed empty SDMX bodies
  ([`22ee328`](https://github.com/ReyemTech/mcp-canada/commit/22ee328eac27e683c30ee9193461b20556d913b0))

- **toronto,datastore**: Resolve GTFS url from CKAN; store nested values as JSON
  ([`9606c3e`](https://github.com/ReyemTech/mcp-canada/commit/9606c3e7c759f5ede9de9bdb06ab862c46714b0e))

- **types**: Clear the remaining pyright errors in source code
  ([`34fa7d5`](https://github.com/ReyemTech/mcp-canada/commit/34fa7d573b0777472fff566fb2efa9f8a2cac649))

- **weather**: Correct ahccd-trends field names; de-mask weather/climate tests
  ([`5c9028b`](https://github.com/ReyemTech/mcp-canada/commit/5c9028b02d30c876ed2343204c26d971b6935a89))

- **weather**: Resolve city names server-side; de-mask weather/current tests
  ([`9cb317d`](https://github.com/ReyemTech/mcp-canada/commit/9cb317d8dd0e8692b8821361fa7becc6ebb9477b))

### Chores

- Sync uv.lock after release
  ([`f2deb22`](https://github.com/ReyemTech/mcp-canada/commit/f2deb2285ebeb4868a278d1d9189add038afa27d))

- **ci**: Fix remaining lint and relax pyright on test files
  ([`fc3c856`](https://github.com/ReyemTech/mcp-canada/commit/fc3c85612c885843dd36f4fe4c344fa14d7c5c95))

### Code Style

- **20.1**: Drop extraneous f-string prefixes in the masking guard
  ([`5e49541`](https://github.com/ReyemTech/mcp-canada/commit/5e4954103ff0ce6b09fcc4403fe0884a2800985e))

- **20.1**: Fix lint introduced during the phase
  ([`278a292`](https://github.com/ReyemTech/mcp-canada/commit/278a2924588fdfff32655508c6b5d27b334e3514))

### Documentation

- Record the ArcGIS where=None masking pitfall
  ([`6e64559`](https://github.com/ReyemTech/mcp-canada/commit/6e645595314113c1251351c6f8ba820700398151))

- **20.1**: Capture phase context
  ([`be4a90e`](https://github.com/ReyemTech/mcp-canada/commit/be4a90e13151ef4d99b405951adf87d5e37ea663))

- **20.1**: Rename phase, backfill TEST-* requirements, record the pitfalls
  ([`deaa69f`](https://github.com/ReyemTech/mcp-canada/commit/deaa69f2a623e9da4034c58a6195cbc8c7ac82fc))

- **20.1**: Verification report and state rollforward — phase complete
  ([`b88dcd1`](https://github.com/ReyemTech/mcp-canada/commit/b88dcd14b68b8c00bb2d4313cfd4335b80604b18))

- **planning**: Backfill BC and Quebec requirements; refresh ER wait-times todo
  ([`50d5150`](https://github.com/ReyemTech/mcp-canada/commit/50d5150c44aa47e54b6d3bc062108b2bbf5e6ad1))

- **planning**: Reconcile state with what is actually on disk
  ([`5000dd9`](https://github.com/ReyemTech/mcp-canada/commit/5000dd9c0bdaeb35c61792861961a998c241a6f5))

- **roadmap**: Insert Phase 20.2 — normalize tool error handling
  ([`ac1223a`](https://github.com/ReyemTech/mcp-canada/commit/ac1223aba39bb4a50036170a45576e3382322bab))

- **state**: Close Phase 20.1 — merged to main
  ([`9fa02dd`](https://github.com/ReyemTech/mcp-canada/commit/9fa02dd8db8ee1639af71ff1d92f945c31f4a7db))

- **state**: Record phase 20.1 context session
  ([`faac35f`](https://github.com/ReyemTech/mcp-canada/commit/faac35f3659fc81ea951aac307b6a1af6d88e8e4))

- **state**: Roll state forward and record the Alberta wildfire outage
  ([`ccbaa6e`](https://github.com/ReyemTech/mcp-canada/commit/ccbaa6e23b38a309d47c91a6a257cac7e4de4dc3))

### Testing

- **20.1**: Add the masking guard; audit PRESERVE list; structured upstream errors
  ([`2bac1c3`](https://github.com/ReyemTech/mcp-canada/commit/2bac1c386be5bc83b17f5a378d0237665fa66601))

- **20.1**: Align BOC integration tests and docs with the intentional shape change
  ([`e48964c`](https://github.com/ReyemTech/mcp-canada/commit/e48964c495e3b5e82f7b8c540a50bfceace12d62))

- **20.1**: De-mask BC scenarios; pin WFS-routing tests to stable datasets
  ([`4198c5c`](https://github.com/ReyemTech/mcp-canada/commit/4198c5c4f9e4be8c59ea2fd4bfaf654f9578882b))

- **20.1**: De-mask remaining weather files, live_apis; fix invented AQHI ids
  ([`134eec2`](https://github.com/ReyemTech/mcp-canada/commit/134eec2217ca4be368ef4b89263ba86f976ce6c8))


## v0.10.0 (2026-06-17)

### Bug Fixes

- **20**: Revise 20-08 gap plan per checker feedback
  ([`864b3c9`](https://github.com/ReyemTech/mcp-canada/commit/864b3c982f13f7cb370a5156a988db6df04d4936))

- **20-08**: Remove UPSTREAM_ERROR escape-hatch from NS health integration scenarios
  ([`19d6c3b`](https://github.com/ReyemTech/mcp-canada/commit/19d6c3bbe4a093862daaefa6825082ba4c843c79))

### Chores

- Sync uv.lock after release
  ([`ff76bbe`](https://github.com/ReyemTech/mcp-canada/commit/ff76bbe19377e0d95751d59a7d6b26c6068c0584))

### Code Style

- **20**: Clean ruff warnings in nova_scotia module (unused imports/locals/f-strings)
  ([`1adbd9d`](https://github.com/ReyemTech/mcp-canada/commit/1adbd9d42f4f608f197bb04da151f46682df59e9))

### Documentation

- **20**: Align plan 07 to wave 6 (contiguous waves)
  ([`01e5431`](https://github.com/ReyemTech/mcp-canada/commit/01e5431cd1752b5df6c53bf52a4455d6a7bf14e9))

- **20**: Capture phase context
  ([`8347833`](https://github.com/ReyemTech/mcp-canada/commit/8347833b4d5ee4de0f6c8d50118e5a19a34fac99))

- **20**: Create Nova Scotia phase plan (7 plans, NS-01…NS-18)
  ([`c69ea10`](https://github.com/ReyemTech/mcp-canada/commit/c69ea108084b7bb6f776b3b87bf56a015d5ab0b0))

- **20**: Gap-closure plan 20-08 — fix ns_get_health_facilities live 400 (NS-13)
  ([`dfafc15`](https://github.com/ReyemTech/mcp-canada/commit/dfafc15546ce9c51d3a76590f12ce599b31fb35f))

- **20**: Research confirms Socrata SHIP + add validation strategy
  ([`df314e7`](https://github.com/ReyemTech/mcp-canada/commit/df314e73f2a3ac3f1fa6cf0dd576831194f3c77d))

- **20**: Research Phase 20 Nova Scotia — Socrata SODA API live-verified, 17 tools planned
  ([`8c2c4bc`](https://github.com/ReyemTech/mcp-canada/commit/8c2c4bc578f507ed8229a89fd7a0d448fc3419b9))

- **20-01**: Complete nova-scotia wave 0 — shared/socrata.py + module scaffold
  ([`ba67760`](https://github.com/ReyemTech/mcp-canada/commit/ba67760a47029abc7f3afda1d9ed05458e9b585a))

- **20-01**: Wave 0 spike — resolve 3 uncertain NS dataset shapes
  ([`44dfb77`](https://github.com/ReyemTech/mcp-canada/commit/44dfb770a2199eb6d63eb133deec6385a61c0af7))

- **20-02**: Complete Nova Scotia discovery tools — 5 tools, categories workaround, 42 tests green
  ([`8e75221`](https://github.com/ReyemTech/mcp-canada/commit/8e75221c07f7677870f78d20161c7b4640161367))

- **20-03**: Complete Nova Scotia aquaculture tools plan — 4 tools, geometry-exclusion, 97 tests
  ([`936ab53`](https://github.com/ReyemTech/mcp-canada/commit/936ab53c430d857355a563891f11f11136b30d10))

- **20-04**: Complete Nova Scotia environment/water/air plan — 4 tools, empty-advisory-valid,
  geometry-exclusion, 97% coverage
  ([`9c35d9e`](https://github.com/ReyemTech/mcp-canada/commit/9c35d9ef5b6d745329551d93fe3d2ca7d8f539d2))

- **20-05**: Complete Nova Scotia health/demographics plan — 17 ns_ tools, 97% coverage
  ([`79fa897`](https://github.com/ReyemTech/mcp-canada/commit/79fa897435ee841a7a2d01d1a892bfb374aace65))

- **20-06**: Complete Nova Scotia prompts and resources plan
  ([`6dd97ef`](https://github.com/ReyemTech/mcp-canada/commit/6dd97ef9bfcfe9eb62d790ab101cf0c0144f835c))

- **20-07**: Complete Nova Scotia final wave — 32 parametrized + 24 live integration + docs sync
  ([`8eaedc3`](https://github.com/ReyemTech/mcp-canada/commit/8eaedc3601bc27b805b1623d9082185664c60cd5))

- **20-07**: Sync README/MODULES/CLAUDE/EXAMPLES — Socrata as 4th portal tech
  ([`274649e`](https://github.com/ReyemTech/mcp-canada/commit/274649eeef2ed5a09b5c0b8cc6cf1e490accb3b1))

- **20-08**: Complete NS health facilities gap closure — NS-13 restored
  ([`fd0b90b`](https://github.com/ReyemTech/mcp-canada/commit/fd0b90b18dbc665f82eb9e27e0ee0f0caf788130))

- **phase-20**: Complete phase execution
  ([`9e009b7`](https://github.com/ReyemTech/mcp-canada/commit/9e009b7c69e67185a5a2f825016845dac2f2d286))

- **phase-20**: Resolve UAT gap + debug session after 20-08 gap closure
  ([`d6b8adc`](https://github.com/ReyemTech/mcp-canada/commit/d6b8adc38a8b73348fe022030d1d7fa08605c025))

- **quick-1**: Complete escape-hatch de-masking summary
  ([`aef4c9d`](https://github.com/ReyemTech/mcp-canada/commit/aef4c9de7e2473b52aca3641d061766961d05cb7))

- **quick-1**: Record quick task 1 + 17-failure finding in STATE.md
  ([`9981081`](https://github.com/ReyemTech/mcp-canada/commit/9981081ae1f87a8442d675d505a1b13b1637ca89))

- **state**: Record phase 20 context session
  ([`863c9bf`](https://github.com/ReyemTech/mcp-canada/commit/863c9bff07b856c609702f20521e489229ddba2e))

### Features

- **20-01**: Build shared/socrata.py — 4th portal client (SODA API)
  ([`16dca1b`](https://github.com/ReyemTech/mcp-canada/commit/16dca1ba8626c39e7c29bbe6b2e6ad2adc19865f))

- **20-01**: Scaffold nova_scotia module — 7-file pattern + test scaffolds
  ([`31d0cb4`](https://github.com/ReyemTech/mcp-canada/commit/31d0cb44e20b367f4b2d913ca22d14d38802fd6a))

- **20-02**: Add 5 discovery @tool functions + tool tests
  ([`0a556fe`](https://github.com/ReyemTech/mcp-canada/commit/0a556fe6040bbee57055565890e37795e3a5fc6d))

- **20-02**: Implement 5 discovery client bodies + TestSharedApiGetContract
  ([`8fbcd1c`](https://github.com/ReyemTech/mcp-canada/commit/8fbcd1caf2180e4f2711085145fe5829b5240a5d))

- **20-03**: Add 4 curated aquaculture @tool functions + tool tests
  ([`f0fb343`](https://github.com/ReyemTech/mcp-canada/commit/f0fb343c8423bd5a2a559432bae665bcdcc1e117))

- **20-03**: Implement 4 fishing/aquaculture client bodies with geometry exclusion
  ([`a1b21e8`](https://github.com/ReyemTech/mcp-canada/commit/a1b21e865104dbf2cb4efe31c5f6f568cadfb2b5))

- **20-04**: Add 4 environment/water/air @tool functions (NS-11/12/15/16)
  ([`f296afc`](https://github.com/ReyemTech/mcp-canada/commit/f296afcb754a372e75d8a9b130458cb2e5b687b8))

- **20-04**: Implement 4 environment/water/air client bodies (NS-11/12/15/16)
  ([`102ab51`](https://github.com/ReyemTech/mcp-canada/commit/102ab51860f53460df7b2e5845ee92937308cb8c))

- **20-05**: Add 3 curated @tool functions for NS health/demographics (double-guard dispatch)
  ([`c46fec9`](https://github.com/ReyemTech/mcp-canada/commit/c46fec9fb829ec8a807d9701251463cde4cd6aa2))

- **20-05**: Implement 3 health/demographics client bodies + _normalize_zone_field tests
  ([`ebbb257`](https://github.com/ReyemTech/mcp-canada/commit/ebbb257c7604cf222e85ece68f77ab2073b2c5b3))

- **20-06**: Add 6 bilingual NS prompts (3 guided + 3 quick lookups)
  ([`85eb176`](https://github.com/ReyemTech/mcp-canada/commit/85eb1762cfec28ffc563459fc42a7c9ab6842980))

- **20-06**: Add 7 zero-parameter NS resources (4 data + 2 docs + 1 template)
  ([`708c264`](https://github.com/ReyemTech/mcp-canada/commit/708c2647a49dd158deb010588a6b6b7bc5c68e12))

- **20-08**: GREEN — per-dataset SoQL constants + branched fetch_health_facilities with
  normalization
  ([`4e85b9f`](https://github.com/ReyemTech/mcp-canada/commit/4e85b9f981edabca4f0cc37dd6b7c561af38b474))

### Testing

- **20**: Complete UAT - 9 passed, 1 issue (health facilities 400 live)
  ([`2407ce9`](https://github.com/ReyemTech/mcp-canada/commit/2407ce9e16c0c6bdda672597deef82ac64679f04))

- **20**: Diagnose health-facilities 400 — per-dataset $select bug + test escape-hatch
  ([`11d47ee`](https://github.com/ReyemTech/mcp-canada/commit/11d47ee2130e2b30298aa7f849894bb03ad7f6ce))

- **20-07**: Parametrized envelope/lang + live field-presence integration tests
  ([`42100d1`](https://github.com/ReyemTech/mcp-canada/commit/42100d1e91d62aa64541af27b5022c707e5a515f))

- **20-08**: RED — real raw Socrata schema fixtures + per-dataset SoQL assertion tests
  ([`b0757c0`](https://github.com/ReyemTech/mcp-canada/commit/b0757c0b87b7572d45cebfb3de4879ad679629bc))

- **quick-1**: De-mask idiom-A SK+NS integration tests (Task 1)
  ([`3419a29`](https://github.com/ReyemTech/mcp-canada/commit/3419a298bf5e94414d8465a6aab4057f890a7aef))

- **quick-1**: De-mask idiom-B QC+MB tests; harden AB road events (Task 2)
  ([`8e5d98f`](https://github.com/ReyemTech/mcp-canada/commit/8e5d98f8f8efb1a2d2778cfe9dca2cc2eb860b62))


## v0.9.0 (2026-06-15)

### Bug Fixes

- **19-01**: Fix shared/arcgis_hub.py pagination param offset→startindex
  ([`9ba9687`](https://github.com/ReyemTech/mcp-canada/commit/9ba96879df6cb122c7e7da49fc945736b75d18da))

### Chores

- Sync uv.lock after release
  ([`a9982b3`](https://github.com/ReyemTech/mcp-canada/commit/a9982b384fcf4bb159874e1e5296918d6bb1a6e8))

### Code Style

- **19**: Clean ruff warnings in saskatchewan module (unused imports/f-strings)
  ([`f3d667f`](https://github.com/ReyemTech/mcp-canada/commit/f3d667fba39bef19b576eaa4aa0858fc1180d362))

### Documentation

- **19**: Capture phase context
  ([`1e701ab`](https://github.com/ReyemTech/mcp-canada/commit/1e701ab18da8bbbb20677883b0436a201730f89a))

- **19**: Create Saskatchewan phase plan (7 plans, 14 tools, SK-01…SK-15)
  ([`0919b4e`](https://github.com/ReyemTech/mcp-canada/commit/0919b4e0a991b270c8ec1364fa7e02cec129ef94))

- **19**: Research finds geohub.saskatchewan.ca ArcGIS Hub — SHIP; add validation strategy
  ([`3731db6`](https://github.com/ReyemTech/mcp-canada/commit/3731db6927b717848a557dd01529d0c68d99f796))

- **19**: Research phase — Saskatchewan ArcGIS Hub confirmed SHIP, 14 tools
  ([`5945fe8`](https://github.com/ReyemTech/mcp-canada/commit/5945fe835eee1d7a86085c9b248892bbbce82c4a))

- **19-01**: Complete Saskatchewan Wave 0 — shared startindex fix + module scaffold
  ([`420281c`](https://github.com/ReyemTech/mcp-canada/commit/420281c71f0d144be2be50a1de35b34217b8d106))

- **19-01**: Record Wave 0 spike verdicts for Saskatchewan uncertain sources
  ([`74e94cd`](https://github.com/ReyemTech/mcp-canada/commit/74e94cde93235aed585a7677f40728b4237548c1))

- **19-02**: Complete Saskatchewan discovery tools plan — 5 tools, OGC params pinned, 47 tests GREEN
  ([`9490222`](https://github.com/ReyemTech/mcp-canada/commit/9490222ff92b663f9675c633f90f9796b8a96c03))

- **19-03**: Complete Saskatchewan agriculture+mining plan — SK-06/07/08/09
  ([`9e5779d`](https://github.com/ReyemTech/mcp-canada/commit/9e5779d39d0da899bb708bcd615aefb0fc19d36f))

- **19-04**: Complete Saskatchewan environment plan — SK-10/11/12 fire bans/wildfires/air quality
  ([`5ed21a4`](https://github.com/ReyemTech/mcp-canada/commit/5ed21a482578de15c2f7837ed83cbf6a42d09a0a))

- **19-05**: Complete Saskatchewan WSA water tools plan — SK-13 + SK-14
  ([`e4c6db8`](https://github.com/ReyemTech/mcp-canada/commit/e4c6db8218097b91a93371c884b538a9a2634533))

- **19-06**: Complete Saskatchewan prompts and resources plan
  ([`adec6fe`](https://github.com/ReyemTech/mcp-canada/commit/adec6fead8aaa412481913a5cf9dfcd94cbb48f6))

- **19-07**: Complete Saskatchewan phase — SUMMARY.md + STATE.md + ROADMAP.md
  ([`2cbf848`](https://github.com/ReyemTech/mcp-canada/commit/2cbf848f137c806ca47782a04e0fc62a7beba067))

- **19-07**: Sync README/MODULES/CLAUDE/EXAMPLES for Saskatchewan + coverage gate
  ([`40e3221`](https://github.com/ReyemTech/mcp-canada/commit/40e3221f091a474820434f013d84ecf17caffc49))

- **phase-19**: Complete phase execution
  ([`d65453a`](https://github.com/ReyemTech/mcp-canada/commit/d65453aafc169d81b75b4df6062a160bfae83acf))

- **state**: Record phase 19 context session
  ([`f1263e4`](https://github.com/ReyemTech/mcp-canada/commit/f1263e421f39b7812e998cbefd0d5635db1a327f))

### Features

- **19-01**: Scaffold Saskatchewan module — 7 files + test scaffolds (Wave 0)
  ([`fb74eaf`](https://github.com/ReyemTech/mcp-canada/commit/fb74eaf53748d150016b146c661cd0d0dee8ab35))

- **19-02**: Implement 5 discovery @tool functions + tool tests
  ([`29d79f9`](https://github.com/ReyemTech/mcp-canada/commit/29d79f93e14f76e9c93c4917eac00bb64a27ad38))

- **19-02**: Implement 5 discovery client bodies with OGC params + param-regression tests
  ([`f598579`](https://github.com/ReyemTech/mcp-canada/commit/f59857917f6e44b78ad3abef18470678b9ce2ec4))

- **19-03**: Add 3 curated @tool functions (SK-06, SK-07, SK-08+SK-09)
  ([`f624234`](https://github.com/ReyemTech/mcp-canada/commit/f6242343084b91403fc402b42f05e9507f9513a0))

- **19-03**: Implement fetch_crop_yields, fetch_grain_elevators, fetch_mineral_mines
  ([`50c1621`](https://github.com/ReyemTech/mcp-canada/commit/50c162199dc8c0550496e3fc79e6398aaaf2b2a5))

- **19-04**: Implement 3 environment @tool functions + tool tests (TDD)
  ([`10df7dc`](https://github.com/ReyemTech/mcp-canada/commit/10df7dc5fd6fa9e0bbaa7296c9e3b7cdd41097a9))

- **19-04**: Implement environment client bodies + client tests (TDD)
  ([`b877520`](https://github.com/ReyemTech/mcp-canada/commit/b877520d90edf0dcc03df84acb9470dc8dfb2025))

- **19-05**: Implement fetch_wsa_stations + fetch_wsa_reservoirs client bodies
  ([`b1bcf43`](https://github.com/ReyemTech/mcp-canada/commit/b1bcf4331cebb046d8b629f1aace5ea19b571755))

- **19-05**: Implement saskatchewan_get_wsa_stations + saskatchewan_get_wsa_reservoirs tools
  ([`6c969d6`](https://github.com/ReyemTech/mcp-canada/commit/6c969d6eb5edb17814271b342caffcb2924d3227))

- **19-06**: Add 6 bilingual Saskatchewan prompts (3 guided + 3 quick)
  ([`60cded0`](https://github.com/ReyemTech/mcp-canada/commit/60cded0ce73b342680a53aac67e99f37613d3916))

- **19-06**: Add 7 zero-parameter Saskatchewan resources (3 data + 2 docs + 2 template)
  ([`8a9f1f4`](https://github.com/ReyemTech/mcp-canada/commit/8a9f1f47a3cde05bfc9b0e1712facb491730611b))

### Testing

- **19**: Complete UAT - 9 passed, 0 issues (all live-verified)
  ([`b319edb`](https://github.com/ReyemTech/mcp-canada/commit/b319edbc786bda64c176e397614fac5e719c9a99))

- **19-07**: Parametrized envelope/lang + live field-presence integration tests
  ([`f1076c6`](https://github.com/ReyemTech/mcp-canada/commit/f1076c63588a671d9c9482be6f9cc8e9c93f37d0))


## v0.8.0 (2026-06-15)

### Bug Fixes

- **18-01**: Fix prompts.py fastmcp Message import path
  ([`c3cc2a5`](https://github.com/ReyemTech/mcp-canada/commit/c3cc2a516dc344c70c78427e269f007445a48381))

- **18-09**: Remap Manitoba Hub Search params to OGC conventions (limit/startindex)
  ([`9a8bef5`](https://github.com/ReyemTech/mcp-canada/commit/9a8bef531716bac5e0c8b26a179c83c1366651df))

### Chores

- Sync uv.lock after release
  ([`5aee2a7`](https://github.com/ReyemTech/mcp-canada/commit/5aee2a7f01b3e89165d6d0c214eca6ae6ab2bf1b))

- **18-01**: Wave 0 spike — resolve Manitoba open questions
  ([`584b8de`](https://github.com/ReyemTech/mcp-canada/commit/584b8dece5111c6a0a9d46489ff4cd200c57b54e))

### Code Style

- **18**: Clean ruff warnings in manitoba module (unused imports/locals)
  ([`bc3b212`](https://github.com/ReyemTech/mcp-canada/commit/bc3b2120cc40ef4f44d15f3f289fcac0b963fbee))

### Documentation

- **18**: Capture phase context
  ([`9815540`](https://github.com/ReyemTech/mcp-canada/commit/9815540da336b8288e6aad91b498637983c0e3e6))

- **18**: Create Manitoba phase plan (8 plans, MB-01..MB-18)
  ([`f1f7e6d`](https://github.com/ReyemTech/mcp-canada/commit/f1f7e6d560c63af4f0a27747243c8746b9a6beac))

- **18**: Gap-closure plan 18-09 for Hub-Search 400 fix
  ([`9450ab0`](https://github.com/ReyemTech/mcp-canada/commit/9450ab03609eeac4342989373a545d46435695f2))

- **18**: Research finds ArcGIS Hub portal, sync context
  ([`c6e37de`](https://github.com/ReyemTech/mcp-canada/commit/c6e37de3a0b69a60d1aabebb21c1a1b75fcba1e4))

- **18**: Research phase — Manitoba ArcGIS Hub discovery, 9+ curated tools verified
  ([`6c63d20`](https://github.com/ReyemTech/mcp-canada/commit/6c63d2022fd39f7bb2349a0c14c15821152e1761))

- **18-01**: Complete Manitoba Wave 0 scaffold plan
  ([`62ea617`](https://github.com/ReyemTech/mcp-canada/commit/62ea617d1edecb27b4cae32e3fefbfc07809477a))

- **18-02**: Complete Manitoba discovery tools plan — 5 Hub tools + 39 tests
  ([`4e840d8`](https://github.com/ReyemTech/mcp-canada/commit/4e840d80ca2e29875667fcbf0e6cf42c1fa74a4a))

- **18-03**: Complete Manitoba flood/hydrology plan — MB-07/MB-08/MB-09
  ([`5ace21b`](https://github.com/ReyemTech/mcp-canada/commit/5ace21b7d5f0b42b4e0f05c4b981b2d103cf4f02))

- **18-04**: Complete Manitoba agriculture/drought plan — 4 tools, 33 tests, 96.67% coverage
  ([`4fa8581`](https://github.com/ReyemTech/mcp-canada/commit/4fa85814b6f3d5098dbed4332f831a871f01becc))

- **18-05**: Complete Manitoba environment/health/parks plan — parks bilingual, fisheries 350+ WBs,
  forests, wait times, health facilities
  ([`3419285`](https://github.com/ReyemTech/mcp-canada/commit/34192858b21b94c3794afb847cd1867ab1ea6705))

- **18-06**: Complete Manitoba transport/511 plan — 3 tools, NOT_CONFIGURED fallback, 18 tests
  ([`22f3322`](https://github.com/ReyemTech/mcp-canada/commit/22f3322cdb5b8fde5f2c9db28548dd595defb25d))

- **18-07**: Complete Manitoba prompts+resources plan — 6 prompts + 7 resources, 36 tests, 97.99%
  coverage
  ([`345c0e2`](https://github.com/ReyemTech/mcp-canada/commit/345c0e2131f685778426cac4e30afc372e3a886d))

- **18-08**: Complete Manitoba closing plan — parametrized tests, integration, docs, 96.75% coverage
  ([`a8524fb`](https://github.com/ReyemTech/mcp-canada/commit/a8524fb1864fd4085ef9982cc9da3cd5fc8f878a))

- **18-08**: Sync README/MODULES/CLAUDE/EXAMPLES for Manitoba — 20 tools, 237 total
  ([`dc727ed`](https://github.com/ReyemTech/mcp-canada/commit/dc727edfcebdea58c9f46fda9b4c9a529f3085da))

- **18-09**: Complete Manitoba Hub Search gap closure — OGC param fix, 96.76% coverage
  ([`a7a5659`](https://github.com/ReyemTech/mcp-canada/commit/a7a56598f1da004452a394036d1b1169075d78fa))

- **phase-18**: Add validation strategy
  ([`67b4253`](https://github.com/ReyemTech/mcp-canada/commit/67b425371840663438b98d3d3bef566e50ffee8e))

- **phase-18**: Complete phase execution
  ([`27f4c2a`](https://github.com/ReyemTech/mcp-canada/commit/27f4c2a683f5aedaa2690adb16333f7ca5771d83))

- **phase-18**: Resolve UAT gap + debug session after 18-09 gap closure
  ([`ea5b76f`](https://github.com/ReyemTech/mcp-canada/commit/ea5b76fa9630cf17c7cf00a2b60c1401000f1d42))

- **readme**: Sync stale counts after Manitoba (237 tools, 25 examples)
  ([`60bed28`](https://github.com/ReyemTech/mcp-canada/commit/60bed286eae776c9331d6ed857c338c354a8d48c))

- **state**: Record phase 18 context session
  ([`47235fd`](https://github.com/ReyemTech/mcp-canada/commit/47235fdea1379a96fc763e0d51e8126a19a92c55))

### Features

- **18-01**: Client helpers + stubs + test scaffolds for Manitoba module
  ([`3aa32b9`](https://github.com/ReyemTech/mcp-canada/commit/3aa32b924bdc910e9947e4d0027cbe06212a5eae))

- **18-01**: Scaffold Manitoba module init, constants, schemas
  ([`c2f4c5f`](https://github.com/ReyemTech/mcp-canada/commit/c2f4c5f2a545a0452f77d78e46a608addf7f4c46))

- **18-02**: Add 5 discovery @tool functions + tool tests
  ([`93aa3c9`](https://github.com/ReyemTech/mcp-canada/commit/93aa3c92e230d012d17629b5b0cd83a85eba7baf))

- **18-02**: Implement 5 discovery client bodies + TestSharedApiGetContract
  ([`3381dbd`](https://github.com/ReyemTech/mcp-canada/commit/3381dbd5ba507c8e32f6bc4e1b4bc4a6adc97e4e))

- **18-03**: Add 3 flood/hydrology @tool functions + tool tests
  ([`24f9832`](https://github.com/ReyemTech/mcp-canada/commit/24f9832c40ce856849e474729abe83ed49203610))

- **18-03**: Implement flood/hydrology client bodies + tests
  ([`6b9d933`](https://github.com/ReyemTech/mcp-canada/commit/6b9d9330f08fb93c92ba72734b2d9a1de208cb2e))

- **18-04**: Add 4 agriculture/drought @tool functions + tool tests
  ([`6f3363e`](https://github.com/ReyemTech/mcp-canada/commit/6f3363e82205a50519cd9d221b126ac8bcd8a6e1))

- **18-04**: Implement drought/ag/livestock/crop-regions client bodies
  ([`c5bf329`](https://github.com/ReyemTech/mcp-canada/commit/c5bf329eb0ef44725418468b5d80e5ed11eff800))

- **18-05**: Add 5 environment/health @tool functions — parks, fisheries, forests, wait times,
  health facilities
  ([`f282a95`](https://github.com/ReyemTech/mcp-canada/commit/f282a95f163a827cafaed287b7e37cf6a99b17e4))

- **18-05**: Implement 5 Plan 05 client bodies — parks, fisheries, forests, wait times, health
  facilities
  ([`ec6b7cb`](https://github.com/ReyemTech/mcp-canada/commit/ec6b7cbb0140224009be4a5b413830d764fda5de))

- **18-06**: Add 3 transport @tool functions with NOT_CONFIGURED fallback + 10 tests
  ([`26eb6e9`](https://github.com/ReyemTech/mcp-canada/commit/26eb6e9b7be2c987e8416d2fa4cbcbbaa9b29223))

- **18-06**: Implement 511 client bodies (key-gated) + 8 tests
  ([`e9ac72d`](https://github.com/ReyemTech/mcp-canada/commit/e9ac72d6c16c06ae63a93f74bf026611abf4fd3f))

- **18-07**: Add 6 bilingual Manitoba prompts (3 guided + 3 quick lookups)
  ([`520ee8f`](https://github.com/ReyemTech/mcp-canada/commit/520ee8fd22aaf53e6ede90b26dd9a349bf29aebe))

- **18-07**: Add 7 zero-parameter Manitoba resources (data:// + docs:// + template://)
  ([`11a7b17`](https://github.com/ReyemTech/mcp-canada/commit/11a7b1763484a5659c7351999473ed9d8656dbae))

### Testing

- **18**: Complete UAT - 8 passed, 1 issue (discovery tools 400)
  ([`fdfbcce`](https://github.com/ReyemTech/mcp-canada/commit/fdfbcceb84008534d3d8e14f7b698b59e8f93551))

- **18**: Diagnose discovery-tools 400 — Hub Search param bug
  ([`0935126`](https://github.com/ReyemTech/mcp-canada/commit/0935126d6592f97ef8716701e4df272ea8919ee5))

- **18-08**: Parametrized envelope/lang tests + Manitoba integration scenarios
  ([`a772a26`](https://github.com/ReyemTech/mcp-canada/commit/a772a2665aada1bdcef2858ed3b3fd1f55017741))

- **18-09**: Add failing param-regression assertions for Hub Search OGC params
  ([`9e255cc`](https://github.com/ReyemTech/mcp-canada/commit/9e255cc33b123d1f74422801ba86ae640ef2f3b8))

- **18-09**: Add live integration scenarios for 3 Manitoba Hub Search discovery tools
  ([`5514bde`](https://github.com/ReyemTech/mcp-canada/commit/5514bde1ea1f344b4a172ee9dbf1e6d7bff00b77))


## v0.7.0 (2026-05-13)

### Chores

- Sync uv.lock after release
  ([`9ef16c4`](https://github.com/ReyemTech/mcp-canada/commit/9ef16c44d860e3a7c4282f95e422ac1875ac606d))

### Documentation

- Add government level column to modules table
  ([`a79a6e1`](https://github.com/ReyemTech/mcp-canada/commit/a79a6e1dae3a2f2b01ef09030d916a77d4e03123))

- Sort modules table by level then alphabetically
  ([`fa9dcc3`](https://github.com/ReyemTech/mcp-canada/commit/fa9dcc30cf58f52ff75f03632166a0dcf5806231))

- Split README catalogs into per-module docs
  ([`2390038`](https://github.com/ReyemTech/mcp-canada/commit/239003862a542f6f1eb78e32bf362a96df7bb802))

- **17**: Add validation strategy
  ([`ffc42f5`](https://github.com/ReyemTech/mcp-canada/commit/ffc42f5fba66f176abffe8301a69c3f14539537a))

- **17**: Capture phase context
  ([`aeb63ab`](https://github.com/ReyemTech/mcp-canada/commit/aeb63abfd37f8eb523c893b937e6c8863184470e))

- **17**: Verify Phase 17 Alberta — 27/27 must-haves pass, 3 doc-sync gaps
  ([`b34bd10`](https://github.com/ReyemTech/mcp-canada/commit/b34bd10a21e35a4b32701d09f6ffafe29a56abf0))

- **17-01**: Summary + state + roadmap update
  ([`20f7ee1`](https://github.com/ReyemTech/mcp-canada/commit/20f7ee16631a20b35c567dfbfcda5c90e8408573))

- **17-02**: Complete alberta discovery tools plan
  ([`e02bae7`](https://github.com/ReyemTech/mcp-canada/commit/e02bae73cfda6768ae1249ff21a8b439740d9097))

- **17-03**: Complete AER energy tools plan
  ([`39cdd44`](https://github.com/ReyemTech/mcp-canada/commit/39cdd44390b7e948bb17635d3115e63511fc5ffb))

- **17-04**: Complete alberta wildfire tools plan
  ([`bfdaedc`](https://github.com/ReyemTech/mcp-canada/commit/bfdaedc0ffca28edfd02a0ef468663fa162390ae))

- **17-05**: Complete alberta AHS health tools plan
  ([`eb0eb84`](https://github.com/ReyemTech/mcp-canada/commit/eb0eb844bb5b81749e28a3efdc84592a5024ca21))

- **17-06**: Complete Alberta 511 transport tools plan
  ([`c2bd7de`](https://github.com/ReyemTech/mcp-canada/commit/c2bd7dedcca5410ef17268b6c167cce4fc608dc5))

- **17-07**: Complete alberta env/agri/demo/parks tools plan
  ([`1b69d3b`](https://github.com/ReyemTech/mcp-canada/commit/1b69d3b7622019185531678b1afb0b8b165aa315))

- **17-08**: Complete alberta prompts and resources plan
  ([`3e907ea`](https://github.com/ReyemTech/mcp-canada/commit/3e907eaa113634008606a251f2c83d15dba3fa2f))

- **17-09**: Add Alberta to README catalog, module docs, examples, CLAUDE
  ([`d5c6392`](https://github.com/ReyemTech/mcp-canada/commit/d5c6392a5fe8acda6078f1fb3abd86413e3ad52a))

- **17-09**: Complete Alberta final wave — 48 parametrized + 11 integration + 96.84% coverage
  ([`3700ab1`](https://github.com/ReyemTech/mcp-canada/commit/3700ab1e97b153c749f0782e47387718b6db327a))

- **17-alberta-government-open-data**: Create phase plan (9 plans, 6 waves, 27 requirements, 22
  tools)
  ([`0971ead`](https://github.com/ReyemTech/mcp-canada/commit/0971ead4c7d512e978d4d992c4a7a7b22c088f7c))

- **phase-17**: Alberta open data research
  ([`c5c6b4a`](https://github.com/ReyemTech/mcp-canada/commit/c5c6b4afb6e83c6094e9f734f704b288b0f5dca8))

- **readme**: Refresh badges and add changelog/security/community sections
  ([`e71be8c`](https://github.com/ReyemTech/mcp-canada/commit/e71be8ca3c6a7448601899656e756bda0f1b36bb))

- **state**: Record phase 17 context session
  ([`2204170`](https://github.com/ReyemTech/mcp-canada/commit/2204170578a0ec3f471eabfc7639a464bc4a8f5b))

### Features

- **17-01**: Scaffold alberta module foundation (init, constants, schemas)
  ([`c23eaa2`](https://github.com/ReyemTech/mcp-canada/commit/c23eaa258becdc6789ff51639a6a082b5f2d456d))

- **17-01**: Stub 24 client/tool functions + 6 prompts + 7 resources
  ([`be672d1`](https://github.com/ReyemTech/mcp-canada/commit/be672d17cc130a4b09aad099b5e9bfe3f4685c26))

- **17-02**: Implement alberta 5 discovery @tool bodies
  ([`01212af`](https://github.com/ReyemTech/mcp-canada/commit/01212afcb068cde24712e67fcf1a514d14b66e85))

- **17-02**: Implement alberta discovery client + shared contract tests
  ([`ef984df`](https://github.com/ReyemTech/mcp-canada/commit/ef984df584602443abe1be7cf8b093e7919f920a))

- **17-03**: Implement 4 AER @tool bodies with bilingual errors
  ([`35fd01d`](https://github.com/ReyemTech/mcp-canada/commit/35fd01d9ff0fdf0d552228d77fe1f13f02e7c2e1))

- **17-03**: Implement 4 AER client functions + ST1 fixed-width parser
  ([`2cbb316`](https://github.com/ReyemTech/mcp-canada/commit/2cbb3168feb0d1d6accd9d79339cb734faed3e56))

- **17-04**: Implement 4 Alberta wildfire client functions
  ([`fe7ecdb`](https://github.com/ReyemTech/mcp-canada/commit/fe7ecdb1314460ead523ffc87a65fe223d8ab8cc))

- **17-05**: Implement 3 AHS @tool bodies for hospitals, zones, facilities
  ([`ecebef4`](https://github.com/ReyemTech/mcp-canada/commit/ecebef4aeaaccefe029bdcc6c0b9501d829f265d))

- **17-06**: Implement 3 Alberta 511 transport @tool bodies
  ([`90263a4`](https://github.com/ReyemTech/mcp-canada/commit/90263a44a1ed426fdcc91a31732c1377d88f2673))

- **17-06**: Implement 3 Alberta 511 transport client functions
  ([`1aba8c6`](https://github.com/ReyemTech/mcp-canada/commit/1aba8c68b590b752a6b1c185f554487a37d0c5b4))

- **17-07**: Implement 5 Alberta env/agri/demo/parks @tool bodies
  ([`2da0e2a`](https://github.com/ReyemTech/mcp-canada/commit/2da0e2a84f094cae59b6247379a3d9636de105d8))

- **17-07**: Implement 5 Alberta env/agri/demo/parks client functions
  ([`73feb0a`](https://github.com/ReyemTech/mcp-canada/commit/73feb0a0a263a9d7954273d997460570a17a83c7))

- **17-08**: Add 6 bilingual @prompt functions for alberta module
  ([`1a904a9`](https://github.com/ReyemTech/mcp-canada/commit/1a904a9b8f92fafd97cc760bafb1e6c95668f40d))

- **17-08**: Add 7 zero-parameter @resource functions for alberta module
  ([`a53c187`](https://github.com/ReyemTech/mcp-canada/commit/a53c18774fb271e76efe6ef6f067d6e6fa2887e4))

### Testing

- **17-01**: Scaffold test fixtures and contract tests
  ([`784699c`](https://github.com/ReyemTech/mcp-canada/commit/784699c6595ef2025e86b594db8cde8533c2ec33))

- **17-04**: Add 13 TDD tests for Alberta wildfire client functions
  ([`08acf4e`](https://github.com/ReyemTech/mcp-canada/commit/08acf4e6b1e6fc92036ae01ec991eb5d7ec69c59))

- **17-06**: Add failing tests for 3 Alberta 511 transport tools
  ([`539103d`](https://github.com/ReyemTech/mcp-canada/commit/539103d0a29c183aae08a1a18f1e01ff17b134bc))

- **17-06**: Add failing tests for 511 transport client functions
  ([`43cedbe`](https://github.com/ReyemTech/mcp-canada/commit/43cedbe7084bcc2e2006fc8e23bfdb5ba525a436))

- **17-09**: Add Alberta integration scenarios via MCP Client
  ([`40cd96a`](https://github.com/ReyemTech/mcp-canada/commit/40cd96a60a70a018bae609e900559421e5fe826c))

- **17-09**: Parametrize envelope + lang propagation tests over all 24 alberta tools
  ([`dc5a77e`](https://github.com/ReyemTech/mcp-canada/commit/dc5a77ecfc16a3ae35dbfae87e05b734aae37652))


## v0.6.0 (2026-04-12)

### Bug Fixes

- **15-05**: Bilingualize bc_get_water_wells 130K guard message
  ([`7b01153`](https://github.com/ReyemTech/mcp-canada/commit/7b011538d85b5e185f3645507a754c79a73e51a4))

- **15-05**: Rewrite BC _api_get to treat shared api_get return as parsed dict
  ([`e7a1440`](https://github.com/ReyemTech/mcp-canada/commit/e7a14407985bd63ef4b9121497e5c2b8c75e352b))

- **16-05**: Add health/medical/sante keywords to quebec_get_er_wait_times for BM25 discovery
  ([`b980a9d`](https://github.com/ReyemTech/mcp-canada/commit/b980a9da395e9fb5c3951293b1587316e4ad9d21))

- **16-05**: Expand electricity format matcher to XLSX/XLS + fix envelope source URL
  ([`833ef5b`](https://github.com/ReyemTech/mcp-canada/commit/833ef5b8c10d11766f0d68bc39eeb2876f6b602f))

- **16-05**: Extend fetch_and_parse to detect query-string format hints + remove road_conditions
  exception swallow
  ([`f2ca2b9`](https://github.com/ReyemTech/mcp-canada/commit/f2ca2b90524d84ea0eff295b0b2021fc5af7467d))

- **16-06**: Fix fetch_road_conditions snake_case mapper keys
  ([`1ad899a`](https://github.com/ReyemTech/mcp-canada/commit/1ad899ab6ded48880dfd0c86a267c0d48c486430))

- **16-06**: Scoped SECLEVEL=1 SSLContext for Hydro-Québec XLSX TLS fix
  ([`53d8217`](https://github.com/ReyemTech/mcp-canada/commit/53d82174066de3532813c4207b50c94c5892baaf))

- **16-07**: Skip Hydro-Québec XLSX formula legend row in fetch_electricity_data
  ([`d37232f`](https://github.com/ReyemTech/mcp-canada/commit/d37232fabee09cd9532fafb911616ae07a2ad87a))

- **16-07**: Stringify numeric ID fields in quebec mappers for Pydantic str schemas
  ([`37e6846`](https://github.com/ReyemTech/mcp-canada/commit/37e68463babfd2ce7694ee32f1d72590bb0fcae6))

- **16-08**: Remove nom_route substring fallback — exact num_route match only
  ([`a5a3aea`](https://github.com/ReyemTech/mcp-canada/commit/a5a3aea4bf987b053c5ffbfaa0e2d28a087bdbd1))

- **server**: Exclude underscore-prefixed module fixtures from production loading
  ([`fb78203`](https://github.com/ReyemTech/mcp-canada/commit/fb782033dc1d1fea13a335696b8978089997cf70))

### Chores

- Sync uv.lock after release
  ([`76e7174`](https://github.com/ReyemTech/mcp-canada/commit/76e7174e3ccacce0441da3de3ab228302999340b))

- **16-05**: Remove pre-existing unused variable in test_client.py (ruff F841)
  ([`f56f7be`](https://github.com/ReyemTech/mcp-canada/commit/f56f7beb857af27432be553fe753ac71430ad5b7))

### Documentation

- Capture todo - Research cross-Canada ER wait times datasets
  ([`5ae25b0`](https://github.com/ReyemTech/mcp-canada/commit/5ae25b0590789d6b1eac3c667bec21cec00b54c0))

- **14**: Add research, validation, and scope adjustment
  ([`aaecf3e`](https://github.com/ReyemTech/mcp-canada/commit/aaecf3ed9e3b457796702d1d566285c4ac2a4926))

- **14**: Capture phase context
  ([`f7cc85a`](https://github.com/ReyemTech/mcp-canada/commit/f7cc85afc3eab1c9619cf6aecc82ade94965529e))

- **14**: Create phase plan for York Region ArcGIS Hub module
  ([`97d7175`](https://github.com/ReyemTech/mcp-canada/commit/97d7175230086c7089ba3114b8d75ba0bce58b6e))

- **14**: Fix checker blockers - tool count and validation assignments
  ([`851c4d3`](https://github.com/ReyemTech/mcp-canada/commit/851c4d3d53229eca0c76d92397b772189589a662))

- **14**: Research phase ArcGIS Hub domain
  ([`50072f2`](https://github.com/ReyemTech/mcp-canada/commit/50072f231da25c9f7460c9a29f57ed4c18b4e672))

- **14-01**: Complete york_region module skeleton plan
  ([`336d511`](https://github.com/ReyemTech/mcp-canada/commit/336d511d05f88f254f367693087d944aa933a9ba))

- **14-02**: Complete york_region tools plan — 27 tools, 99.89% coverage
  ([`d03e950`](https://github.com/ReyemTech/mcp-canada/commit/d03e950aea1a8ffd3040e390248ba2d3b5b87cf6))

- **14-03**: Complete york_region prompts+resources plan — phase 14 done
  ([`2345f17`](https://github.com/ReyemTech/mcp-canada/commit/2345f17289e10e5958530a8821a3dc38b2b715de))

- **15**: Add research and validation strategy
  ([`d48e219`](https://github.com/ReyemTech/mcp-canada/commit/d48e219d0cb88cf9fb0f9caeddafb2a476fade26))

- **15**: Capture phase context
  ([`669a216`](https://github.com/ReyemTech/mcp-canada/commit/669a2165ae771fd54d37b6d13601d3a044ddd5d5))

- **15**: Plan British Columbia phase — 4 plans across 4 waves
  ([`97aad99`](https://github.com/ReyemTech/mcp-canada/commit/97aad99ec76c9c5dd875dae3532616e73af04e1f))

- **15**: Research BC CKAN + WFS — verified 15 curated datasets live
  ([`a78c1ee`](https://github.com/ReyemTech/mcp-canada/commit/a78c1eec72b3cf520c684d75a4be4638276d19ca))

- **15-01**: Complete BC infrastructure plan — shared/ogc.py + module skeleton + Wave 0 stubs
  ([`031c4a9`](https://github.com/ReyemTech/mcp-canada/commit/031c4a97072b20248ae2c6c58eb9aab35d06c9dc))

- **15-02**: Complete BC CKAN discovery tools plan
  ([`1d85bde`](https://github.com/ReyemTech/mcp-canada/commit/1d85bdeb5cc92fdf7b01638e779e4988eded4882))

- **15-03**: Complete BC WFS curated tools plan — 15 tools, 175 total
  ([`05e2a9e`](https://github.com/ReyemTech/mcp-canada/commit/05e2a9e82cfcbd0efdabbe6b58c60d05006c297b))

- **15-04**: Complete BC module — prompts+resources+integration tests plan
  ([`e050c81`](https://github.com/ReyemTech/mcp-canada/commit/e050c813776729b1bd599340f1cecfd77a735062))

- **15-05**: Add gap-closure plan for _api_get + bilingual guard
  ([`9ed8c09`](https://github.com/ReyemTech/mcp-canada/commit/9ed8c09d7401778ab67da11574e456177fdd5ed6))

- **15-05**: Complete BC gap closure plan — 0 integration failures, bilingual guard fixed
  ([`1ce51c7`](https://github.com/ReyemTech/mcp-canada/commit/1ce51c73548eff71ca2efef48f39c93fae5edb7c))

- **15-05**: Verify gap closure — 5/5 resolved, UAT green
  ([`88fb15d`](https://github.com/ReyemTech/mcp-canada/commit/88fb15db1d1e1c66c7a99158ba3acb307af7dee2))

- **16**: Add phase context for Quebec CKAN module
  ([`fff0213`](https://github.com/ReyemTech/mcp-canada/commit/fff0213e43c4e1fe7f0a7a33000025935b79d384))

- **16**: Add research and validation strategy
  ([`27a65bb`](https://github.com/ReyemTech/mcp-canada/commit/27a65bbfadf25de188bf7d123376dfa6b25b2d20))

- **16**: Create Quebec phase plan (4 plans, 4 waves, 18 tools)
  ([`eb9d826`](https://github.com/ReyemTech/mcp-canada/commit/eb9d8263328f195355a21b4dd45640378c4c02d9))

- **16**: Diagnose route filter substring match bug (Test 8, cycle 4)
  ([`a732aec`](https://github.com/ReyemTech/mcp-canada/commit/a732aec0fab7ca6e807664d41cab6d5b316a660c))

- **16**: Research Quebec CKAN — live-verified dataset availability, bilingual field shape, pitfalls
  ([`116721d`](https://github.com/ReyemTech/mcp-canada/commit/116721d6d04cf8fda86894b306883d7fcc484e44))

- **16-01**: Complete Quebec module skeleton plan — wave_0_complete, 105 test stubs
  ([`65e4b41`](https://github.com/ReyemTech/mcp-canada/commit/65e4b41a3ba0a72f7e9761e4b1d86d98bd33e3a9))

- **16-02**: Complete Quebec CKAN discovery layer — client + 5 tools, 96% coverage
  ([`ec9e4f8`](https://github.com/ReyemTech/mcp-canada/commit/ec9e4f8dfac9bf6fc913269d2d405cc272c974fe))

- **16-03**: Complete Quebec health+transport tools plan — 7 tools, 98% coverage
  ([`83012dc`](https://github.com/ReyemTech/mcp-canada/commit/83012dc527b001ba5bbb937dd8ef688355113d03))

- **16-04**: Complete Quebec environment/energy plan — Phase 16 done, 18 tools, 96.51% coverage
  ([`47b6d89`](https://github.com/ReyemTech/mcp-canada/commit/47b6d89005633a23d7d3adab7eed2818ed62497b))

- **16-04**: Update README, CLAUDE.md, and VALIDATION.md for Phase 16 completion
  ([`9c94cfb`](https://github.com/ReyemTech/mcp-canada/commit/9c94cfbaa2156a1b138463477fea82ced2e598f3))

- **16-05**: Add gap-closure plan for MTQ CSV parser + Hydro XLSX + BM25 keywords
  ([`da40056`](https://github.com/ReyemTech/mcp-canada/commit/da40056608e9787bea3d6e28e2d984f2e92c9fa2))

- **16-05**: Complete Quebec gap-closure plan summary and state updates
  ([`a4f9d77`](https://github.com/ReyemTech/mcp-canada/commit/a4f9d774440d53228a3ed5c5c62776f6aed56f51))

- **16-06**: Add gap-closure plan for bridges paging, road conditions mapper, Hydro-Quebec TLS
  ([`5cfe98b`](https://github.com/ReyemTech/mcp-canada/commit/5cfe98b4bfbf14fbbf797dc8b54bfeaf2c97ec75))

- **16-06**: Complete gap closure cycle 2 plan
  ([`4b18c69`](https://github.com/ReyemTech/mcp-canada/commit/4b18c69cce3ab74c1149f381a8fd06efcdc3f031))

- **16-07**: Complete quebec gap closure cycle 3 plan
  ([`900597b`](https://github.com/ReyemTech/mcp-canada/commit/900597bc57f786fed3198bde8a5e969a0cb7d48a))

- **16-08**: Complete bridge route substring fix plan
  ([`7e538e3`](https://github.com/ReyemTech/mcp-canada/commit/7e538e3f5b370ea0faf7ed4fedbf84d9864fe597))

- **16-08**: Create gap closure cycle 4 plan — route filter substring match fix
  ([`73eb8ae`](https://github.com/ReyemTech/mcp-canada/commit/73eb8ae3ae7ccaa2515da8ca94766c9a96d9d922))

- **phase-14**: Complete phase execution
  ([`289e1a7`](https://github.com/ReyemTech/mcp-canada/commit/289e1a79a57c86dba09e50127184535fe9369d3e))

- **phase-15**: Complete phase execution
  ([`61d8c41`](https://github.com/ReyemTech/mcp-canada/commit/61d8c41a42dc63ed1a0075f41644a22485d8c317))

- **phase-16**: Complete phase execution
  ([`55d9f91`](https://github.com/ReyemTech/mcp-canada/commit/55d9f91c160bae7b8d36cb263b827f82e5590b57))

- **phase-16**: Complete phase execution
  ([`47c174e`](https://github.com/ReyemTech/mcp-canada/commit/47c174ebe5daa81a9ff94e58444fc8f6ebc08a02))

- **phase-16**: Complete phase execution (cycle 4 — route filter fix)
  ([`0176241`](https://github.com/ReyemTech/mcp-canada/commit/0176241cf2e3185b7991d19a2008a6a7d7540ad9))

- **phase-16**: Resolve 3 post-retest UAT gaps after 16-06 gap closure cycle 2
  ([`c307908`](https://github.com/ReyemTech/mcp-canada/commit/c307908bb31fc59e6907d55fd23730fd84e9406d))

- **phase-16**: Resolve UAT gaps and debug session after 16-05 gap closure
  ([`31d37e1`](https://github.com/ReyemTech/mcp-canada/commit/31d37e17ce736f476e9c2f6af6def03e9e8c39d2))

- **state**: Record phase 14 context session
  ([`2b53d17`](https://github.com/ReyemTech/mcp-canada/commit/2b53d178bdf79ccbb10a9b43b9e1ee27bb75655b))

- **state**: Record phase 15 context session
  ([`491ce6b`](https://github.com/ReyemTech/mcp-canada/commit/491ce6be7c313c1a3f9bd3d2b05beb7fec0244a3))

### Features

- **14-01**: Add shared/arcgis_hub.py ArcGIS Hub + FeatureServer client
  ([`08dc020`](https://github.com/ReyemTech/mcp-canada/commit/08dc0206af4a4b7acb7c98b05688f3e8ac4977b6))

- **14-01**: Add york_region module skeleton with client and unit tests
  ([`39e5b20`](https://github.com/ReyemTech/mcp-canada/commit/39e5b209c8e26b9c25930b2efa6f7eff6746a52d))

- **14-02**: Add york_region tools.py — 27 @tool functions with unit tests
  ([`3d875e9`](https://github.com/ReyemTech/mcp-canada/commit/3d875e9aa7aaf7143bfbf46d3e77e5fafa20ea5b))

- **14-03**: Add integration tests, update README and REQUIREMENTS.md
  ([`875b098`](https://github.com/ReyemTech/mcp-canada/commit/875b098e6ea0ac65d10417349b0ed4f2fbeef1a9))

- **14-03**: Add york_region prompts.py + resources.py with unit tests
  ([`dc0d00a`](https://github.com/ReyemTech/mcp-canada/commit/dc0d00afddb38c7e3b8a26a35c014580636287f2))

- **15-01**: Create british_columbia module 7-file skeleton
  ([`731ac5b`](https://github.com/ReyemTech/mcp-canada/commit/731ac5b5cc75c5f4c6b7e736f1fd4ab43be1b744))

- **15-01**: Implement shared/ogc.py WFS 2.0 client with unit tests
  ([`cf2cb23`](https://github.com/ReyemTech/mcp-canada/commit/cf2cb23233b5fafa07e44bdb6ef58f4f6915ba14))

- **15-01**: Scaffold Wave 0 test stubs for british_columbia + integration classes
  ([`57c6699`](https://github.com/ReyemTech/mcp-canada/commit/57c6699291c092fd0c8ed0cc94d8d8d03124c73c))

- **15-02**: Implement 5 BC CKAN discovery tools + bc_query_features WFS routing
  ([`5c5e3df`](https://github.com/ReyemTech/mcp-canada/commit/5c5e3df786719bbc48bead63df71bc53e9847e19))

- **15-02**: Implement CKAN client functions + queryable_via_wfs derivation
  ([`39de48e`](https://github.com/ReyemTech/mcp-canada/commit/39de48e649b15374b8876757a2d4ad04d2631cb3))

- **15-03**: Implement 10 curated environment/health/transport/climate tools
  ([`75d4df9`](https://github.com/ReyemTech/mcp-canada/commit/75d4df93211b9d4e7c7b4004cb228069322fe755))

- **15-03**: Implement _wfs_fetch + 5 curated wildfire/forestry tools
  ([`6de1b66`](https://github.com/ReyemTech/mcp-canada/commit/6de1b66bb54d5692cd232f5226f540efe265259e))

- **15-04**: Implement bc_ prompts (6) + resources (7) + unit tests
  ([`f48eec2`](https://github.com/ReyemTech/mcp-canada/commit/f48eec2e06a41292d8e1a17b1a342a51c618166b))

- **15-04**: Populate integration tests + update README.md + CLAUDE.md
  ([`bca1002`](https://github.com/ReyemTech/mcp-canada/commit/bca1002d7bf0b9c1be0114b7ef58896e017c10b4))

- **16-01**: Quebec module skeleton — 7-file pattern with constants, schemas, client stubs
  ([`ffb03a0`](https://github.com/ReyemTech/mcp-canada/commit/ffb03a06d35e161e78925018c04d07a6d70bc494))

- **16-02**: Implement 5 Quebec CKAN discovery tools
  ([`9509770`](https://github.com/ReyemTech/mcp-canada/commit/9509770658bb16a9997e672e43ed7e789b5e62bc))

- **16-02**: Implement Quebec CKAN client with Phase 15 parsed-dict _api_get
  ([`310b2aa`](https://github.com/ReyemTech/mcp-canada/commit/310b2aa7fad03c7a87d70b342c2792f9e44d5c49))

- **16-03**: Add 7 curated Quebec tools (health + MTQ transport)
  ([`7b5ca00`](https://github.com/ReyemTech/mcp-canada/commit/7b5ca00671a710b29955d23d05574f4cec15d60d))

- **16-03**: Implement 7 Health/MTQ client functions
  ([`3c0c1ea`](https://github.com/ReyemTech/mcp-canada/commit/3c0c1eae5c09fba327e1910836824342e3c4109d))

- **16-04**: Implement 6 bilingual prompts + 7 zero-parameter resources
  ([`121be2e`](https://github.com/ReyemTech/mcp-canada/commit/121be2eb2f7f38d0b2bc283dd67e315c0e120b52))

- **16-04**: Implement 6 environment/energy client + tool functions
  ([`6d61252`](https://github.com/ReyemTech/mcp-canada/commit/6d61252f1058eb7dcd250e705015a707a8eabd1e))

- **16-04**: Wire Quebec integration tests through MCP Client layer
  ([`e5e88ce`](https://github.com/ReyemTech/mcp-canada/commit/e5e88cedbf038e699a6a37a97c876069de10b9b1))

- **16-06**: WFS paging loop and route normalizer for bridge structures
  ([`3fdd9d7`](https://github.com/ReyemTech/mcp-canada/commit/3fdd9d7473eb78ece2f80137457b543eff702e16))

### Testing

- **14**: Complete UAT - 9/9 passed
  ([`afb6b3d`](https://github.com/ReyemTech/mcp-canada/commit/afb6b3dd84bced60872742ec8845a4f23eccb5f7))

- **15**: Complete UAT - 9 passed, 5 issues
  ([`f2775e8`](https://github.com/ReyemTech/mcp-canada/commit/f2775e8f93f697c6a9f230441ee634d2123f8492))

- **15**: Diagnose UAT gaps — _api_get contract + bilingual error
  ([`9e57a9e`](https://github.com/ReyemTech/mcp-canada/commit/9e57a9e1cc53b2ea34adc8aa8a3be936269e8f09))

- **16**: Complete UAT - 12 passed, 4 issues
  ([`c29bb67`](https://github.com/ReyemTech/mcp-canada/commit/c29bb6794ccb003be25c32f2572efb1358a6227d))

- **16**: Retest 2 post-16-06 - 2 fixed (9, 11), 1 new schema issue + 1 minor
  ([`2cf0eb6`](https://github.com/ReyemTech/mcp-canada/commit/2cf0eb64278af8dc4b8d54a57d6b80ea7ef4fea4))

- **16**: Retest 3 post-16-07 — Test 11 FIXED (legend row skip), Test 8 new route filter substring
  match bug
  ([`ea83209`](https://github.com/ReyemTech/mcp-canada/commit/ea83209311086ab9283726494a27a365357f187e))

- **16**: Retest 4 post-16-08 — Test 8 PASSED, all 16 UAT tests green, phase DONE
  ([`cdc03da`](https://github.com/ReyemTech/mcp-canada/commit/cdc03dacb8e05a4d03cc7d57b64d8043e96a5446))

- **16**: Retest post-16-05 - 1 fixed (BM25), 3 new downstream issues
  ([`2fe59b6`](https://github.com/ReyemTech/mcp-canada/commit/2fe59b614fc4b07a55afad8320cc4836a18eb9d7))

- **16-01**: Wave 0 test scaffolds for Quebec module
  ([`d858b02`](https://github.com/ReyemTech/mcp-canada/commit/d858b0262cf54914306cb5e6822dbc786616a539))

- **16-08**: Add failing test for route filter substring match bug
  ([`3f32f49`](https://github.com/ReyemTech/mcp-canada/commit/3f32f49206d83b11a0cc3f08cebc25e2d88ce28f))

- **16-08**: Tighten integration test to reject Route 204 in A-20 results
  ([`def28fb`](https://github.com/ReyemTech/mcp-canada/commit/def28fb565d9ecb06af0f3d9c2d2ecb2da231201))


## v0.5.0 (2026-04-09)

### Bug Fixes

- Separate citizenship into own dataset with correct parse config
  ([`499fa0a`](https://github.com/ReyemTech/mcp-canada/commit/499fa0ab3eb683403e0713f0821538249de8ec5d))

- **12**: Fix population projections — skip_rows=4 and row-based filtering
  ([`88d435b`](https://github.com/ReyemTech/mcp-canada/commit/88d435b17f77b222f501b218b47f15bd071f3465))

- **12**: Nest population age data into age_groups and single_age dicts
  ([`b369513`](https://github.com/ReyemTech/mcp-canada/commit/b369513327aaed681c23e91b18e60efb1257cb99))

- **12**: Use substring matching for scenario and gender filters
  ([`8e565d9`](https://github.com/ReyemTech/mcp-canada/commit/8e565d96d9d15e4ba2bead2598d3adb72cf11898))

- **13-02**: Remove unused BASE_URL import and fix fetch_organizations call
  ([`520ec3d`](https://github.com/ReyemTech/mcp-canada/commit/520ec3df24ee3d002b3a3dacd37d9e223786f6ec))

### Chores

- Sync uv.lock after release
  ([`056efe0`](https://github.com/ReyemTech/mcp-canada/commit/056efe05394dade0981f5b69444c518ac8b4ea61))

### Documentation

- Add coverage badge to README
  ([`0a5c6fa`](https://github.com/ReyemTech/mcp-canada/commit/0a5c6fa116eb67aaf7a5de40819d01a24370241c))

- Add Phase 12 — Ontario Government Open Data
  ([`a977a2c`](https://github.com/ReyemTech/mcp-canada/commit/a977a2cd8269a5710efa44c9a287be60f1c74df9))

- Add Phase 13 — Toronto Municipal Government Open Data
  ([`564f959`](https://github.com/ReyemTech/mcp-canada/commit/564f959ade3c60f9aafe536e7c9ddf6169bb7ecc))

- Add Phase 14 — York Region Municipal Government Open Data
  ([`ba7b168`](https://github.com/ReyemTech/mcp-canada/commit/ba7b168f32ea9b843057c03ed3b37654f13c3b23))

- Add Phase 15 — British Columbia Government Open Data
  ([`caf1f22`](https://github.com/ReyemTech/mcp-canada/commit/caf1f221190152b74806decaaeecade2037e1f64))

- Add Phase 16 — Quebec Government Open Data
  ([`69d43b7`](https://github.com/ReyemTech/mcp-canada/commit/69d43b79732bb76751365205d66718672cde11e8))

- Add Phase 17 — Alberta Government Open Data
  ([`56ee244`](https://github.com/ReyemTech/mcp-canada/commit/56ee244a2b9386422ee5a1fc26f5b2b773498310))

- Add Phases 18-39 — all provinces, territories, municipalities, regions
  ([`47e5a60`](https://github.com/ReyemTech/mcp-canada/commit/47e5a60e28ad951cc20c239c74369b9f4f7fed69))

- Add public ROADMAP.md with provincial, municipal, and regional phases
  ([`c94bb66`](https://github.com/ReyemTech/mcp-canada/commit/c94bb6629ead50520c1a0172eb2134d5480f382a))

- **12**: Add research and validation strategy
  ([`4d346d8`](https://github.com/ReyemTech/mcp-canada/commit/4d346d84363c64f7ad827b3d74d9ffe4f9ea89cf))

- **12**: Add shared/reshape usage for population projections tool
  ([`752b152`](https://github.com/ReyemTech/mcp-canada/commit/752b1520ac865a9a55e7a36aa76e134c099b6d74))

- **12**: Create Ontario open data phase plan
  ([`f60cb2a`](https://github.com/ReyemTech/mcp-canada/commit/f60cb2a1bab52b722b8381f2f7dfed74aea857fb))

- **12**: Research Ontario Government Open Data phase
  ([`a5b7436`](https://github.com/ReyemTech/mcp-canada/commit/a5b743611570e7d9066ae80865976b7057e5dbb7))

- **12-01**: Complete Ontario module skeleton plan
  ([`001fce1`](https://github.com/ReyemTech/mcp-canada/commit/001fce12b68ee84a377a629540ec1c2bda1325ed))

- **12-02**: Complete Ontario tools plan — SUMMARY, STATE, ROADMAP
  ([`40ab85d`](https://github.com/ReyemTech/mcp-canada/commit/40ab85d6288ad92e0fc5485ec19b2d81b21acc83))

- **13**: Add research and validation strategy
  ([`6976bbd`](https://github.com/ReyemTech/mcp-canada/commit/6976bbdbe74eca63f2d32b77a5b8bb406cf1f0af))

- **13**: Capture phase context
  ([`e313c19`](https://github.com/ReyemTech/mcp-canada/commit/e313c19546e8bd7dacbdafe3d370206a40130297))

- **13**: Create phase plan for Toronto municipal open data
  ([`f39e84f`](https://github.com/ReyemTech/mcp-canada/commit/f39e84f90f1868ccdb74fd620d881648be404a69))

- **13**: Fix requirements coverage and validation plan references
  ([`0b255e7`](https://github.com/ReyemTech/mcp-canada/commit/0b255e70053b0fb64f7d77023095411859ca3526))

- **13**: Research Toronto CKAN API, GTFS, neighbourhood profiles, RentSafeTO
  ([`b47795a`](https://github.com/ReyemTech/mcp-canada/commit/b47795a6b23a1a693aded70db74d76767398d9b3))

- **13-01**: Complete Toronto module skeleton plan
  ([`18881c6`](https://github.com/ReyemTech/mcp-canada/commit/18881c60ced2ed2ef0be7e3208be9e1c07025f07))

- **13-02**: Complete Toronto tools plan — 12 tools, 52 unit tests, 8 integration tests, README
  updated
  ([`e816aa6`](https://github.com/ReyemTech/mcp-canada/commit/e816aa669f8d4034fed358927fcaa29fc59778ed))

- **40**: Add research and validation strategy
  ([`7bf48b2`](https://github.com/ReyemTech/mcp-canada/commit/7bf48b2ad205aa1fb258614d93e88641f69f72ef))

- **40**: Capture phase context
  ([`aff248d`](https://github.com/ReyemTech/mcp-canada/commit/aff248d2332326c5781d928c8bb60fda3d4d3881))

- **40**: Create phase plan for MCP prompts and resources
  ([`2b5314c`](https://github.com/ReyemTech/mcp-canada/commit/2b5314cd27dc50e2213581bf7020c9fcce4d25ba))

- **40**: Research phase MCP prompts and resources
  ([`f7a8cca`](https://github.com/ReyemTech/mcp-canada/commit/f7a8cca519fc3a0b763e3b3e2724e1e2fbb4fd6e))

- **40-01**: Complete BoC prompts/resources plan — SUMMARY, STATE, ROADMAP updated
  ([`36e38e8`](https://github.com/ReyemTech/mcp-canada/commit/36e38e85e8ed13c5acf3cf3c0fc67cc7b44a34fe))

- **40-02**: Complete StatCan/Datastore/CKAN prompts and resources plan
  ([`536e4cf`](https://github.com/ReyemTech/mcp-canada/commit/536e4cf7190e4d65c3d5b4b297673628a18cf76a))

- **40-03**: Complete Open Parliament + Recalls + Drug DB + Nutrient File prompts/resources plan
  ([`8584fb8`](https://github.com/ReyemTech/mcp-canada/commit/8584fb8a1ef352419220acd06c914313017b8791))

- **40-04**: Complete Weather, IRCC, Ontario, Toronto prompts and resources plan
  ([`b5cf4af`](https://github.com/ReyemTech/mcp-canada/commit/b5cf4af5aaffe24b0cea32aae269dbe2652e3d8e))

- **40-05**: Complete integration tests + documentation plan — phase 40 complete
  ([`59fc115`](https://github.com/ReyemTech/mcp-canada/commit/59fc115077bc58666d4b6321045c2d50570df48e))

- **40-05**: Update README and CLAUDE.md with 7-file pattern and prompt/resource catalogs
  ([`0dce5e8`](https://github.com/ReyemTech/mcp-canada/commit/0dce5e8d1f0dfc12abb0f9e71a58e3a23268c262))

- **phase-12**: Complete phase execution
  ([`43682a7`](https://github.com/ReyemTech/mcp-canada/commit/43682a7fdbdb1ddb8aba1c6079cd1fe0655c989f))

- **phase-13**: Complete phase execution
  ([`de2046b`](https://github.com/ReyemTech/mcp-canada/commit/de2046b164c271575d11fbf504abed08aa82e229))

- **phase-40**: Complete phase execution
  ([`663499a`](https://github.com/ReyemTech/mcp-canada/commit/663499ac611f98db978786dd7df74d9d8f7aaf5a))

- **state**: Record phase 13 context session
  ([`190125e`](https://github.com/ReyemTech/mcp-canada/commit/190125e76cbefabe0fa7045c9516c8b94d4f7ad9))

- **state**: Record phase 40 context session
  ([`84a3ced`](https://github.com/ReyemTech/mcp-canada/commit/84a3cedaae8b26c44fdd797c29b2c716c9844c63))

### Features

- **12-01**: Create Ontario open data module skeleton and CKAN client layer
  ([`8dcb563`](https://github.com/ReyemTech/mcp-canada/commit/8dcb5631a53f3645c435300796c7e029bc0ec313))

- **12-02**: Add Ontario integration tests and update README
  ([`595f33b`](https://github.com/ReyemTech/mcp-canada/commit/595f33b0d01be827dcaea8f6b7674af1b984e2e2))

- **12-02**: Implement Ontario tool functions with unit tests
  ([`7952a29`](https://github.com/ReyemTech/mcp-canada/commit/7952a29f8a9948dfb861f9d90d68dccb53f30948))

- **13-01**: Add GeoJSON and JSON parsers to shared/parsers.py
  ([`6c04f0a`](https://github.com/ReyemTech/mcp-canada/commit/6c04f0a9f6d8b53e73b7f3ac43631f15f3964774))

- **13-01**: Create Toronto module skeleton with full client layer and unit tests
  ([`5be54b5`](https://github.com/ReyemTech/mcp-canada/commit/5be54b59f598b5485bd3dc5fbd36e4cec5e943c9))

- **13-02**: Add Toronto integration tests and update README
  ([`a94fbe7`](https://github.com/ReyemTech/mcp-canada/commit/a94fbe7a37ae461610142148c997c9af5ff8a4df))

- **13-02**: Implement 12 toronto_ tool functions with BM25 docstrings and unit tests
  ([`f040273`](https://github.com/ReyemTech/mcp-canada/commit/f040273767f48d922e1368a598d276636bf83916))

- **40-01**: Add annotated prompt/resource templates to _example module
  ([`81e7021`](https://github.com/ReyemTech/mcp-canada/commit/81e70219ec7f5fe338d36e8a2d4b090415e1b02b))

- **40-01**: Add BoC prompts.py and resources.py reference implementation
  ([`4792085`](https://github.com/ReyemTech/mcp-canada/commit/479208596d241261ceeecf741ab8306e8945756c))

- **40-02**: Add Datastore and CKAN prompts.py, resources.py, and unit tests
  ([`23d8c12`](https://github.com/ReyemTech/mcp-canada/commit/23d8c122b83daad6569004a3f9edf441fb683bb7))

- **40-02**: Add StatCan prompts.py, resources.py, and unit tests
  ([`fc7f6b3`](https://github.com/ReyemTech/mcp-canada/commit/fc7f6b3b30964b061dc7adc499c74d1f6b501414))

- **40-03**: Add Drug Database + Nutrient File prompts/resources + tests
  ([`f63a22a`](https://github.com/ReyemTech/mcp-canada/commit/f63a22a393a91947e82cd949c1abd17882f37263))

- **40-03**: Add Open Parliament + Recalls prompts/resources + tests
  ([`e2a43ff`](https://github.com/ReyemTech/mcp-canada/commit/e2a43ff5712481df9e66ad55d8607e80062f6bc0))

- **40-04**: Add Ontario and Toronto prompts.py and resources.py
  ([`684abac`](https://github.com/ReyemTech/mcp-canada/commit/684abac3be22f3cce5f2aed0715a05f8369cf8cc))

- **40-04**: Add Weather and IRCC prompts.py and resources.py
  ([`ebed253`](https://github.com/ReyemTech/mcp-canada/commit/ebed253b5fe89e3b41d8db01711d53b736477e99))

- **40-05**: Add integration tests for prompts and resources through MCP Client
  ([`74c8bb1`](https://github.com/ReyemTech/mcp-canada/commit/74c8bb1c4aada7a28da682ce8659ad8aa01b77e8))

### Refactoring

- Extract shared reshape utilities and apply to BOC tools
  ([`485afdb`](https://github.com/ReyemTech/mcp-canada/commit/485afdb4c005e5155484cff24bc659522a4806f8))

### Testing

- **12**: Complete UAT - 8/8 passed
  ([`414c387`](https://github.com/ReyemTech/mcp-canada/commit/414c387102e9d6efb8579f32362324f8b3b3656a))

- **40**: Complete UAT - 8/8 passed
  ([`2d4ba74`](https://github.com/ReyemTech/mcp-canada/commit/2d4ba7418fecd1cfdea94bfb2af4c76c93a491c3))

- **40-01**: Add failing tests for BoC prompts and resources
  ([`7843f45`](https://github.com/ReyemTech/mcp-canada/commit/7843f45bd5eede1a8029499528ea653386d14656))

- **40-04**: Add failing tests for Ontario and Toronto prompts and resources
  ([`72e7d85`](https://github.com/ReyemTech/mcp-canada/commit/72e7d85642ea1d54b20257b28d65ee59eb678771))

- **40-04**: Add failing tests for Weather and IRCC prompts and resources
  ([`2df020a`](https://github.com/ReyemTech/mcp-canada/commit/2df020a6b04bd4f020cc77eb0e4c8ece3a7e4a30))


## v0.4.4 (2026-04-09)

### Bug Fixes

- Add missing IRCC ops breakdowns — new citizens and TRV V-1 approved
  ([`448f503`](https://github.com/ReyemTech/mcp-canada/commit/448f5032c393c0db34e4d06653c10d735ad8d99e))

### Chores

- Sync uv.lock after release
  ([`568cad8`](https://github.com/ReyemTech/mcp-canada/commit/568cad8f862c34e2894595c23ef5ec86da34db77))


## v0.4.3 (2026-04-08)

### Bug Fixes

- Move xlrd to base dependencies for adhoc_pr support
  ([`6f21d74`](https://github.com/ReyemTech/mcp-canada/commit/6f21d741704018ed6435d0c37045cfc0fc5fce04))

### Chores

- Sync uv.lock after release
  ([`ea33ba0`](https://github.com/ReyemTech/mcp-canada/commit/ea33ba0cd3ea938261a796e7e754748b641650da))


## v0.4.2 (2026-04-08)

### Bug Fixes

- Print version to stderr on server start
  ([`b583860`](https://github.com/ReyemTech/mcp-canada/commit/b5838601b247955f1144b39284d369f120800e53))

### Chores

- Sync uv.lock after release
  ([`c30083a`](https://github.com/ReyemTech/mcp-canada/commit/c30083a10f817169463ea1898d59cf670a831216))


## v0.4.1 (2026-04-08)

### Bug Fixes

- Include version in list_modules response
  ([`b53148a`](https://github.com/ReyemTech/mcp-canada/commit/b53148a6957afe44fb3c493ccfcaeef7cb915481))

### Chores

- Sync uv.lock after release
  ([`5d7752c`](https://github.com/ReyemTech/mcp-canada/commit/5d7752c52aeab8805934bfc0b6c4765de374b4e6))


## v0.4.0 (2026-04-08)

### Bug Fixes

- **11**: Clean group names in 2-label nesting
  ([`7ccee5e`](https://github.com/ReyemTech/mcp-canada/commit/7ccee5e7c6a73a07875fb4801416e106a49ca088))

- **11**: Clean up IRCC column names and filter all-null data rows
  ([`d6093a3`](https://github.com/ReyemTech/mcp-canada/commit/d6093a39da8c74194591fc6899bd40db9914cf74))

- **11**: Forward-fill label columns in IRCC multi-row data
  ([`8831b49`](https://github.com/ReyemTech/mcp-canada/commit/8831b499559e1492884b39dbfae0ec8f610b1da2))

- **11**: Resolve pyright and ruff errors in test_parsers.py
  ([`14cb3e1`](https://github.com/ReyemTech/mcp-canada/commit/14cb3e11ac946b08f56efed842839573aa408308))

- **11**: Revise plans based on checker feedback
  ([`ac3becc`](https://github.com/ReyemTech/mcp-canada/commit/ac3becc4b42a13333fdd5a0b9cc9a6858d114ff0))

- **11**: Support French quarter names (t1-t4) in nested reshaping
  ([`8e4b9aa`](https://github.com/ReyemTech/mcp-canada/commit/8e4b9aa5d97eb1f19689d9cdd0cee4c56139801f))

- **11**: Transliterate accented chars in _normalize_key
  ([`d35c7ef`](https://github.com/ReyemTech/mcp-canada/commit/d35c7ef0058431f1406686857648e14fa0a53ac6))

- **11**: Treat empty strings as missing in IRCC label forward-fill
  ([`63988f5`](https://github.com/ReyemTech/mcp-canada/commit/63988f51c5e4cf280f1f3ecbb117e523eee1119d))

### Chores

- Sync uv.lock after release
  ([`065a0f5`](https://github.com/ReyemTech/mcp-canada/commit/065a0f599a26a1ad472c2e693726a259324d3255))

### Documentation

- Add Phase 11 — IRCC Immigration module
  ([`34cce16`](https://github.com/ReyemTech/mcp-canada/commit/34cce164bb21383aa15252926c1c8d7a946295e8))

- Update Phase 11 — shared file parsers + IRCC module
  ([`66372ad`](https://github.com/ReyemTech/mcp-canada/commit/66372ad14fe017ded422d2d87626389f01efd063))

- **11**: Add research and validation strategy
  ([`fa2999e`](https://github.com/ReyemTech/mcp-canada/commit/fa2999ee384a2c7242e46319280a42da1d96fcd0))

- **11**: Capture phase context
  ([`2396f76`](https://github.com/ReyemTech/mcp-canada/commit/2396f768be5e9a2ff86aa07de37e6c927c642674))

- **11**: Create gap closure plan for IRCC multi-row header parsing
  ([`0189f93`](https://github.com/ReyemTech/mcp-canada/commit/0189f93886a2dde08b0df639fcfbb89e9011b3e6))

- **11**: Create phase plan — shared parser + IRCC module
  ([`e35bc43`](https://github.com/ReyemTech/mcp-canada/commit/e35bc4347221cfc68ce1044c1d2cd7e814a64930))

- **11**: Research phase domain — shared parsers + IRCC immigration
  ([`cfce467`](https://github.com/ReyemTech/mcp-canada/commit/cfce467c4547450f4408e47ee2c6b9ef1cbcfe3d))

- **11-01**: Complete shared file parsers plan
  ([`89afcad`](https://github.com/ReyemTech/mcp-canada/commit/89afcadaf55169d8910c40515d53294df4d2a7e9))

- **11-02**: Complete IRCC module skeleton plan
  ([`bc770eb`](https://github.com/ReyemTech/mcp-canada/commit/bc770eb89981b418979f355268615026ce2dcd7d))

- **11-03**: Complete IRCC tool functions plan
  ([`a940b4f`](https://github.com/ReyemTech/mcp-canada/commit/a940b4f849a5269387e11e8c90bb9a17b3952b03))

- **11-04**: Complete IRCC multi-row header parser plan
  ([`457f7e8`](https://github.com/ReyemTech/mcp-canada/commit/457f7e8948eafefbaf744beafa149ce4cc3b0422))

- **phase-11**: Complete phase execution
  ([`87a7f08`](https://github.com/ReyemTech/mcp-canada/commit/87a7f08e04956a03c700b048542319b71ff2cdcd))

- **state**: Record phase 11 context session
  ([`622b3a4`](https://github.com/ReyemTech/mcp-canada/commit/622b3a4f6354df792ace3de258b509411fff2154))

### Features

- **11**: Add filter and recent params to all IRCC tools
  ([`b29663c`](https://github.com/ReyemTech/mcp-canada/commit/b29663ccfede51dd7193648b0c01eceac2636cbc))

- **11**: Auto-convert numeric strings to int/float in parser
  ([`4cfc8b6`](https://github.com/ReyemTech/mcp-canada/commit/4cfc8b61277446f2775b19b752544658963b8c54))

- **11**: Fix 2-label forward-fill and add hierarchical nesting
  ([`66fe56a`](https://github.com/ReyemTech/mcp-canada/commit/66fe56a6574c49ca114bf7dd1266eba47c9f1a50))

- **11**: Reshape IRCC tool output to nested year > quarter > month format
  ([`4b5bc2f`](https://github.com/ReyemTech/mcp-canada/commit/4b5bc2ff748dd3e42ca5597947e66692072f1643))

- **11-01**: Implement shared file parsers (XLSX/CSV/XLS)
  ([`618c69a`](https://github.com/ReyemTech/mcp-canada/commit/618c69af2012e7f8640e475e26f9efd509d6f2fd))

- **11-02**: Create IRCC module skeleton and dataset registry
  ([`f767d21`](https://github.com/ReyemTech/mcp-canada/commit/f767d21426ff6e64ea886967b9d860e50baae972))

- **11-02**: Implement IRCC client functions
  ([`b6a0f1d`](https://github.com/ReyemTech/mcp-canada/commit/b6a0f1d7f875079711d7c1b8778cd0d96c46a79c))

- **11-03**: Add IRCC integration tests and update README
  ([`6bbb134`](https://github.com/ReyemTech/mcp-canada/commit/6bbb134b58838c70340cb9920a23c3d864b3c41d))

- **11-03**: Implement 10 ircc_ tool functions with TDD
  ([`d3f8a7a`](https://github.com/ReyemTech/mcp-canada/commit/d3f8a7a8832c2f473bb4bf5a643e34a47a1128a7))

- **11-04**: Add _parse_ircc_xlsx + DATASET_PARSE_CONFIG for multi-row merged headers
  ([`24c3f1a`](https://github.com/ReyemTech/mcp-canada/commit/24c3f1a728ea60577a7f018fcd953151086b5a25))

- **11-04**: Wire client.py to pass DATASET_PARSE_CONFIG to fetch_and_parse
  ([`cf47603`](https://github.com/ReyemTech/mcp-canada/commit/cf47603ed2c4959cda4d80b136c5b3391b3624e4))

### Testing

- **11**: Complete UAT - 10/10 passed, all gaps resolved
  ([`6b8c9c1`](https://github.com/ReyemTech/mcp-canada/commit/6b8c9c1414d72fed80679615f406585e2050c565))

- **11**: Complete UAT - 6 passed, 2 issues
  ([`784a065`](https://github.com/ReyemTech/mcp-canada/commit/784a065d6a14068a6957e5076e431131390f32d2))

- **11**: Complete UAT - 9 passed, 1 minor issue
  ([`55f7ed7`](https://github.com/ReyemTech/mcp-canada/commit/55f7ed77519fbf5fb3ea8b3afa4a0046f9a5bde8))

- **11**: Diagnose IRCC header parsing blocker
  ([`1d054bb`](https://github.com/ReyemTech/mcp-canada/commit/1d054bb69386accb1e23c6fcf3d3dc67a77612d9))

- **11-01**: Add failing tests for shared file parsers
  ([`74402c5`](https://github.com/ReyemTech/mcp-canada/commit/74402c51c2b52b10ccac10d2bc6b689841824044))

- **11-02**: Add failing tests for IRCC client functions
  ([`fa46086`](https://github.com/ReyemTech/mcp-canada/commit/fa460866995bc6b6ae51964b2aba47190c1d5211))


## v0.3.0 (2026-04-08)

### Bug Fixes

- Add retry and larger timeout for StatCan transient failures
  ([`52361a3`](https://github.com/ReyemTech/mcp-canada/commit/52361a3330c2373353d2fcf96a546cf147dac638))

- Handle nullable cansim_id and auto-append datetime for bulk vector
  ([`146f9df`](https://github.com/ReyemTech/mcp-canada/commit/146f9df8e7e191171e1e750477953f0cfb1c63fc))

- Handle StatCan responseStatusCode 2 (no data) gracefully
  ([`23dd4b5`](https://github.com/ReyemTech/mcp-canada/commit/23dd4b5bcc1163504bd425bcf4335e0d1e6dcd8b))

- Increase timeout and add retry for StatCan cube list fetch
  ([`e01f1e8`](https://github.com/ReyemTech/mcp-canada/commit/e01f1e8233778f0baced86c5932d8788bd293c24))

- **07**: Revise plans based on checker feedback
  ([`48ec8f5`](https://github.com/ReyemTech/mcp-canada/commit/48ec8f5949b426bab6d77d1fd9a03bcf592835df))

### Chores

- Add project config
  ([`b0f5fe1`](https://github.com/ReyemTech/mcp-canada/commit/b0f5fe1b482581a9053dd539ad5390accfde8b27))

- Sync uv.lock after release
  ([`65da8a0`](https://github.com/ReyemTech/mcp-canada/commit/65da8a02d362144422861a986eb8ae0b0188d660))

- **08-02**: Mark SC-04 through SC-09, SC-13, SC-14 requirements complete
  ([`7ee80e4`](https://github.com/ReyemTech/mcp-canada/commit/7ee80e4c1c8ee0145267619f203f9f118c8e9a8d))

### Documentation

- Complete project research
  ([`1a6ee06`](https://github.com/ReyemTech/mcp-canada/commit/1a6ee067de7875b7d465e7483febd7a333e446a2))

- Create roadmap (4 phases)
  ([`24ee1e7`](https://github.com/ReyemTech/mcp-canada/commit/24ee1e749f7d585f53c17e93c07753d17f0a58fa))

- Define v1.1 requirements
  ([`3264182`](https://github.com/ReyemTech/mcp-canada/commit/3264182978066543a198f9112627b9458faba529))

- Initialize project
  ([`d714df8`](https://github.com/ReyemTech/mcp-canada/commit/d714df87cd249d28ad24c6bd68ce33a115449d14))

- Promote install command to top of Quick Start
  ([`e63f328`](https://github.com/ReyemTech/mcp-canada/commit/e63f3280672bd5dd3bb63585109f110e1716cf84))

- **07**: Capture phase context
  ([`42297fa`](https://github.com/ReyemTech/mcp-canada/commit/42297faf8ec75b7544af5a28dc5fd916435cbef0))

- **07**: Create phase plan — 3 plans, 2 waves
  ([`4c097b6`](https://github.com/ReyemTech/mcp-canada/commit/4c097b6c4c87a0a9169a161881638df642516b7c))

- **07**: Create phase plans (3 plans, 2 waves) — verified
  ([`804dc0e`](https://github.com/ReyemTech/mcp-canada/commit/804dc0e50477f9cfcb1afc295c8f3b8dff0a7c43))

- **07**: Research phase — aiosqlite datastore + StatCan SSL strategy
  ([`d8f0263`](https://github.com/ReyemTech/mcp-canada/commit/d8f026342cbc49a2c37bfd544059f46189948e6d))

- **07-01**: Complete datastore module skeleton plan
  ([`fa02c9b`](https://github.com/ReyemTech/mcp-canada/commit/fa02c9bdb44a81884e4f5641cdb7fbf0852a25ff))

- **07-02**: Complete datastore tools plan — 6 ds_ tools, 26 unit tests, 6 integration tests
  ([`897caf2`](https://github.com/ReyemTech/mcp-canada/commit/897caf2d2a88aabc340e7a70c4bca5d8c160fd14))

- **07-03**: Complete StatCan SSL probe + module stub plan
  ([`3b8b818`](https://github.com/ReyemTech/mcp-canada/commit/3b8b8183e9b66f6f723e6f1e40b8a0188297e355))

- **08**: Capture phase context
  ([`83c979f`](https://github.com/ReyemTech/mcp-canada/commit/83c979f4cb9742696b5adc2e308dc34079564423))

- **08**: Research phase — StatCan WDS endpoints, BM25 search, response shapes
  ([`d9d28eb`](https://github.com/ReyemTech/mcp-canada/commit/d9d28eb6665547ea02718b11437d7a583a0d7351))

- **08-01**: Complete StatCan WDS client foundation plan
  ([`681c0ed`](https://github.com/ReyemTech/mcp-canada/commit/681c0edc99d16c2fd914cc810a15e5742d750e32))

- **08-02**: Complete plan — 8 WDS client functions for series info, data retrieval, and monitoring
  ([`4e1a5ef`](https://github.com/ReyemTech/mcp-canada/commit/4e1a5efe12211694d6810620dc93a60c553393ab))

- **08-03**: Complete StatCan WDS tools plan — Phase 8 feature-complete
  ([`74a672f`](https://github.com/ReyemTech/mcp-canada/commit/74a672f293c5751e52d657a88bb1cf5a28250b06))

- **08-statcan-wds**: Create phase plan — 3 plans across 3 waves
  ([`990e2c7`](https://github.com/ReyemTech/mcp-canada/commit/990e2c7927c0593f9c046a4a4842fde6bb87dd15))

- **09**: Capture phase context
  ([`0b40cd1`](https://github.com/ReyemTech/mcp-canada/commit/0b40cd11bacae8c50ebc727541444bddb71750e7))

- **09**: Create phase plan — 2 plans in 2 waves
  ([`b6287ca`](https://github.com/ReyemTech/mcp-canada/commit/b6287ca7e45020e42e8babc97ff2e1f30441f59a))

- **09**: Research phase SDMX + composite domain
  ([`7bc81a1`](https://github.com/ReyemTech/mcp-canada/commit/7bc81a1262c1a5bb04bdd02989e72deddc9addf1))

- **09-01**: Complete SDMX client layer plan — constants, schemas, 3 async functions
  ([`fe409ed`](https://github.com/ReyemTech/mcp-canada/commit/fe409ed42d65b606b92f8c6f4b8ae85c5db8d817))

- **09-02**: Complete SDMX tool layer plan — summary, state, roadmap updated
  ([`71fa4a8`](https://github.com/ReyemTech/mcp-canada/commit/71fa4a872852f2dbc1c0bc961cba38f8e943b348))

- **10**: Capture phase context
  ([`4babf34`](https://github.com/ReyemTech/mcp-canada/commit/4babf34c878569c7f113f8d07d5c3ac07e208988))

- **10-01**: Complete tests-docs plan — 96.39% coverage, all sc_/ds_ tools have integration tests
  ([`c81d534`](https://github.com/ReyemTech/mcp-canada/commit/c81d5340f8f04040587a31a1ff87b8a5c812b154))

- **10-02**: Complete documentation updates — README counts, StatCan credit, cross-module SQL
  examples
  ([`dadc105`](https://github.com/ReyemTech/mcp-canada/commit/dadc105b5625e1082270f4f4f57bcd44ccc6eb33))

- **10-tests-docs**: Create phase plan
  ([`a5d5522`](https://github.com/ReyemTech/mcp-canada/commit/a5d55227092cebe2cd8d05f3bb5bb7d011d45812))

- **phase-07**: Complete phase execution
  ([`6f702c9`](https://github.com/ReyemTech/mcp-canada/commit/6f702c9dd563d5764c706a2d387b94412139a47c))

- **phase-08**: Complete phase execution
  ([`6e267db`](https://github.com/ReyemTech/mcp-canada/commit/6e267dbbdf2321f1f3a222bbb4b99207b48d8638))

- **phase-09**: Complete phase execution
  ([`b4a6caa`](https://github.com/ReyemTech/mcp-canada/commit/b4a6caa5a7f8ccb87bc8ec68566ffe34082ef229))

- **phase-10**: Complete phase execution — ALL PHASES DONE
  ([`85712bc`](https://github.com/ReyemTech/mcp-canada/commit/85712bce791b5a008951f99e67267e6922d6b28b))

- **phase-7**: Add validation strategy
  ([`4ac27d1`](https://github.com/ReyemTech/mcp-canada/commit/4ac27d1e4678cab4136808ae09ff98ca1e72e594))

- **phase-8**: Add research and validation strategy
  ([`cc95aab`](https://github.com/ReyemTech/mcp-canada/commit/cc95aabd8692685938fc6301b7a1853642da1ce6))

- **phase-9**: Add research and validation strategy
  ([`29ced48`](https://github.com/ReyemTech/mcp-canada/commit/29ced4878e34216f671f3e44e0cd61fb554e26ab))

- **state**: Record phase 10 context session
  ([`7a88eb0`](https://github.com/ReyemTech/mcp-canada/commit/7a88eb011a06c96f9270367ee625ef4acd3d031e))

- **state**: Record phase 7 context session
  ([`6495d3a`](https://github.com/ReyemTech/mcp-canada/commit/6495d3ac75aaa3eef84f73f035a1b9b5e4f933e2))

- **state**: Record phase 8 context session
  ([`72763fe`](https://github.com/ReyemTech/mcp-canada/commit/72763fec2a2e4a6a09ada20c2495e9c256ac02f5))

- **state**: Record phase 9 context session
  ([`0f582cd`](https://github.com/ReyemTech/mcp-canada/commit/0f582cd25eec1d1cfd76651d36ee6e7630159685))

### Features

- **07-01**: Add datastore module skeleton and async SQLite client
  ([`c0bfade`](https://github.com/ReyemTech/mcp-canada/commit/c0bfade395db08677f6499b74046eec6b424fd21))

- **07-02**: Add TestDatastoreScenarios integration tests + coverage gate
  ([`07abd2a`](https://github.com/ReyemTech/mcp-canada/commit/07abd2a385f27a427c77fec3e9a93697aab8d263))

- **07-02**: Implement 6 ds_ datastore tools with TDD
  ([`674623b`](https://github.com/ReyemTech/mcp-canada/commit/674623b403d478a54786b74781b4da4e703641d5))

- **07-03**: StatCan SSL probe + module stub
  ([`232633c`](https://github.com/ReyemTech/mcp-canada/commit/232633cb885126b2c14c8a5a517ecd60d8cee814))

- **08-01**: StatCan WDS client foundation — schemas, BM25 search, metadata
  ([`ea7611f`](https://github.com/ReyemTech/mcp-canada/commit/ea7611f09dde87ebc124b313a37a75a3e660cca4))

- **08-02**: Add date range, bulk vector, and change monitoring client functions
  ([`52b3685`](https://github.com/ReyemTech/mcp-canada/commit/52b36856b2d99a2a7a4d16a691b4b0f59bc579e3))

- **08-02**: Add series info and latest-N client functions
  ([`2df4baf`](https://github.com/ReyemTech/mcp-canada/commit/2df4baf5c7a77cc8a439de4389dc82dd8031fe17))

- **08-03**: Add 11 sc_ tool functions with unit tests
  ([`4ce2f13`](https://github.com/ReyemTech/mcp-canada/commit/4ce2f13b456d15be79d232d5fac3d28f8414db4e))

- **08-03**: Add StatCan integration tests and fix 3 schema bugs
  ([`1f711b0`](https://github.com/ReyemTech/mcp-canada/commit/1f711b0167d1bc4be58bd6993edbc61433001baf))

- **09-01**: SDMX client functions with unit tests
  ([`2fb10bc`](https://github.com/ReyemTech/mcp-canada/commit/2fb10bc39314748b4641eab09020770d0f3b6534))

- **09-01**: SDMX constants, schemas, and test fixtures
  ([`bc0ab8f`](https://github.com/ReyemTech/mcp-canada/commit/bc0ab8f6be81b2c375236ba85b86ac944560694e))

- **09-02**: Add 4 SDMX tool functions with unit tests
  ([`ea11f5a`](https://github.com/ReyemTech/mcp-canada/commit/ea11f5a6e9081679702fd259dd661d5e5b8cb826))

- **09-02**: Add TestSdmxScenarios integration tests
  ([`9ea359f`](https://github.com/ReyemTech/mcp-canada/commit/9ea359f8d1829e1539ecea63ab87f27f396fb626))

- **10-01**: Add integration tests for 4 missing StatCan WDS tools
  ([`f340119`](https://github.com/ReyemTech/mcp-canada/commit/f340119c8bffd05bef55f921df9c7d108668f229))

- **10-02**: Add 4 cross-module SQL examples to EXAMPLES.md
  ([`2444f84`](https://github.com/ReyemTech/mcp-canada/commit/2444f84cfc23fba659831606b99410ec20932415))

- **10-02**: Update README with accurate tool counts and StatCan credit
  ([`abefe76`](https://github.com/ReyemTech/mcp-canada/commit/abefe7649682b89c20180faf7fc3baecf75c0786))

### Testing

- **08**: Complete UAT — 11 passed, 3 issues (all fixed)
  ([`3a367f4`](https://github.com/ReyemTech/mcp-canada/commit/3a367f4fe3034b0cb1a9b0e051d10093e9907b94))


## v0.2.0 (2026-04-07)

### Bug Fixes

- Move installer tests to tests/ and exclude installer.py from coverage
  ([`b0a903b`](https://github.com/ReyemTech/mcp-canada/commit/b0a903beeb867339390e7154577aec40631541aa))

### Chores

- Add InquirerPy dependency for install subcommand TUI
  ([`e89b217`](https://github.com/ReyemTech/mcp-canada/commit/e89b2170abe053e8a07af43e11594d1b2820d6d1))

- Sync uv.lock after release
  ([`826bf39`](https://github.com/ReyemTech/mcp-canada/commit/826bf39c2c40f5a8a5153630cb6ccd60a3434a8a))

### Documentation

- Add cross-API examples showcasing multi-module intelligence
  ([`a941946`](https://github.com/ReyemTech/mcp-canada/commit/a94194621ee565abf38107075454881bc8536fb5))

- Add install subcommand to README
  ([`0cdaf34`](https://github.com/ReyemTech/mcp-canada/commit/0cdaf341434658d6f5697525bce9dc36f7bf03d8))

### Features

- Add install subcommand to CLI with backward-compatible argparse
  ([`957018b`](https://github.com/ReyemTech/mcp-canada/commit/957018b8d9867f642065d71200c799b396530879))

- Add installer module with platform registry, config generation, and merge logic
  ([`baf6b98`](https://github.com/ReyemTech/mcp-canada/commit/baf6b98d6f7e48548b80487bc787d6f791fb444a))


## v0.1.3 (2026-04-07)

### Bug Fixes

- **ci**: Resolve pyright errors on MCP content type union
  ([`9fb300c`](https://github.com/ReyemTech/mcp-canada/commit/9fb300cecb6ff8caeb5e5173c280f1c1b0e0988c))

### Chores

- Add workflow_dispatch trigger to CI workflow
  ([`063da1b`](https://github.com/ReyemTech/mcp-canada/commit/063da1b6002c1b2d1d35a97c1b0c2e37509086a9))

- Sync uv.lock after release
  ([`d65bcb4`](https://github.com/ReyemTech/mcp-canada/commit/d65bcb4641917d5961d0fc104f0423aa0cbae40d))

### Documentation

- Add CI and integration test badges to README
  ([`1ab9a29`](https://github.com/ReyemTech/mcp-canada/commit/1ab9a29fa6305642923fb8de2ad53185785ac8c0))


## v0.1.2 (2026-04-06)

### Bug Fixes

- **ci**: Sync uv.lock after semantic release version bump
  ([`61ede70`](https://github.com/ReyemTech/mcp-canada/commit/61ede70770b98e391c38d68e6bb07771b77daa9f))


## v0.1.1 (2026-04-06)

### Bug Fixes

- **dist**: Exclude __tests__/ from PyPI wheel
  ([`196aedd`](https://github.com/ReyemTech/mcp-canada/commit/196aedddaf0d982b6bedf3cb726f6a605d88373f))

### Chores

- Regenerate uv.lock after version bump
  ([`54c849d`](https://github.com/ReyemTech/mcp-canada/commit/54c849d2aca7d92acdd3cf35c9d49c420d7b033e))


## v0.1.0 (2026-04-06)

- Initial Release

All notable changes to mcp-canada will be documented in this file.
This changelog is automatically generated by [python-semantic-release](https://python-semantic-release.readthedocs.io/).
