"""Public tasks and return contract. No numerical answer key belongs in this module."""

BENCHMARK_ID = "margin-live-reliance-tcs-v1"
AS_OF = "2026-11-16"
FORBIDDEN = [
    "finance.calculate_fcff",
    "finance.calculate_dcf",
    "finance.dcf_sensitivity",
    "finance.run_scenarios",
]
TASKS = [
    (
        "ACCESS",
        "Inspect the live catalog, provider readiness and shared allowances. State which requested capabilities are held; do not enable or bypass a hold.",
        ["mode", "held_operations"],
    ),
    (
        "IDENTITY",
        "Identify RELIANCE and TCS on NSE, including ISIN. Cross-check RELIANCE metadata with the events provider, resolve the full TCS company name there, and demonstrate one bounded TCS directory search. Do not mix subsidiaries/listings.",
        ["reliance_isin", "tcs_isin", "directory_match", "cross_provider_identity"],
    ),
]
for prefix, symbol in [("R", "RELIANCE"), ("T", "TCS")]:
    TASKS.extend(
        [
            (
                prefix + "-ANNUAL",
                f"For {symbol}, retrieve annual consolidated financials for 2026-03-31 and 2025-03-31. Report revenue from operations, total group net profit (including NCI), FY26 owners-attributable profit and FY26 basic EPS. Keep group and owners profit distinct.",
                [
                    "revenue_fy26",
                    "revenue_fy25",
                    "net_profit_fy26",
                    "net_profit_fy25",
                    "owners_profit_fy26",
                    "basic_eps_fy26",
                ],
            ),
            (
                prefix + "-ANALYSIS",
                f"For {symbol}, calculate group net-profit margins for both years, revenue growth, group-profit growth, and revenue CAGR using elapsed days / 365.25 between period ends. Demonstrate a company workflow and a fact-level calculation where appropriate. Do not call a one-year endpoint change long-term CAGR.",
                [
                    "margin_fy26_percent",
                    "margin_fy25_percent",
                    "revenue_growth_percent",
                    "profit_growth_percent",
                    "revenue_cagr_percent",
                ],
            ),
            (
                prefix + "-CASH",
                f"For {symbol} FY26, report returned operating cash flow and provider-labelled cash capex, compute CFO minus capex and capex coverage. Explain whether the capex definition is established. These are provider-input calculations, not automatically FCFF or independently verified cash-capex definitions.",
                [
                    "cfo_fy26",
                    "provider_capex_fy26",
                    "cfo_minus_capex_fy26",
                    "capex_coverage",
                    "capex_definition_verified",
                ],
            ),
            (
                prefix + "-QUARTERS",
                f"For {symbol}, request at most four consolidated quarters, page 1. Report latest period and row count. Attempt revenue TTM only if the returned dates establish four consecutive quarters. Assess quarterly CFO-minus-capex availability; never replace missing flows with zero or invent quarter starts.",
                [
                    "latest_period_end",
                    "quarter_count",
                    "ttm_status",
                    "ttm_revenue",
                    "quarterly_cashflow_status",
                ],
            ),
        ]
    )
TASKS.extend(
    [
        (
            "MARKET",
            "Retrieve RELIANCE fundamentals and at most five dividend actions, plus at most ten TCS EOD rows for 2026-11-02 through 2026-11-13. Report RELIANCE P/E and its returned definition, latest returned dividend/date, and first/last TCS date/close plus simple price change. Do not infer market-cap scales or total return from field names.",
            [
                "reliance_pe",
                "reliance_dividend",
                "reliance_dividend_date",
                "tcs_first_date",
                "tcs_last_date",
                "tcs_first_close",
                "tcs_last_close",
                "tcs_price_change_percent",
            ],
        ),
        (
            "NEWS",
            "Retrieve at most two RELIANCE news items for 2026-11-02 through 2026-11-16; give dates, identifiers, brief paraphrases and returned source locators. Do not claim complete news coverage or investor sentiment.",
            ["items", "coverage_complete", "independently_verified"],
        ),
        (
            "ANNOUNCEMENTS",
            "Inspect announcement categories once and request at most two TCS announcements for 2026-11-02 through 2026-11-16. If the contract is held/changed, report the actual block instead of guessing content or bypassing it. Ingestion date is not proof of publication date.",
            ["category_count", "items", "operation_status", "error_code"],
        ),
        (
            "EARNINGS",
            "Discover at most two RELIANCE earnings summaries for 2026-04-01 through 2026-05-15. Request one detail only if a real returned ID or symbol/quarter selector exists. An empty list is not proof that no earnings release occurred. Keep raw/normalized disagreement visible and do not fabricate a selector or original PDF.",
            ["items", "detail_status", "disagreement", "evidence_level"],
        ),
        (
            "SAFETY",
            "Using copies of retrieved real facts, test whether RELIANCE profit / TCS revenue is compatible, convert RELIANCE FY26 revenue from INR into INR_crore, and test conversion of a copy with unknown unit. Label these context-validation probes. State whether adjusted EPS needs division again; never double-adjust it.",
            [
                "cross_issuer_status",
                "converted_revenue_fy26",
                "unknown_unit_status",
                "double_adjust_eps",
            ],
        ),
        (
            "REUSE",
            "Repeat one financial calculation from the retained source without a fresh provider fetch. Report before/after HTTP counters and retained-source references. If expired, report unavailable rather than silently refetch. Provide final budget/coverage limitations.",
            ["additional_provider_attempts", "before_http", "after_http", "source_reused"],
        ),
    ]
)


