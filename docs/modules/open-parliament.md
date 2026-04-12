# :classical_building: Open Parliament

Bills, MPs, votes, ballots, and Hansard debates from the [Open Parliament API](https://api.openparliament.ca/).

All tools accept `lang: "en" | "fr"` for bilingual support.

## Tools (10)

<!-- CATALOG:open-parliament:start -->
| Tool | Description | Key Parameters |
|------|-------------|----------------|
| `parl_search_bills` | List Canadian federal bills filtered by session or status. | `keyword`, `session`, `status`, `page` |
| `parl_get_bill_details` | Get full details for a specific Canadian federal bill including sponsor and status history. | `bill_id` |
| `parl_get_politicians` | Search or list Canadian Members of Parliament by name, party, or province. | `name`, `party`, `province`, `page` |
| `parl_search_by_riding` | Find the MP or politician for a specific electoral riding in Canada. | `riding` |
| `parl_get_party_members` | Get the current Members of Parliament for a specific political party. | `party` |
| `parl_get_votes` | Get House of Commons vote records, optionally filtered by session, bill, or result. | `session`, `bill`, `result`, `page` |
| `parl_get_voting_record` | Get votes an MP participated in, with house-wide totals per division. | `politician`, `session`, `page` |
| `parl_get_debates` | Get Hansard debate transcripts from the House of Commons. | `date`, `politician`, `page` |
| `parl_search_hansard` | Full-text search of Canadian Hansard debate transcripts. | `query`, `page` |
| `parl_get_ballots` | Get individual MP yea/nay ballots for a specific House of Commons vote. | `vote_id`, `politician`, `page` |
<!-- CATALOG:open-parliament:end -->

### Example

```
call_tool("parl_get_ballots", {"vote_id": "44-1/333", "politician": "anna-roberts"})
```

> **Note:** `parl_get_voting_record` returns house-wide totals, NOT individual MP votes. Use `parl_get_ballots` for how a specific MP voted on a specific division.

## Prompts (5)

| Prompt | Type | Description |
|--------|------|-------------|
| `parl_research_bill` | Guided | Research a federal bill -- search -> details -> sponsor -> votes |
| `parl_find_mp` | Quick | Look up an MP's profile and riding |
| `parl_track_voting` | Guided | Track how an MP votes on bills |
| `parl_search_debates` | Quick | Search Hansard debate transcripts |
| `parl_party_breakdown` | Guided | Get all MPs from a political party |

## Resources (7)

| URI | Type | Description |
|-----|------|-------------|
| `data://parliament/party-codes` | Catalog | Political party codes and bilingual names |
| `data://parliament/session-format` | Catalog | Session ID format and recent sessions |
| `data://parliament/bill-types` | Catalog | Bill type codes (C-, S-, M-) with descriptions |
| `docs://parliament/voting-guide` | Guide | How divisions work, yea/nay/paired, how to look up ballots |
| `docs://parliament/hansard-guide` | Guide | Hansard transcript structure and full-text search tips |
| `docs://parliament/api-quirks` | Guide | Pagination, URL slug format, URL-based IDs |
| `template://parliament/mp-profile` | Template | MP profile with `{name}`, `{party}`, `{riding}`, `{votes}` |
