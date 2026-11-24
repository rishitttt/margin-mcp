"""Explicit two-request HUL finance acceptance; private outputs, no forecasts or retries."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from collections import Counter
from decimal import Decimal, localcontext
from pathlib import Path

from margin.analysis.company import FUNCTIONS, calculate_company
from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.agent.local_config import read_provider_env


async def check(output, saved=None):
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    keys = read_provider_env(Path(__file__).resolve().parents[1] / ".env") if saved is None else {}
    service = ResearchService(
        Settings(
            mode="live" if saved is None else "synthetic",
            bharatstock_key=keys.get("BHARATSTOCK_API_KEY", ""),
            enabled_unverified=frozenset({"bharatstock.get_financials"}),
            bharatstock_requests=2 if saved is None else 0,
            drishti_requests=0,
            drishti_credits=0,
            max_payload_runs=40,
            max_buffer_bytes=40 * 1024 * 1024,
        )
    )
    observations, arithmetic = [], []

    def save(name, data):
        clean = service.sanitizer.clean(data)
        fd = os.open(output / name, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as stream:
            json.dump(clean, stream, indent=2)

    def crosscheck(label, actual, expected):
        with localcontext() as ctx:
            ctx.prec = 50
            match = abs(Decimal(str(actual)) - Decimal(str(expected))) <= Decimal("1e-20")
        arithmetic.append(
            {"check": label, "actual": str(actual), "expected": str(expected), "match": match}
        )
        if not match:
            raise ValueError("Independent arithmetic mismatch; inspect private evidence.")

    def verify(payload):
        if payload["status"] not in {"success", "partial"} or not isinstance(
            payload.get("inputs"), list
        ):
            return
        fields = {
            f["metric"]: Decimal(str(f["value"]))
            for f in payload["inputs"]
            if f.get("value") is not None
        }
        values = payload.get("values", {})
        formulas = {
            "working_capital": lambda: fields["current_assets"] - fields["current_liabilities"],
            "current_ratio": lambda: fields["current_assets"] / fields["current_liabilities"],
            "current_assets_less_inventory_ratio": lambda: (
                (fields["current_assets"] - fields["inventories"]) / fields["current_liabilities"]
            ),
            "cash_ratio": lambda: (
                fields["cash_and_cash_equivalents"] / fields["current_liabilities"]
            ),
            "gross_borrowings": lambda: (
                fields["borrowings_current"] + fields["borrowings_non_current"]
            ),
            "net_borrowings": lambda: (
                fields["borrowings_current"]
                + fields["borrowings_non_current"]
                - fields["cash_and_cash_equivalents"]
            ),
            "borrowings_to_total_equity": lambda: (
                (fields["borrowings_current"] + fields["borrowings_non_current"])
                / fields["total_equity"]
            ),
            "liabilities_to_assets": lambda: fields["total_liabilities"] / fields["total_assets"],
            "cfo_margin_percent": lambda: fields["cash_flow_operating"] / fields["revenue"] * 100,
            "cfo_to_group_profit": lambda: fields["cash_flow_operating"] / fields["net_profit"],
            "capex_to_revenue_percent": lambda: fields["capex"] / fields["revenue"] * 100,
            "cfo_less_capex_margin_percent": lambda: (
                (fields["cash_flow_operating"] - fields["capex"]) / fields["revenue"] * 100
            ),
            "cfo_minus_capex": lambda: fields["cash_flow_operating"] - fields["capex"],
            "capex_coverage": lambda: fields["cash_flow_operating"] / fields["capex"],
            "margin_percent": lambda: (
                fields.get("profit_from_continuing_operations", fields.get("net_profit"))
                / fields["revenue"]
                * 100
            ),
        }
        for metric in (
            "net_profit",
            "profit_from_continuing_operations",
            "net_profit_attributable_to_owners",
            "operating_profit",
            "ebitda",
        ):
            formulas[metric + "_margin_percent"] = lambda m=metric: (
                fields[m] / fields["revenue"] * 100
            )
        with localcontext() as ctx:
            ctx.prec = 50
            for name, fn in formulas.items():
                if name in values and values[name] is not None:
                    crosscheck(payload["function"] + ":" + name, values[name], fn())
            if "total" in values:
                crosscheck(
                    "TTM sum",
                    values["total"],
                    sum(Decimal(str(f["value"])) for f in payload["inputs"]),
                )

    async def run(plan, label):
        save(label + "-plan.json", plan)
        started = await service.start_run(plan["plan_id"], label)
        await service._tasks[started["run_id"]]
        state = service.get_run(started["run_id"])
        results = [
            service.get_result(state["run_id"], op["operation_id"]) for op in state["operations"]
        ]
        for result in results:
            save(label + "-" + result["operation"].replace(".", "-") + ".json", result)
            if result["provider"] == "bharatstock" and result["status"] not in {"success", "empty"}:
                raise RuntimeError("Provider branch stopped; no retry.")
        final = results[-1]
        observations.append(
            {
                "function": final["operation"],
                "period_type": plan["operations"][-1]["arguments"]["period_type"],
                "status": final["status"],
                "error": final["error"],
                "result_file": label + "-" + final["operation"].replace(".", "-") + ".json",
            }
        )
        if isinstance(final.get("payload"), dict):
            verify(final["payload"])
        return final

    try:
        for period in ("annual", "quarterly"):
            names = [
                n
                for n in FUNCTIONS
                if not (n.endswith("_ttm") and period != "quarterly")
                and not (n.endswith("_cagr") and period != "annual")
            ]
            for index, name in enumerate(names):
                if saved is not None:
                    source_file = saved / (
                        period + "-finance-company_data_readiness-bharatstock-get_financials.json"
                    )
                    source = json.loads(source_file.read_text())
                    arguments = {
                        "ticker": "HINDUNILVR",
                        "exchange": "NSE",
                        "period_type": period,
                        "basis": "consolidated",
                        "money_unit": "auto",
                        "metric": "revenue",
                        "source_operation_id": source["operation_id"],
                        "source_run_id": "archived-live-source",
                    }
                    payload = calculate_company(name, arguments, source)
                    filename = period + "-" + name.replace(".", "-") + ".json"
                    save(
                        filename,
                        {
                            "operation": name,
                            "status": payload["status"],
                            "payload": payload,
                            "source_file": str(source_file),
                            "mode": "reprocessed_saved_real_response",
                            "additional_http_attempts": 0,
                        },
                    )
                    observations.append(
                        {
                            "function": name,
                            "period_type": period,
                            "status": payload["status"],
                            "result_file": filename,
                        }
                    )
                    verify(payload)
                    continue
                plan = service.plan_financial(
                    name,
                    "HINDUNILVR",
                    "NSE",
                    period_type=period,
                    money_unit="auto",
                    fetch_missing=index == 0,
                )
                await run(plan, period + "-" + name.replace(".", "-"))
        save(
            "arithmetic-checks.json",
            {
                "scope": "Returned-input arithmetic only; no full financial source verification",
                "checks": arithmetic,
            },
        )
    finally:
        await service.close()
        save(
            "summary.json",
            {
                "ticker": "HINDUNILVR",
                "mode": "fresh_live" if saved is None else "reprocessed_saved_real_response",
                "outcomes": observations,
                "counts": dict(Counter(o["status"] for o in observations)),
                "arithmetic_checks": len(arithmetic),
                "ledger": service.ledger.snapshot(),
                "original_documents_independently_verified": False,
            },
        )
        save(
            "manifest.json",
            {
                "sha256": {
                    p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in output.iterdir()
                    if p.is_file()
                }
            },
        )
    print(
        json.dumps(
            {
                "outcome_counts": dict(Counter(o["status"] for o in observations)),
                "arithmetic_checks": len(arithmetic),
                "http_attempts": service.ledger.requests,
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-live", action="store_true")
    parser.add_argument(
        "--saved-responses",
        type=Path,
        help="Reprocess an earlier private run; no external requests",
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1] / "reports/private"
    if not args.output.resolve().is_relative_to(root):
        parser.error("Choose an ignored reports/private directory.")
    if not args.confirm_live and args.saved_responses is None:
        parser.error("Live calls require --confirm-live; alternatively supply --saved-responses.")
    if args.confirm_live and args.saved_responses is not None:
        parser.error("Choose live calls or saved-response processing, not both.")
    asyncio.run(check(args.output, args.saved_responses))