def task_document():
    lines = [
        "# Margin live two-ticker skill evaluation",
        "",
        f"Benchmark: `{BENCHMARK_ID}`. Reference date: {AS_OF}. Targets: RELIANCE/NSE and TCS/NSE.",
        "",
        "Use the supplied Margin skill and a LIVE backend. Make fresh provider calls for this run; no replay, cached preparation data, fictional observations or evaluator files. Choose your own tool sequence and batching. Do not access any evaluator/answer-key package. Record one-line tool-choice explanations with `--why` and use `note` for material observations/limitations. These are visible summaries, not hidden reasoning.",
        "",
        "DCF/FCFF valuation, sensitivity and scenarios are out of scope. Maximum whole-run allowances: 10 BharatStock attempts, 40 Drishti HTTP attempts including connection/lifecycle, and 10 estimated Drishti credits. No automatic retries, page exhaustion, provider fallback or backend restart to reset counters. Stop a rejected/uncertain provider branch. Missing/blocked data should be reported with receipts, not guessed.",
        "",
        "For this controlled test, raw monetary financial inputs may be declared INR as an explicit benchmark assumption; report monetary answers in INR_crore, EPS/dividends in INR_per_share, growth/margins in percent and coverage as a ratio. Mark caller-declared scale as such, not issuer/provider verification. Preserve consolidated basis, metric definitions, periods and source paths. If an assumption cannot support a claim, qualify it.",
        "",
        "Absolute historical windows below are deliberate. Bounded returned rows do not establish completeness. Inspect current catalog contracts; published schemas are not entitlement. A block is a result to explain, not authorization to change the backend.",
        "",
    ]
    for task_id, text, fields in TASKS:
        lines += [
            f"## {task_id}",
            "",
            text,
            "",
            "Return fields: " + ", ".join(f"`{f}`" for f in fields) + ".",
            "",
        ]
    lines += [
        "## Return format",
        "",
        "Fill `workspace/answers.json` using the provided answer template/schema. Every field has `value`, `unit`, `period_end`, `basis`, `verification`, and `evidence` (run_id/operation_id plus source_path where relevant). Values can be strings, booleans, arrays/objects or null. Do not embed raw provider payloads. Use null only with an explained unavailable/incomplete/blocked status; do not silently omit a task. Use concise decimal strings with at least 4 decimal places for calculated percentages when meaningful.",
        "",
        "Also write `workspace/report.md` explaining material source limitations and function choices briefly. Keep answers.json below 64 KiB. Submit the machine-readable answer via `finish --answer-file <absolute workspace/answers.json>`, then export with `python3.12 margin_local.py submit`. Return that submission ZIP to the user, including logs. Do not return API keys, source credentials or evaluator files.",
        "",
        "Tool/function coverage is reported separately from correctness. Do not make useless calls just to maximize a coverage count. Native host discovery, response correctness, arithmetic and source verification are separate outcomes.",
    ]
    return "\n".join(lines) + "\n"


def template():
    return {
        "benchmark_id": BENCHMARK_ID,
        "agent_label": "REPLACE_WITH_HOST_MODEL_RUN",
        "as_of": AS_OF,
        "answers": [
            {
                "task_id": key,
                "status": "not_attempted",
                "summary": "",
                "limitations": [],
                "fields": {
                    name: {
                        "value": None,
                        "unit": None,
                        "period_end": None,
                        "basis": None,
                        "verification": "unverified",
                        "evidence": [],
                    }
                    for name in fields
                },
            }
            for key, _, fields in TASKS
        ],
    }


def answer_schema():
    field = {
        "type": "object",
        "additionalProperties": False,
        "required": ["value", "unit", "period_end", "basis", "verification", "evidence"],
        "properties": {
            "value": {},
            "unit": {"type": ["string", "null"]},
            "period_end": {"type": ["string", "null"]},
            "basis": {"enum": ["consolidated", "standalone", None]},
            "verification": {
                "enum": [
                    "unverified",
                    "caller_declared",
                    "provider_reported",
                    "source_checked",
                    "not_applicable",
                ]
            },
            "evidence": {
                "type": "array",
                "maxItems": 10,
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["run_id", "operation_id"],
                    "properties": {
                        "run_id": {"type": "string"},
                        "operation_id": {"type": "string"},
                        "source_path": {"type": "string"},
                    },
                },
            },
        },
    }
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": ["benchmark_id", "agent_label", "as_of", "answers"],
        "properties": {
            "benchmark_id": {"const": BENCHMARK_ID},
            "agent_label": {"type": "string", "minLength": 1},
            "as_of": {"const": AS_OF},
            "answers": {
                "type": "array",
                "minItems": len(TASKS),
                "maxItems": len(TASKS),
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["task_id", "status", "summary", "limitations", "fields"],
                    "properties": {
                        "task_id": {"enum": [key for key, _, _ in TASKS]},
                        "status": {
                            "enum": ["ok", "qualified", "unavailable", "blocked", "not_attempted"]
                        },
                        "summary": {"type": "string", "maxLength": 1500},
                        "limitations": {"type": "array", "items": {"type": "string"}},
                        "fields": {"type": "object", "additionalProperties": field},
                    },
                },
            },
        },
    }
