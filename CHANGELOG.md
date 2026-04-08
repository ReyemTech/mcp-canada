# Changelog

<!-- CHANGELOG -->

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
