"""Explicit INFY-only live acceptance; limits are fixed, no retries or inference."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import httpx

from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.service import ResearchService
from margin.evidence.results import data_payload
from margin.interfaces.agent.local_config import read_provider_env


def requests():
    window = {"symbols": ["INFY"], "from": "2026-11-10", "to": "2026-11-25", "page": 1}
    return [
        {"operation": "drishti.get_news", "arguments": {"query": window | {"limit": 2}}},
        {
            "operation": "drishti.get_announcements",
            "arguments": {"query": window | {"limit": 1, "include_extracted_information": False}},
        },
        {
            "operation": "drishti.list_earnings",
            "arguments": {"query": window | {"from": "2026-09-01", "limit": 1}},
        },
    ]


def detail_request(result):
    decoded = data_payload(result["payload"], result["payload_kind"])
    rows = decoded.get("data", []) if isinstance(decoded, dict) else []
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        return None
    first = rows[0]
    if first.get("symbol") != "INFY":
        return None
    identifier = first.get("earnings_id") or first.get("id")
    if identifier:
        args = {"earnings_id": identifier, "detailed": True}
    elif first.get("symbol") == "INFY" and first.get("quarter"):
        args = {"symbol": "INFY", "quarter": first["quarter"], "detailed": True}
    else:
        return None
    return {"operation": "drishti.get_earnings_filing", "arguments": args}


async def account(key):
    async with httpx.AsyncClient(timeout=20, follow_redirects=False) as client:
        async with client.stream(
            "GET", "https://developers.manasija.in/v1/account", headers={"X-API-Key": key}
        ) as response:
            if response.status_code != 200:
                raise DomainError("account_access", "Account check failed; no automatic retry.")
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > 256 * 1024:
                    raise DomainError("account_size", "Account response exceeded its bound.")
    decoded = json.loads(body)
    data = decoded.get("data", {})
    # Do not retain account identity, billing/contact details or arbitrary metadata.
    return {k: data.get(k) for k in ("status", "balance", "products")}


def assert_access(profile):
    try:
        balance = Decimal(str(profile["balance"]))
    except (InvalidOperation, KeyError, TypeError):
        raise DomainError("account_shape", "Cannot establish current credit balance.") from None
    if not balance.is_finite() or balance < 8 or profile.get("status") != "active":
        raise DomainError("account_access", "Active access and eight available credits required.")


async def check(output, env_file):
    key = read_provider_env(env_file).get("DRISHTI_API_KEY")
    if not key:
        raise DomainError("credentials", "Configure the Drishti key in the ignored env file.")
    output.mkdir(parents=True, exist_ok=False, mode=0o700)
    allowed = frozenset(r["operation"] for r in requests()) | {"drishti.get_earnings_filing"}
    service = ResearchService(
        Settings(
            mode="live",
            drishti_key=key,
            bharatstock_requests=0,
            drishti_requests=16,
            drishti_credits=8,
            enabled_unverified=allowed,
        )
    )
    summary = {
        "started_at": datetime.now(UTC).isoformat(),
        "scope": "Live provider acceptance; not original-source or model verification",
        "limits": {"bharatstock": 0, "drishti_http": 16, "estimated_credits": 8, "account_gets": 2},
        "account_attempts": 0,
        "observations": [],
        "completed": False,
    }

    def save(name, value):
        clean = service.sanitizer.clean(value)
        descriptor = os.open(output / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        with os.fdopen(descriptor, "w") as stream:
            json.dump(clean, stream, indent=2, allow_nan=False)
            stream.write("\n")

    async def run(request):
        plan = service.create_plan([request])
        save(request["operation"] + "-plan.json", plan)
        run = await service.start_run(plan["plan_id"], "review-acceptance-" + plan["plan_id"])
        await service._tasks[run["run_id"]]
        operation_id = service.get_run(run["run_id"])["operations"][0]["operation_id"]
        result = service.get_result(run["run_id"], operation_id)
        save(request["operation"] + ".json", result)
        observation = {
            "operation": request["operation"],
            "status": result["status"],
            "http_attempts": result["receipt"]["http_attempts"],
            "error": result["error"],
        }
        summary["observations"].append(observation)
        print(json.dumps(observation), flush=True)
        if result["status"] not in {"success", "empty"}:
            raise DomainError("acceptance_stopped", "Data request failed/held; no automatic retry.")
        imported = service.import_review_sources(run["run_id"], operation_id, "NSE:INFY")
        save(request["operation"] + "-sources.json", imported)
        return result

    before = None
    try:
        summary["account_attempts"] += 1
        before = await account(key)
        save("account-before.json", before)
        assert_access(before)
        save("metadata.json", await service.connect_drishti())
        for request in requests():
            result = await run(request)
            if request["operation"] == "drishti.list_earnings":
                detail = detail_request(result)
                if detail:
                    await run(detail)
                else:
                    summary["observations"].append(
                        {
                            "operation": "drishti.get_earnings_filing",
                            "status": "no_returned_selector",
                        }
                    )
        summary["completed"] = True
    except Exception as error:
        # SDK/HTTP exception strings can expose auth URLs/headers. Never serialize them.
        summary["stopped"] = {
            "code": error.code if isinstance(error, DomainError) else type(error).__name__
        }
    finally:
        await service.close()
        summary["ledger"] = service.ledger.snapshot()
        if before is not None:
            summary["account_attempts"] += 1
            try:
                after = await account(key)
                save("account-after.json", after)
                summary["observed_balance_delta"] = str(
                    Decimal(str(before["balance"])) - Decimal(str(after["balance"]))
                )
                summary["balance_delta_scope"] = "Account-wide; concurrent activity is not isolated"
            except Exception as error:
                summary["account_after_error"] = type(error).__name__
        summary["finished_at"] = datetime.now(UTC).isoformat()
        save("summary.json", summary)
    print(json.dumps(service.sanitizer.clean(summary)), flush=True)
    return summary["completed"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-live", action="store_true", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--env-file", type=Path, default=Path(__file__).resolve().parents[1] / ".env"
    )
    args = parser.parse_args()
    raise SystemExit(0 if asyncio.run(check(args.output, args.env_file)) else 1)


if __name__ == "__main__":
    main()
