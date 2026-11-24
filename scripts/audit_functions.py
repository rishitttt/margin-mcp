"""One-ticker bounded live audit with a complete function matrix and private review bundle."""

from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import json
import os
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from margin.analysis.company import planning_capabilities
from margin.analysis.facts import prepare_financial_facts
from margin.analysis.service import capabilities
from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.registry import Registry
from margin.core.service import ResearchService
from margin.evidence.results import data_payload
from margin.interfaces.agent.local_config import read_provider_env

VALUATION = {
    "finance.calculate_fcff",
    "finance.calculate_dcf",
    "finance.dcf_sensitivity",
    "finance.run_scenarios",
}


class Audit:
    def __init__(self, args):
        self.args = args
        self.root = Path(__file__).resolve().parents[1]
        self.output = args.output.expanduser().absolute()
        if self.output.exists() or self.output.with_suffix(".zip").exists():
            raise ValueError("Choose new output/archive paths; existing runs are never overwritten")
        ignored = subprocess.run(
            ["git", "check-ignore", "-q", str(self.output)], cwd=self.root, check=False
        )
        if ignored.returncode:
            raise ValueError(
                "Save licensed responses under the repo's ignored reports/private directory"
            )
        self.output.mkdir(parents=True, mode=0o700)
        (self.output / "cases").mkdir(mode=0o700)
        keys = read_provider_env(self.root / ".env")
        if set(keys) != {"BHARATSTOCK_API_KEY", "DRISHTI_API_KEY"}:
            raise ValueError("Both provider credentials are required in the ignored repo .env")
        self.service = ResearchService(
            Settings(
                mode="live",
                bharatstock_key=keys["BHARATSTOCK_API_KEY"],
                drishti_key=keys["DRISHTI_API_KEY"],
                enabled_unverified=frozenset(Registry(Settings()).specs),
                bharatstock_requests=7,
                drishti_requests=16,
                drishti_credits=10,
                max_payload_runs=30,
                max_buffer_bytes=40 * 1024 * 1024,
            )
        )
        self.matrix = {}
        self.results = []
        self.stopped = {}
        self.count = 0
        self.started = datetime.now(UTC).isoformat()
        self.junit = args.offline_results.resolve()
        xml = ET.parse(self.junit).getroot()
        self.offline = {
            "tests": sum(int(s.get("tests", 0)) for s in xml.iter("testsuite")),
            "failures": sum(
                int(s.get("failures", 0)) + int(s.get("errors", 0)) for s in xml.iter("testsuite")
            ),
            "skipped": sum(int(s.get("skipped", 0)) for s in xml.iter("testsuite")),
        }
        self.testcases = list(xml.iter("testcase"))
        if self.offline["failures"]:
            raise ValueError("Offline failures must be reviewed before live acceptance")
        self.contracts = {
            "retrieval": self.service.registry.capabilities(),
            "local": capabilities(),
            "company": planning_capabilities(),
            "review": self.service.review_capabilities(),
        }
        for category in ("retrieval", "local", "company"):
            for spec in self.contracts[category]:
                name = spec.get("operation", spec.get("function"))
                tests = [
                    c.get("classname", "") + "::" + c.get("name", "")
                    for c in self.testcases
                    if name in c.get("name", "")
                    or category == "company"
                    and "test_all_five_company_wrappers" in c.get("name", "")
                ]
                self.matrix[name] = {
                    "function": name,
                    "category": category,
                    "implemented": True,
                    "offline_status": "passed" if tests else "see_suite_evidence",
                    "offline_tests": tests,
                    "new_ticker_outcome": "not_run",
                    "cases": [],
                    "notes": [],
                }
        self.save("contracts.json", self.contracts)
        self.save(
            "run-plan.json",
            {
                "ticker": args.ticker,
                "company_query": args.company_name,
                "as_of": args.as_of,
                "limits": {
                    "bharatstock_http": 7,
                    "drishti_http_including_lifecycle": 16,
                    "estimated_drishti_credits": 10,
                },
                "clock": "Explicit windows; UTC receipts",
                "started_at": self.started,
                "valuation_policy": "No invented forecasts, WACC, working-capital changes or company valuation inputs",
                "retention_review_date": (
                    date.fromisoformat(args.as_of) + timedelta(days=14)
                ).isoformat(),
                "automatic_deletion": False,
            },
        )

    def save(self, name, value):
        clean = self.service.sanitizer.clean(value)
        descriptor = os.open(self.output / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            json.dump(clean, stream, indent=2, ensure_ascii=False)
            stream.write("\n")

    def record(self, name, case, value):
        self.count += 1
        filename = f"cases/{self.count:02d}-{name.replace('.', '-')}-{case}.json"
        self.save(filename, value)
        status = value.get("status", "not_run")
        entry = {
            "case": case,
            "status": status,
            "file": filename,
            "error": value.get("error"),
            "issues": value["payload"].get("issues", [])
            if isinstance(value.get("payload"), dict)
            else [],
            "http_attempts": value.get("receipt", {}).get("http_attempts", 0),
        }
        self.matrix[name]["cases"].append(entry)
        print(
            json.dumps(
                {
                    "function": name,
                    "case": case,
                    "status": status,
                    "http_attempts": entry["http_attempts"],
                }
            ),
            flush=True,
        )
        return value

    async def run_case(self, name, arguments, label):
        provider = name.split(".")[0]
        if provider in self.stopped:
            return self.record(
                name,
                label,
                {
                    "status": "not_run_provider_stopped",
                    "arguments": arguments,
                    "reason": self.stopped[provider],
                },
            )
        try:
            plan = self.service.create_plan([{"operation": name, "arguments": arguments}])
            run = await self.service.start_run(plan["plan_id"], "audit-" + plan["plan_id"])
            await self.service._tasks[run["run_id"]]
            result = self.service.get_result(run["run_id"], run["operations"][0]["operation_id"])
            result["audit_run_id"] = run["run_id"]
        except DomainError as error:
            result = {
                "status": "held_before_dispatch",
                "arguments": arguments,
                "error": {"code": error.code, "message": error.message},
            }
        if provider in {"bharatstock", "drishti"} and result["status"] in {"failed", "unknown"}:
            self.stopped[provider] = result.get("error") or {"code": "failed"}
        self.results.append(result)
        return self.record(name, label, result)

    async def retrieval(self):
        identity = {"ticker": self.args.ticker, "exchange": "NSE"}
        end = date.fromisoformat(self.args.as_of)
        requests = [
            ("bharatstock.get_stock_quote", identity, "identity"),
            ("bharatstock.search_stocks", {"q": self.args.ticker, "limit": 3}, "directory"),
            ("bharatstock.get_stock_fundamentals", identity, "ratios"),
            (
                "bharatstock.get_financials",
                identity | {"period_type": "annual", "page": 1, "page_size": 2},
                "annual",
            ),
            (
                "bharatstock.get_financials",
                identity | {"period_type": "quarterly", "page": 1, "page_size": 4},
                "quarterly",
            ),
            (
                "bharatstock.get_stock_prices",
                identity
                | {
                    "from": (end - timedelta(days=13)).isoformat(),
                    "to": self.args.as_of,
                    "page": 1,
                    "page_size": 10,
                },
                "eod",
            ),
            (
                "bharatstock.get_corporate_actions",
                identity | {"action_type": "dividend", "page": 1, "page_size": 5},
                "dividends",
            ),
        ]
        for name, args, label in requests:
            await self.run_case(name, args, label)
        await self.financial()
        try:
            metadata = await self.service.connect_drishti()
            self.save("drishti-metadata.json", metadata)
        except DomainError as error:
            self.save(
                "drishti-metadata.json", {"error": {"code": error.code, "message": error.message}}
            )
            self.stopped["drishti"] = {"code": error.code, "message": error.message}
            return
        q = {
            "symbols": [self.args.ticker],
            "from": (end - timedelta(days=14)).isoformat(),
            "to": self.args.as_of,
            "limit": 2,
            "page": 1,
        }
        dr = [
            ("drishti.get_symbols", {"query": {"symbols": [self.args.ticker]}}, "identity"),
            ("drishti.resolve_symbols", {"queries": [self.args.company_name]}, "resolution"),
            ("drishti.get_announcement_categories", {}, "categories"),
            ("drishti.get_news", {"query": q}, "news"),
            ("drishti.get_announcements", {"query": q | {"limit": 1}}, "announcements"),
            (
                "drishti.list_earnings",
                {"query": q | {"from": (end - timedelta(days=89)).isoformat(), "limit": 1}},
                "earnings-list",
            ),
        ]
        earnings = None
        for name, args, label in dr:
            result = await self.run_case(name, args, label)
            if name == "drishti.list_earnings":
                earnings = result
        name = "drishti.get_earnings_filing"
        if earnings and earnings["status"] == "success":
            data = data_payload(earnings["payload"], earnings["payload_kind"])
            rows = data.get("data", []) if isinstance(data, dict) else []
            if rows:
                row = rows[0]
                selector = row.get("earnings_id") or row.get("id")
                detail = (
                    {"earnings_id": selector, "detailed": True}
                    if selector
                    else {
                        "symbol": row.get("symbol"),
                        "quarter": row.get("quarter"),
                        "detailed": True,
                    }
                )
                await self.run_case(name, detail, "returned-selector")
            else:
                self.record(
                    name,
                    "discovery",
                    {
                        "status": "not_run_no_selector",
                        "reason": "No real discovery record; no selector was fabricated.",
                    },
                )
        else:
            self.record(
                name,
                "discovery",
                {
                    "status": "not_run_no_selector",
                    "reason": "No successful nonempty earnings discovery; no fabricated selector or fallback.",
                },
            )

    async def financial(self):
        annual = next(
            (
                r
                for r in self.results
                if r.get("operation") == "bharatstock.get_financials"
                and r.get("receipt", {}).get("arguments", {}).get("period_type") == "annual"
                and r["status"] == "success"
            ),
            None,
        )
        quarterly = next(
            (
                r
                for r in self.results
                if r.get("operation") == "bharatstock.get_financials"
                and r.get("receipt", {}).get("arguments", {}).get("period_type") == "quarterly"
                and r["status"] == "success"
            ),
            None,
        )
        if not annual:
            return
        facts = prepare_financial_facts(annual, "INR")
        self.save("annual-facts.json", facts)
        basis = (
            "consolidated"
            if any(f["basis"] == "consolidated" for f in facts["facts"])
            else "standalone"
            if any(f["basis"] == "standalone" for f in facts["facts"])
            else None
        )
        if basis is None:
            return
        selected = [f for f in facts["facts"] if f["basis"] == basis]
        dates = sorted({f["period_end"] for f in selected if f["period_end"]}, reverse=True)

        def pick(metric, end):
            found = [f for f in selected if f["metric"] == metric and f["period_end"] == end]
            return found[0] if len(found) == 1 else None

        current = pick("revenue", dates[0]) if dates else None
        previous = pick("revenue", dates[1]) if len(dates) > 1 else None
        profit = pick("net_profit", dates[0]) if dates else None
        cfo, capex = (
            pick(field, dates[0]) if dates else None for field in ("cash_flow_operating", "capex")
        )
        calls = []
        if current and profit:
            calls += [
                ("facts.check_compatibility", {"facts": [profit, current], "purpose": "ratio"}),
                ("facts.convert_units", {"value": current, "target_unit": "INR_crore"}),
                ("finance.calculate_margins", {"profit": profit, "revenue": current}),
            ]
        if current and previous:
            years = str(
                Decimal(
                    (
                        date.fromisoformat(current["period_end"])
                        - date.fromisoformat(previous["period_end"])
                    ).days
                )
                / Decimal("365.25")
            )
            calls += [
                ("finance.compare_periods", {"previous": previous, "current": current}),
                (
                    "finance.calculate_cagr",
                    {"previous": previous, "current": current, "years": years},
                ),
            ]
        if cfo and capex:
            calls.append(("finance.calculate_cashflow_metrics", {"cfo": cfo, "capex": capex}))
        if quarterly:
            qfacts = prepare_financial_facts(quarterly, "INR")
            self.save("quarterly-facts.json", qfacts)
            quarters = [
                f for f in qfacts["facts"] if f["basis"] == basis and f["metric"] == "revenue"
            ]
            if len(quarters) == 4:
                calls.append(("finance.calculate_ttm", {"facts": quarters}))
        before = copy.deepcopy(self.service.ledger.requests)
        for name, arguments in calls:
            await self.run_case(name, arguments, "real-facts")
        for spec in planning_capabilities():
            name = spec["function"]
            period = "quarterly" if name.endswith("ttm") else "annual"
            source = quarterly if period == "quarterly" else annual
            if not source:
                continue
            try:
                plan = self.service.plan_financial(
                    name,
                    self.args.ticker,
                    "NSE",
                    period_type=period,
                    basis=basis,
                    money_unit="INR",
                    source={
                        "run_id": source["audit_run_id"],
                        "operation_id": source["operation_id"],
                    },
                    fetch_missing=False,
                )
                run = await self.service.start_run(plan["plan_id"], "audit-" + plan["plan_id"])
                await self.service._tasks[run["run_id"]]
                result = self.service.get_result(
                    run["run_id"], run["operations"][-1]["operation_id"]
                )
                result["audit_run_id"] = run["run_id"]
            except DomainError as error:
                result = {
                    "status": "incomplete",
                    "error": {"code": error.code, "message": error.message},
                }
            self.record(name, "retained-source", result)
        assert self.service.ledger.requests == before, (
            "Local financial checks unexpectedly fetched data"
        )
        self.save(
            "finance-source-policy.json",
            {
                "basis": basis,
                "amount_scale": "INR",
                "unit_origin": "caller_declared_not_independently_verified",
                "period_ends": dates,
                "before_http": before,
                "after_http": self.service.ledger.requests,
                "valuation_policy": "No invented forecasts or unsupported operating-working-capital/EBIT mappings",
            },
        )
        for name in VALUATION:
            try:
                self.service.calculate(name, {})
                raise AssertionError("Missing required valuation inputs were unexpectedly accepted")
            except DomainError as error:
                self.record(
                    name,
                    "missing-input-guard",
                    {
                        "status": "needs_explicit_inputs",
                        "arguments": {},
                        "error": {"code": error.code, "message": error.message},
                        "note": "Software-reference math passed separately; no HUL valuation/FCFF was fabricated.",
                    },
                )

    def finish_matrix(self):
        for row in self.matrix.values():
            statuses = {case["status"] for case in row["cases"]}
            if statuses == {"success"}:
                row["new_ticker_outcome"] = "success"
            elif statuses <= {"success", "empty"} and statuses:
                row["new_ticker_outcome"] = "success_or_empty"
            elif "unknown" in statuses or "failed" in statuses:
                row["new_ticker_outcome"] = "failed_or_uncertain"
            elif "incomplete" in statuses:
                row["new_ticker_outcome"] = "incomplete"
            elif statuses:
                row["new_ticker_outcome"] = sorted(statuses)[0]
            if row["function"] in VALUATION:
                row["notes"].append(
                    "Requires explicit valuation/model inputs; passing offline reference math is not automatic company valuation."
                )
            if row["new_ticker_outcome"] == "incomplete":
                row["notes"].append(
                    "Inspect exact missing-context/data issues; incomplete is not automatically a calculation bug."
                )
        self.save(
            "function-matrix.json",
            {
                "ticker": self.args.ticker,
                "core_version": "0.2.0",
                "as_of": self.args.as_of,
                "offline_suite": self.offline,
                "functions": list(self.matrix.values()),
                "review_function_contracts": [s["function"] for s in self.contracts["review"]],
                "review_scope": "Separate ten local review functions covered by the offline suite; not all exercised against this ticker in this audit.",
            },
        )
        shutil.copyfile(self.junit, self.output / "offline-tests.xml")
        (self.output / "offline-tests.xml").chmod(0o600)
        counts = dict(Counter(row["new_ticker_outcome"] for row in self.matrix.values()))
        lines = [
            f"# Function audit: {self.args.ticker}",
            "",
            f"As of {self.args.as_of}. Core 0.2.0. Fresh real API calls; no provider replay, invented company facts or forecasts.",
            "",
            f"Offline suite: {self.offline['tests']} tests, {self.offline['failures']} failures, {self.offline['skipped']} skipped. These use labelled fictional software fixtures; the company cases below are separate real observations.",
            "",
            "## Function matrix",
            "",
            "| Function | Offline contract/math | New-ticker outcome | Evidence |",
            "| --- | --- | --- | --- |",
        ]
        for row in self.matrix.values():
            files = (
                ", ".join(f"[{c['case']}]({c['file']})" for c in row["cases"])
                or "No usable prerequisites"
            )
            lines.append(
                f"| `{row['function']}` | {row['offline_status']} | **{row['new_ticker_outcome']}** | {files} |"
            )
        lines += [
            "",
            "## Interpretation",
            "",
            "Success means the implemented function executed on the returned inputs. It does not independently authenticate provider data or original filings.",
            "",
            "Incomplete means the response lacked required values/context or the eligibility check refused a calculation. Read the saved issues before treating it as a bug. Held-before-dispatch means the guard stopped a provider call. Needs-explicit-inputs means no company valuation was fabricated.",
            "",
            "Financial scales are explicit caller declarations where absent from the provider. Group/owners profit, capex definitions, periods and adjustments remain visible in raw sanitized cases and facts. DCF/FCFF/sensitivity/scenarios have passing numerical software references but were not run as an actual company valuation.",
            "",
            "## Accounting",
            "",
            "```json",
            json.dumps(self.service.ledger.snapshot(), indent=2),
            "```",
            "",
            "The snapshot is taken after SDK cleanup. Credits are estimates, not measured account debit. Per-process counters do not coordinate other clients' account use.",
            "",
            "## Files",
            "",
            "- `cases/`: complete sanitized provider/local responses, receipts and missing-input guards.",
            "- `annual-facts.json`, `quarterly-facts.json`: reviewed-path facts when present.",
            "- `function-matrix.json`: machine-readable outcomes and exact offline test references.",
            "- `contracts.json`: all current retrieval/local/company/review schemas.",
            "- `run-plan.json`, `run-summary.json`, `manifest.json`: scope, costs and integrity.",
            "- `offline-tests.xml`: full test results for this run.",
            "",
            "Private diagnostic material: do not publish raw licensed payloads. Manual review/delete date is in run-plan.json; expiry is not automatic deletion. No provider keys are included. Hashes check exported integrity, not source truth.",
        ]
        (self.output / "REPORT.md").write_text("\n".join(lines) + "\n")
        (self.output / "REPORT.md").chmod(0o600)
        self.save(
            "run-summary.json",
            {
                "started_at": self.started,
                "finished_at": datetime.now(UTC).isoformat(),
                "ticker": self.args.ticker,
                "outcome_counts": counts,
                "ledger": self.service.ledger.snapshot(),
                "stopped_providers": self.stopped,
                "original_documents_independently_verified": False,
                "external_model_calls": 0,
            },
        )
        manifest = {
            "sha256": {
                str(p.relative_to(self.output)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(self.output.rglob("*"))
                if p.is_file()
            },
            "source_code_sha256": {
                str(p.relative_to(self.root)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted((self.root / "src/margin").rglob("*.py"))
            },
            "contains_provider_keys": False,
            "new_ticker": self.args.ticker,
            "source_mode": "live",
        }
        self.save("manifest.json", manifest)
        for p in self.output.rglob("*"):
            if p.is_file() and any(
                key.encode() in p.read_bytes() for key in self.service.sanitizer.secrets
            ):
                raise ValueError("Credential content detected; archive withheld")
        archive = self.output.with_suffix(".zip")
        fd = os.open(archive, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "wb") as stream, ZipFile(stream, "w", ZIP_DEFLATED) as z:
            for p in sorted(self.output.rglob("*")):
                if p.is_file():
                    z.write(p, str(Path(self.output.name) / p.relative_to(self.output)))
        print(
            json.dumps(
                {
                    "report": str(self.output / "REPORT.md"),
                    "archive": str(archive),
                    "counts": counts,
                    "ledger": self.service.ledger.snapshot(),
                }
            ),
            flush=True,
        )

    async def run(self):
        try:
            await self.retrieval()
        except DomainError as error:
            self.save("audit-stop.json", {"code": error.code, "message": error.message})
        finally:
            await self.service.close()
        self.finish_matrix()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--confirm-live", action="store_true", required=True)
    p.add_argument("--ticker", required=True)
    p.add_argument("--company-name", required=True)
    p.add_argument("--as-of", required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--offline-results", type=Path, required=True)
    args = p.parse_args()
    if not re.fullmatch(r"[A-Z0-9][A-Z0-9&_.-]{0,39}", args.ticker):
        p.error("Use an explicit NSE ticker")
    date.fromisoformat(args.as_of)
    asyncio.run(Audit(args).run())


if __name__ == "__main__":
    main()
