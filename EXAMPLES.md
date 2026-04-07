# Examples: Cross-API Intelligence with mcp-canada

> Canadian government data becomes dramatically more powerful when you can query multiple APIs in a single conversation.

These examples show what happens when an AI agent can reach across **7 federal APIs** simultaneously — producing insights that no single database can surface alone. Each example is a real prompt you can give your agent today.

---

## Table of Contents

- [Economy & Policy](#economy--policy)
- [Environment & Climate](#environment--climate)
- [Health & Safety](#health--safety)
- [Food & Nutrition](#food--nutrition)
- [Developer Patterns](#developer-patterns)

---

## Economy & Policy

### 1. The Inflation Accountability Clock

> "CPI spiked to 8.1% in 2022. What did the Bank do, what bills addressed it, and how did the votes go?"

**APIs:** Bank of Canada + Open Parliament

```
Step 1: boc_get_inflation_data(indicator="total", start_date="2021-01-01", end_date="2023-06-01")
        → Full CPI timeline showing the spike to 8.1%

Step 2: boc_get_interest_rates(rate_type="policy", start_date="2021-01-01")
        → The Bank of Canada's eight consecutive rate hikes overlaid

Step 3: parl_search_bills(session="44-1")
        → Find cost-of-living and affordability bills introduced during the spike

Step 4: parl_get_bill_details(bill_id="44-1/C-31")
        → Status, sponsor, and linked vote IDs for the affordability bill

Step 5: parl_get_ballots(vote_id="44-1/...")
        → Individual MP yea/nay on cost-of-living votes
```

**The insight:** CPI crossed 8% while the Bank hiked rates eight consecutive times — but you can trace which affordability bills were introduced during the spike, how long they sat before a vote, and exactly which MPs voted against relief measures their own party championed. The agent maps the lag between economic reality and democratic response.

---

### 2. The Carbon Policy Calculator

> "Show me the full carbon price debate in data: the economic pressure, the vote record, and whether measured warming justifies it."

**APIs:** Bank of Canada + Open Parliament + Weather/Climate + CKAN

```
Step 1: boc_get_inflation_data(indicator="total")
        → CPI trend including energy component

Step 2: boc_get_commodity_prices(commodity_type="energy")
        → BCPI energy index (crude oil, natural gas)

Step 3: parl_get_bill_details(bill_id="44-1/C-234")
        → The agricultural carbon tax exemption bill — status, sponsor, vote links

Step 4: parl_get_ballots(vote_id="44-1/...")
        → Individual MP yea/nay on the carbon exemption vote

Step 5: wx_get_climate_trends(measurement_type="temperature")
        → AHCCD long-term warming trend at Canadian stations

Step 6: ckan_search_datasets(query="greenhouse gas emissions province Canada")
        → ECCC emissions inventory datasets
```

**The insight:** Ottawa's AHCCD record shows +2.1C since 1981 — outpacing the global average. You can see exactly which MPs voted for the farm fuel carbon exemption, overlay that against their riding's measured warming trend, and cross-reference ECCC emissions data. Four federal data systems, one conversation, zero spin.

---

### 3. Riding Accountability Brief — Climate Data vs. Voting Record

> "Pick a riding hit hard by floods. How does the MP actually vote on climate and infrastructure bills?"

**APIs:** Open Parliament + Weather/Climate + Bank of Canada

```
Step 1: parl_search_by_riding("Abbotsford")
        → Get the MP for one of BC's most flood-affected ridings

Step 2: parl_get_voting_record(politician="...")
        → Their voting record — house-wide totals on each division

Step 3: parl_get_ballots(vote_id="44-1/...")
        → Their individual yea/nay on specific climate and infrastructure votes

Step 4: wx_compare_climate_periods(station_id="...",
          period1_start="2000-01-01", period1_end="2010-12-31",
          period2_start="2014-01-01", period2_end="2023-12-31")
        → Measured climate shift in their constituency

Step 5: boc_get_commodity_prices(commodity_type="agriculture")
        → Economic impact on local farming
```

**The insight:** A data-backed accountability brief for any riding: how your MP votes on climate bills, cross-referenced against measured temperature and precipitation shifts in their own constituency and the commodity price impact on local agriculture. Every local outlet can run this for their riding.

---

### 4. The Silent Drug Shortage

> "How many drugs went off-market during the supply chain crisis — and what bills addressed it?"

**APIs:** Drug Product Database + Recalls + Open Parliament

```
Step 1: drug_search(company="Apotex") + drug_search(company="Teva Canada")
        → All products from major generic manufacturers

Step 2: drug_get_status(drug_code=...) [for each product]
        → Track MARKETED → CANCELLED/DORMANT transitions with dates

Step 3: drug_get_therapeutic_class(drug_code=...)
        → Which ATC categories were hit hardest (antibiotics? cardiovascular?)

Step 4: recalls_get_health_products(keyword="shortage")
        → Recall alerts triggered by supply failures

Step 5: parl_search_bills(session="44-1")
        → Find drug safety or supply chain bills introduced in response
```

**The insight:** The Drug Product Database reveals which therapeutic classes lost the most active products during the supply crisis. Cross-referencing with recall alerts shows when shortages became safety events. The parliamentary bill record reveals whether legislation followed — or whether the regulatory crisis went unaddressed on the Hill.

---

## Environment & Climate

### 5. The Wildfire Economy Report

> "What happens to Canada's lumber prices when a major wildfire season unfolds — and what do MPs say about it?"

**APIs:** Weather/Climate + Bank of Canada + CKAN + Open Parliament

```
Step 1: wx_get_aqhi(lat=49.88, lon=-119.49)
        → Air quality during BC wildfire season (AQHI 10+ for days)

Step 2: boc_get_commodity_prices(commodity_type="forestry")
        → BCPI forestry sub-index over the same period

Step 3: ckan_search_datasets(query="wildfire burned area British Columbia")
        → National Forestry Database burn statistics

Step 4: parl_get_debates(date="2023-08-15")
        → Parliamentary debates during peak fire season — what was discussed?
```

**The insight:** Physical event (17.3M hectares burned in 2023) → market reaction (forestry BCPI declining while demand held — a supply-side crash) → policy response (or silence). The AQHI data *predates* the economic damage by weeks — communities with sustained AQHI 10+ are experiencing both the health crisis and the coming supply chain shutdown simultaneously.

---

### 6. The Prairie Drought Chain

> "Trace the path from Saskatchewan soil drought to the Canadian dollar."

**APIs:** Weather/Climate + Bank of Canada

```
Step 1: wx_get_climate_daily(station_id="...",
          start_date="2021-06-01", end_date="2021-08-31")
        → The 2021 heat dome: daily temperature records across the Prairies

Step 2: wx_compare_climate_periods(station_id="...",
          period1_start="2015-01-01", period1_end="2018-12-31",
          period2_start="2020-01-01", period2_end="2023-12-31")
        → Growing season precipitation collapse

Step 3: boc_get_commodity_prices(commodity_type="agriculture",
          start_date="2021-01-01", end_date="2022-06-01")
        → BCPI agriculture sub-index response

Step 4: boc_get_exchange_rates(currency="USD", start_date="2021-01-01")
        → CAD/USD weakening as canola production collapsed 35%
```

**The insight:** The CAD is called a "petro-loonie," but the BCPI agriculture sub-index is an uncredited co-driver. In 2021, energy prices rose while agriculture collapsed — the two sub-indices pulled in opposite directions. An analyst tracking only energy would have missed the full currency signal. The drought index gives you the leading indicator 4-8 weeks before the BCPI updates.

---

### 7. The Flood Intelligence Brief

> "There's heavy rain in Southern Ontario. Give me a flood risk assessment for the Grand River basin."

**APIs:** Weather/Hydro + Weather/Current + Weather/Severe

```
Step 1: wx_search_hydro_stations(province="ON", name="Grand River")
        → Find station: 02GA010, Grand River at Galt

Step 2: wx_get_flood_risk(station_number="02GA010")
        → Current level vs. historical max = risk percentage

Step 3: execute_batch([
          wx_get_water_levels(station_number="02GA010"),
          wx_get_water_flow(station_number="02GA010"),
          wx_get_weather_alerts(province="ON"),
          wx_get_radar_data(lat=43.36, lon=-80.31),
          wx_get_aqhi(lat=43.36, lon=-80.31)
        ])
        → 5 simultaneous calls across hydrology + weather + air quality
```

**The insight:** "Grand River at Galt is at 78% of historical max. Active rainfall warning. Radar shows heavy precipitation 40km upstream. Risk level: HIGH." Three weather submodules fused into a single real-time risk picture — the kind of brief that would take an emergency manager hours to compile manually.

---

### 8. Heating Degree Days — The Quiet Deflation

> "The home heating carbon tax exemption was a huge political fight. What does the actual heating data say?"

**APIs:** Weather/Climate + Bank of Canada + Open Parliament

```
Step 1: wx_get_climate_normals(station_id="8202251")
        → Halifax 1981-2010 heating degree day baseline

Step 2: wx_compare_climate_periods(station_id="8202251",
          period1_start="1990-01-01", period1_end="2000-12-31",
          period2_start="2014-01-01", period2_end="2023-12-31")
        → HDD decline in Atlantic Canada (steepest in the country)

Step 3: boc_get_inflation_data(indicator="total")
        → CPI energy component falling as heating load shrinks

Step 4: parl_get_bill_details(bill_id="44-1/C-234")
        → The home heating exemption bill — sponsor, status, vote links
```

**The insight:** Atlantic Canada's heating load is declining — meaning future carbon costs on home heating are *structurally shrinking anyway*. The policy debate was conducted as if climate change didn't exist, even though declining HDDs are the most direct evidence that it does.

---

## Health & Safety

### 9. The Opioid Supply Chain Map

> "Which opioids are currently marketed in Canada, how many have been recalled, and what legislation exists?"

**APIs:** Drug Product Database + Recalls + Open Parliament + CKAN

```
Step 1: drug_search(company="PURDUE")
        → Map all opioid products by manufacturer

Step 2: drug_get_therapeutic_class(drug_code=...)
        → Confirm ATC N02A (opioid analgesics)

Step 3: drug_get_status(drug_code=...)
        → MARKETED vs. CANCELLED vs. DORMANT for each

Step 4: recalls_get_health_products(keyword="opioid")
        → Health product recalls in this class

Step 5: parl_search_bills(session="44-1")
        → Bills addressing substance policy in the current session

Step 6: ckan_search_datasets(query="opioid overdose deaths Canada")
        → PHAC mortality datasets
```

**The insight:** The Drug Product Database shows which opioid formulations remain on the market and which manufacturers produce them. The recall system shows safety failures. The bill record shows what legislation was introduced. PHAC datasets show the death toll. Four federal data systems — pharmaceutical registry, safety alerts, parliamentary record, and epidemiology — assembled in one conversation to reveal what no single database can show.

---

### 10. The Recalled Pill's Paper Trail

> "A drug was recalled for contamination. What's the full pharmaceutical profile, and what's the company's track record?"

**APIs:** Recalls + Drug Product Database

```
Step 1: recalls_get_health_products(keyword="contamination")
        → Recent health product recalls

Step 2: recalls_get_details(recall_id=...)
        → Affected products, DINs, corrective actions

Step 3: drug_search(brand_name="...") + drug_get_therapeutic_class(drug_code=...)
        → Full pharmaceutical profile and ATC classification

Step 4: drug_search(company="...") + drug_get_status(drug_code=...)
        → Every product by the same company — how many are CANCELLED/DORMANT?
```

**The insight:** A single recall becomes a company-wide audit. The Drug Product Database reveals the manufacturer's full portfolio and market status history. Cross-referencing ATC therapeutic class with recall frequency reveals which drug categories have the worst safety records — and which companies are repeat offenders.

---

### 11. Wildfire Smoke Season — The Health Product Cascade

> "During a wildfire smoke emergency, what happens to air quality, respiratory drug supply, and counterfeit health products?"

**APIs:** Weather/AQHI + Drug Product Database + Recalls

```
Step 1: wx_get_aqhi(lat=53.54, lon=-113.49)
        → Edmonton AQHI (10+ during major smoke events)

Step 2: drug_search(brand_name="salbutamol")
        → Check respiratory drug availability and market status

Step 3: drug_get_status(drug_code=...)
        → Is the leading inhaler MARKETED or supply-constrained?

Step 4: recalls_get_health_products(keyword="respirator mask N95")
        → Unauthorized PPE that floods the market during smoke emergencies
```

**The insight:** AQHI reaches 10+ → demand for respirators spikes → counterfeit N95s enter the market → Health Canada issues recall alerts. The AQHI tool gives you the trigger event; the drug database shows whether the legitimate supply chain can respond; the recall API shows the market failures that follow. Three APIs reveal a repeatable failure mode in Canada's emergency health product supply chain.

---

## Food & Nutrition

### 12. The Food Recall Nutrient Shadow

> "Spinach was just recalled for E. coli. What do Canadians lose nutritionally, and what's the best substitute?"

**APIs:** Recalls + Canadian Nutrient File

```
Step 1: recalls_get_food(keyword="spinach")
        → Active spinach recalls

Step 2: nutrient_search_foods(query="spinach raw")
        → Get food_id for recalled item

Step 3: nutrient_search_foods(query="kale raw")
        + nutrient_search_foods(query="arugula raw")
        + nutrient_search_foods(query="swiss chard raw")
        → Find substitutes in the same food group

Step 4: nutrient_compare_foods(
          food_ids=[spinach_id, kale_id, arugula_id, chard_id],
          format="by_nutrient")
        → Side-by-side on iron, folate, vitamin K, vitamin C per 100g

Step 5: nutrient_get_serving_sizes(food_id=...)
        → Convert to real serving sizes
```

**The insight:** A "safe swap" card: spinach is recalled — kale has 2x the vitamin C, comparable iron, and 90% of the folate. Swiss chard matches on vitamin K. This bridges Health Canada's recall system and nutritional database for the first time — immediately useful for dietitians, parents, and public health communications.

---

### 13. The Nutritional Poverty Trap

> "Build the cheapest possible diet that meets Health Canada's recommended daily values. Now inflation-adjust it."

**APIs:** Canadian Nutrient File + Bank of Canada + CKAN

```
Step 1: nutrient_search_foods(query="dried lentils")
        + nutrient_search_foods(query="eggs")
        + nutrient_search_foods(query="oats")
        + nutrient_search_foods(query="frozen broccoli")
        → 20 affordable staple foods

Step 2: nutrient_compare_foods(food_ids=[...], format="by_nutrient")
        → Build a minimum nutritional basket meeting daily protein,
          fibre, iron, vitamin C requirements

Step 3: boc_get_inflation_data(indicator="total",
          start_date="2019-01-01", end_date="2024-12-31")
        → Apply food CPI inflation to the basket year-by-year

Step 4: ckan_search_datasets(query="low income measure food bank usage")
        → Statistics Canada poverty threshold data
```

**The insight:** In 2019, a household at the low income threshold could afford the minimum nutritional basket. By 2024, even spending the entire food budget on the cheapest nutritionally adequate foods leaves the basket ~15-20% short. This turns the abstract "cost of living crisis" into a mathematical proof using government data.

---

### 14. Inflation vs. Recall Rates — Food Safety on a Budget

> "As food prices spiked, did consumers shift to foods with higher recall rates?"

**APIs:** Bank of Canada + Recalls + Canadian Nutrient File + CKAN

```
Step 1: boc_get_inflation_data(indicator="total", start_date="2019-01-01")
        → CPI food component timeline showing the 11.4% peak

Step 2: recalls_get_food(limit=200)
        → Historical food recalls — extract dates and categories

Step 3: nutrient_list_food_groups()
        → Map recalled foods to nutritional categories

Step 4: ckan_search_datasets(query="CFIA food inspection results")
        → CFIA inspection intensity data
```

**The insight:** In the 12 months when grocery inflation peaked at 11.4%, recalls of processed and canned meat products increased 34% — yet CFIA inspection data shows a 12% reduction in scheduled plant visits. Canadians who had no choice but to buy cheaper cuts faced higher risk and less oversight simultaneously.

---

## Developer Patterns

### 15. Morning Economic Brief — 5 APIs in One Batch

> "Give me a Canadian economic briefing: USD/CAD, EUR/CAD, policy rate, year-over-year CPI, and energy commodity prices."

```
discover_tools("exchange rate inflation policy rate commodities")
→ finds all relevant Bank of Canada tools

execute_batch([
  {name: "boc_get_exchange_rates",   arguments: {currency: "USD", recent: 1}},
  {name: "boc_get_exchange_rates",   arguments: {currency: "EUR", recent: 1}},
  {name: "boc_get_interest_rates",   arguments: {rate_type: "policy", recent: 1}},
  {name: "boc_get_inflation_data",   arguments: {recent: 2}},
  {name: "boc_get_commodity_prices", arguments: {commodity_type: "energy", recent: 1}}
])
→ 5 API calls fire simultaneously, results synthesized by the agent
```

**Why this matters:** Without MCP: 5 HTTP clients, 5 parsers, 5 retry policies, manual asyncio.gather. With mcp-canada: 2 tool calls after discovery. The agent synthesizes what no API returns: "CAD weakening against USD while BoC holds. Energy commodities up — historically precedes rate pressure."

---

### 16. Is Today Unusually Hot? — Real-Time vs. Historical Fusion

> "It's 34C in Ottawa. How does that compare to the 30-year normal, the all-time record, and the decade trend?"

```
wx_search_stations(province="ON", name="Ottawa")
→ station_id: "6106000"

execute_batch([
  {name: "wx_get_climate_normals",      arguments: {station_id: "6106000"}},
  {name: "wx_get_historical_extremes",  arguments: {station_id: "6106000"}},
  {name: "wx_get_climate_trends",       arguments: {station_id: "6106000",
                                          measurement_type: "temperature"}},
  {name: "wx_get_climate_daily",        arguments: {station_id: "6106000",
                                          start_date: "2016-04-01",
                                          end_date: "2026-04-07"}}
])
→ Four data dimensions in one batch: normals, extremes, trends, daily
```

**Agent synthesis:** "34C is 22.8C above the April normal of 11.2C, 2.7C below the all-time April record of 36.7C (1918), and consistent with the +1.8C/decade warming trend at this station."

---

### 17. The Pharmacovigilance Cross-Reference

> "Check if Metformin has any recalls, get its full drug profile, and flag food recalls relevant to diabetic diets."

```
drug_search(brand_name="Metformin")
→ drug_code: 12345

execute_batch([
  {name: "drug_get_details",            arguments: {drug_code: 12345}},
  {name: "drug_get_ingredients",        arguments: {drug_code: 12345}},
  {name: "drug_get_schedule",           arguments: {drug_code: 12345}},
  {name: "drug_get_therapeutic_class",  arguments: {drug_code: 12345}},
  {name: "recalls_get_health_products", arguments: {keyword: "metformin"}},
  {name: "recalls_get_food",            arguments: {keyword: "sugar glucose"}}
])
→ 6 calls: 4 from Drug DB + 2 from Recalls — cross-module in one batch
```

**Why this matters:** Two completely separate government APIs (Health Canada DPD + Recalls) joined in one `execute_batch`. The `drug_code` flows from the first call into the batch — dynamic chaining that would require a custom pipeline without MCP.

---

### 18. Bilingual Query — Requete en Francais

> "Donne-moi les alertes meteo actives au Quebec, les conditions actuelles a Montreal, et les previsions."

```
execute_batch([
  {name: "wx_get_weather_alerts",      arguments: {province: "QC", lang: "fr"}},
  {name: "wx_get_current_conditions",  arguments: {location: "Montreal", lang: "fr"}},
  {name: "wx_get_forecast",            arguments: {location: "Montreal", days: 3, lang: "fr"}}
])
→ All responses return French labels, error messages, and source attribution
```

**Why this matters:** `lang: "fr"` is a first-class parameter on every tool — not an afterthought. Canada has two official languages. Run the exact same payload with `lang: "en"` then `lang: "fr"` — identical structure, content switches languages. Bilingual apps get language parity for free.

---

### 19. MP Dossier Builder — 10 Calls, One Conversation

> "Build a complete dossier on the PM's first 30 days: bills, votes, debates, and compare against NDP voting patterns."

```
plan_query("MP activity: bills, votes, debates, party comparison")
→ Suggests 3-wave execution plan with parallelism map

Wave 1:  parl_get_politicians(name="...")
       + parl_search_bills(session="45-1", status="introduced")

Wave 2:  parl_get_voting_record(politician="...", session="45-1")
       + parl_get_debates(politician="...")

Wave 3:  parl_get_party_members(party="NDP")
       + parl_get_votes(session="45-1", result="Passed")

→ 7 API calls in 3 waves, parallelized within each wave
```

**Why this matters:** `plan_query` returns a dependency graph — which calls can run in parallel and which must wait. Without this server, OpenParliament.ca requires manual URL construction, pagination, and response normalization across 4+ endpoint patterns.

---

## Key Patterns

Three structural patterns make these examples work:

**The Accountability Loop** (examples 1, 2, 3, 4, 9): Government produces data, something happens, Parliament is supposed to respond. The MCP server lets you compare economic reality against the legislative record.

**The Causal Chain** (examples 5, 6, 7, 8): Physical event (drought, wildfire, flood) → economic signal (commodity index) → policy response (or silence). No single API contains more than one link.

**The Safety Cross-Check** (examples 10, 11, 12, 14): A product is recalled or at risk → what's the full pharmaceutical or nutritional profile? → who else is affected? Cross-referencing safety alerts with drug and nutrition databases produces actionable intelligence.

---

## Getting Started

```bash
# Install and run
uvx mcp-canada

# Or load specific modules
uvx mcp-canada --modules bank_of_canada,open_parliament,recalls

# 86 tools. 7 APIs. Zero auth tokens. One command.
```

Add to Claude Desktop, Claude Code, or any MCP-compatible agent — then try any prompt above.
