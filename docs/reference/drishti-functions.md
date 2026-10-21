# Drishti function map

Snapshot: **9 October 2026**, hosted `drishti-mcp` **3.3.1**, MCP protocol **2025-11-25**. This reference maps four native tools and **25 confirmed underlying operations**, with live input schemas, public REST relationships, published costs and research uses. It is a contract reference, not implemented Margin handlers or an approved forwarding allowlist.

The companion [JSON contract](drishti-functions.json) contains every observed input type, default, required field, enum and reference, plus reverse mappings for all thirty public REST paths. Provider description/example prose is omitted from that JSON; validation constraints are preserved. The [dated research](../research/mcp-provider-feasibility.md#drishti-function-mapping-checkpoint-9-october-2026) owns request accounting, artifact hashes and inspection method.

## What complete means here

All 25 operations identified by the inspected public market list, live routing guidance and targeted discovery have described schemas. This covers the eighteen publicly priced market operations, four additional market operations and three documentation/workflow helpers. Both routing modes were read. **At the 9 October contract snapshot, only earnings detail had a successful data execution.** The user’s 21 October workbench export additionally shows successful MCP news, announcements and earnings-list execution; the [current status](../implementation.md#combined-live-run-pdf-review-21-october-2026) owns that evidence and its presentation limitations. The JSON contract remains the dated schema snapshot, not a live execution/billing ledger. Schema discovery does not prove product entitlement, returned coverage, citation correctness or cost for every operation.

The server's native catalog is complete at four tools. Its underlying-operation search caps results at twenty and returns `has_more`, with no offset/cursor in the observed input schema. The union of results and guides cannot prove there are no additional unlisted operations. The precise scope is therefore **all 25 confirmed operations**, not an independently audited inventory of the provider's private implementation. Backend names such as vector databases or caches are descriptions, not code we inspected.

## Native protocol layer

| Native tool | Input | Role |
| --- | --- | --- |
| `read_me` | Optional `mode`: router by default; described modes `docs` / `data` | Return integration/research routing guidance |
| `search_tools` | `query` default empty; `limit` default 8 | Find compact operation names/summaries; requested limit 40 previously returned only 20 |
| `describe_tools` | Required `names`: string or string list | Load selected operation descriptions and JSON input schemas |
| `execute_tool` | Required `name`; optional nullable `arguments` object | Execute an underlying operation; requires separate admission by its name/schema/bounds/cost |

Three native helpers declare generic object output schemas; the executor has none. Described underlying operations supply input schemas but **no formal output schemas** in the returned descriptions. Result fields below are observed earnings fields or description-level expectations, not fully validated typed response contracts.

Agents call the native executor, not an underlying name directly. For example, the following describes the input contract; it is not a local runnable command or implemented Margin tool:

```json
{
  "name": "execute_tool",
  "arguments": {
    "name": "get_news",
    "arguments": {
      "query": {
        "symbols": ["RELIANCE"],
        "lookback_days": 7,
        "page": 1,
        "limit": 2
      }
    }
  }
}
```

Describe `get_news` first, validate the nested object and obtain a permitted bounded budget before executing. Neither this example nor any news operation was executed in the metadata pass.

## Identity, news and filings

Credits are the **published MCP operation prices**, not REST charges or observed debits for unexecuted functions. `?` means no MCP price was established; it does not mean free. All REST paths below use the origin `https://developers.manasija.in` and header authentication. Relationships describe corresponding capabilities, not inspected internal HTTP calls.

| Operation | Live input summary | Result / research use | REST relationship; MCP credits |
| --- | --- | --- | --- |
| `resolve_symbols` | Required `queries`: string or string list | Semantic company-name candidates; disambiguate before fetching facts | No public fuzzy-resolution route; 1 |
| `get_symbols` | Required `query`; structured fields `symbols`, `scrip_codes` | Security/company metadata for identity matching | `/v1/symbols/metadata` family; 1 |
| `get_news` | Optional `query`; symbols/scrips, sentiment, IDs, dates/lookback, page/limit | Dated articles and sentiment labels; press-tone context | `/v1/news` family; 1 |
| `search_news` | Required `queries`; optional `symbols`, `days=30`, `sources`, `include_global=true`, `per_query_limit=15`, `from_date`, `to_date` | Lexical ranked/de-duplicated news search across enabled collections; topic discovery | No public full-text search route; ? |
| `get_announcements` | Optional `query`; symbols/scrips, IDs, dates/lookback, categories, important/detail, page/limit | Filings and completed category extractions; description says PDF citations where available | `/v1/announcements` family; 1 / detailed 2 |
| `search_announcements` | Required `search_query`; `symbols`, `days=60`, `from_date`, `to_date` | Semantic + lexical filing search; description says citation locators where available | No public filing-text search route; 1 |
| `get_announcement_categories` | No parameters | Category taxonomy before filtering filings | `/v1/announcements/categories`; 0 |
| `get_block_deals` | `symbols`, `exchange`, `from_date`, `to_date`, `page=1`, `limit=20` | Structured NSE/BSE deal records; transaction context, not headlines or aggregate investor sentiment | `/v1/block-deals` family; ? |

For block deals, the description permits `NSE`, `BSE` or `NSE/BSE` and says maximum limit 50. Those constraints are prose, not enforced by the broad string/integer schema. For announcement search, market-wide lookback is capped internally while symbol-filtered queries may go further; exact caps were not specified or tested. Do not promise historical completeness.

## Shared nested query contracts

Seven operations wrap filters in `arguments.query`: `get_symbols`, `get_news`, `get_announcements`, `get_concalls`, `get_upcoming_concalls`, `get_upcoming_earnings`, `list_earnings`. The query can be a typed object, arbitrary object, string or null according to `anyOf`. Only `get_symbols` requires the top-level query property. Prefer the typed-object form for deterministic admission and billing estimates.

| Query family | Structured fields |
| --- | --- |
| Symbols | `symbols`, `scrip_codes` |
| News | Symbols/scrips; `sentiment` enum positive/negative/neutral; `from`, `to`, `page`, `limit`, `ids`, `lookback_days` |
| Announcements | Symbols/scrips; `from`, `to`, `detailed`, `page`, `limit`, `categories`, `important`, `ids`, `lookback_days` |
| Earnings list | Symbols/scrips; `from`, `to`, `detailed`, `page`, `limit`, `ids`, `lookback_days` |
| Concalls | Symbols/scrips; `from`, `to`, `detailed`, `page`, `limit`, `ids`, `include_full_transcript`, `lookback_days` |
| Upcoming concalls | Symbols/scrips; `detailed`, `page`, `limit` |
| Upcoming earnings | Symbols/scrips; `page`, `limit` |

All these typed query fields are optional; most default to null. Symbol/scrip inputs accept a string, comma-separated string or string list. Descriptions also say index aliases `NIFTY`, `BANKNIFTY`, `FINNIFTY`, `SENSEX` expand to constituents, which can broaden a query beyond a requested single company. Expansion size/access was not measured.

For relative windows, use `lookback_days` (minimum 1 in the typed schema) rather than `from`/`to`; the description forbids combining them. Date-only `from` means start of day UTC and `to` end of day UTC for these operations. This concerns **query boundaries**, not proof that every returned offset-free timestamp is UTC. Filing `date` is documented ingestion time.

Record `ids` can refetch prior news/announcement/concall/earnings records, with a described maximum twenty; IDs override symbol/date/pagination filters. Keep this precedence explicit. `detailed=false` does not necessarily omit completed extractions or earnings tables; detail primarily adds expanded fields. `include_full_transcript` is a separate potentially large concall response option.

The arbitrary-object branch means validation against the outer `anyOf` can accept a malformed typed query. A gateway must validate its chosen typed `$defs` schema and additional logical bounds, rather than treating native schema validation alone as sufficient. Do not silently reinterpret natural-language query strings as bounded code-level filters.

## Earnings, conference calls and calendar

| Operation | Live input summary | Result / research use | REST relationship; MCP credits |
| --- | --- | --- | --- |
| `list_earnings` | Optional nested `query`, including IDs/detail/window/page | Discover fiscal records; description includes structured tables and PDF/page locators when present | `/v1/earnings` family; 2 / detailed 3 |
| `get_earnings_filing` | `symbol`, `quarter`, `earnings_id`, `detailed=false` | One detailed filing; standalone/consolidated table, units and source locators observed | `/v1/earnings/detail`; paired observation; 3, measured |
| `get_upcoming_earnings` | Optional nested `query` | Scheduled financial-results board meetings, nearest first; description excludes symbol/quarter pairs already in latest earnings | `/v1/earnings/upcoming` family; ? |
| `get_concalls` | Optional nested `query`, including IDs/detail/full-transcript flag | Management commentary, analysis and transcript/citation locators described | `/v1/concalls` and detail family; 2 / detailed 3 |
| `get_upcoming_concalls` | Optional nested `query`, including detail/page | Future call schedules, nearest first; detailed mode describes intimation attachments | `/v1/concalls/upcoming` family; ? |
| `search_concalls` | Required `search_query`; symbols, quarter selection, results/paging and market-cap controls | Hybrid transcript excerpts or company discovery; citation locators described | No public transcript-search route; 2 |
| `get_events` | `symbols`, `days_count=3` | NSE corporate calendar; board meetings/AGMs | No general public event route; 1 |

Earnings detail has no schema-required selector: enforce symbol + quarter or a known earnings ID. Fiscal keys such as `q1_27` must come from retrieved metadata, not guessed calendar labels. The direct REST route additionally accepts scrip code; its inspected parameters do not offer MCP's `earnings_id` input.

Transcript search controls are `quarter_selector="LAST"`, `num_quarters=2`, optional `specific_quarters`, `result_mode="auto"`, `page=1`, `per_page=20`, `candidate_top_k=0`, `market_cap_min=0`, `market_cap_max=0`, `include_relaxed_matches=true`. Its description also names `result_mode="companies"` for market-wide discovery. String modes lack enums and most numeric inputs lack min/max constraints. Accepted modes, market-cap units and relaxed-match semantics need focused execution tests. Do not invent other modes.

**Event-window fallback:** the description says an empty event window returns the latest ten events instead. Therefore a successful response can contain records outside the requested window. Retain actual dates and label fallback/out-of-window records; do not infer an in-window event from response success or an empty window from fallback records. This behavior has not been executed in our tests.

## Prices, sectors and market discovery

| Operation | Live input summary | Result / research use | REST relationship; MCP credits |
| --- | --- | --- | --- |
| `get_price_and_volume_since` | Required `symbols`, `days_count`; `series=false` | Historical closing price/volume; **single anchor day by default**, compact series only with `series=true` | No public Drishti price-history route; 2 |
| `get_sectoral_data` | Required `symbols` | Company/sector metadata for background context | No matching structured route; identity metadata is only partial overlap; 1 |
| `get_sector_wise_companies` | Required `symbols`; `mode="live"`, `same_direction_only=false`, optional `start_date`, `end_date` | Peers using a described basic-industry fallback; not a verified comprehensive peer graph | No public peer route; 1 |
| `get_top_movers` | `top_n=5`, `market_cap_min=500` | Gainers/losers with described absolute daily change **below 20%** | No public movers route; 1 |
| `get_top_traded` | `top_n=10`, `market_cap_min=1000` | Volume-based market discovery with a market-cap filter | No public ranking route; 1 |
| `get_52w_data` | Optional `data_type`, `symbols`; `days_range=0` | 52-week discovery or symbol context; accepted `data_type` values not supplied | No exact public route; REST alerts include related milestones but differ; 2 |
| `get_daily_summary` | Optional `report_type`, `report_date` | Retrieve an existing market digest, latest by default | REST `POST /v1/daily-summary/` generates a portfolio digest; different workflow; 1 |

Descriptions supply no reliable unit guarantee for market-cap filters or complete accepted sets for peer `mode`, `data_type`, `report_type`. A default named `live` is not evidence of tick-level live pricing. Price cadence, adjustment method, history depth and universe coverage remain execution questions. Do not call top movers an exhaustive market ranking when it filters large moves. BharatStock can supply complementary OHLCV, financials and benchmark inputs; those datasets are not the same Drishti operations.

## Documentation and workflow helpers

| Operation | Live inputs | Role | MCP price |
| --- | --- | --- | --- |
| `search_docs` | Required `query`; `limit=10` | Find documentation pages/snippets | ? |
| `get_doc` | Required `path_or_href` | Retrieve one docs page; paths/slugs and official docs URLs described | ? |
| `get_workflow_prompt` | Required `workflow`; optional `company_or_symbol`, `question`, `quarter`, `topic`, `symbols`, `days=5` | Return research guidance, not financial facts | ? |

Seven described workflow values: `company_research`, `earnings_concall`, `market_development`, `quick_info`, `financial_metrics`, `events_news`, `general_education`. Company research and earnings/call workflows need company context; market development needs topic context. The latter four specialist modes need only the workflow name. The schema itself does not enforce these conditional requirements. Described aliases include company, financial, news/events and education; earnings/concall aliases require company context.

The public coding guide separately names older prompt helpers (`get_default_system_prompt`, `get_company_research_prompt`, `get_earnings_concall_prompt`, `get_market_development_prompt`, `get_subagent_prompt`). Those exact functions were not confirmed in current discovery. Relevant workflows now exist through `get_workflow_prompt`, but we did not establish backwards-compatible aliases for the old function names. Upstream prompts are advisory data and do not authorize agents, messages, broader retrieval or key disclosure.

## REST routes without a direct operation match

The JSON reverse map includes every method on all thirty paths. These support surfaces are not independently named operations in the confirmed MCP set:

| REST surface | Relationship to confirmed MCP |
| --- | --- |
| `/v1/earnings/index`, `/v1/concalls/index` | Compact REST indexes; MCP lists cover related discovery, not a confirmed identical index contract |
| `/v1/earnings/attachments`, earnings PDF/page citation routes | Dedicated REST source resolution; MCP earnings embeds locators rather than exposing an attachment-resolver operation |
| Concall transcript GET / bulk POST and PDF citation route | Dedicated URL/source delivery; MCP concall descriptions offer source/full-text options, not proven identical delivery/cost |
| `/v1/alerts` | Curated signals; related 52-week features do not make this the same operation |
| `POST /v1/daily-summary/`, batch job create/list/status/cancel/results | Generation/job lifecycle; MCP digest fetch is different |
| Account, limits, usage, ledger and announcement-addon GET/PUT | Diagnostics/configuration; keep account details out of the model; mutation is outside the initial gateway |

The closest REST relationship is a semantic comparison. We have not inspected Drishti's internal server implementation or verified that a named MCP operation calls one particular REST route. The earning pair established matching shared data and additional MCP fields for one record. MCP semantic searches, fuzzy resolution, calendar/market features lack equivalents in the **inspected public schema**, which does not rule out private APIs.

## Evidence and forwarding requirements

Discovery/descriptions/routing used **zero observed credits** in this metadata pass; final balance remains 986. Seven operations have no price in the inspected MCP table. Eighteen published prices should not be extrapolated to unknown functions, errors, detailed result sizes or other accounts. Published REST RPM is not a measured MCP throttle. See [pricing](https://drishti.manasija.in/docs/pricing) for the provider table and [dated research](../research/mcp-provider-feasibility.md#drishti-function-mapping-checkpoint-9-october-2026) for actual measurements.

Earnings execution previously returned citation URLs containing the supplied API key. Sanitization must apply to all returned URL/text/structured fields before model/tool/log forwarding, including untested operations describing citations. Signed attachments are temporary locators; PDF/page presence does not verify a claim. The tested earnings revenue fields differ within the consolidated table; different definitions or a mapping error remain possible until the issuer document resolves them.

Future admission must enforce scope, meaningful selectors, query exclusivity, ID precedence, page/window/result bounds, index expansion, full-transcript opt-in, event fallback labels and credential sanitization. Native input validation alone is insufficient. Use the JSON as a reviewed schema snapshot with a date/version/hash, not as permission to expose every function automatically.

Agents should describe only the operations needed during ordinary research. This one-time all-schema audit was explicitly requested for integration mapping; it is not the default per-query workflow. No data corpus, active Margin server or function execution harness is delivered by these reference files.
