from __future__ import annotations

import copy
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from importlib.resources import files

from jsonschema import Draft202012Validator, FormatChecker, ValidationError

from margin.core.config import Settings
from margin.core.contracts import DomainError, OperationRequest, encoded_size

SNAPSHOT = json.loads(files("margin.resources").joinpath("drishti-contracts.json").read_text())
DRISHTI = {o["name"]: o for o in SNAPSHOT["operations"]}
NATIVE = {o["name"]: o for o in SNAPSHOT["nativeTools"]}


def schema_hash(schema: dict) -> str:
    def strip(x):
        if isinstance(x, dict):
            return {
                k: strip(v) for k, v in x.items() if k not in {"description", "examples", "title"}
            }
        if isinstance(x, list):
            return [strip(v) for v in x]
        return x

    return hashlib.sha256(json.dumps(strip(schema), sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class Spec:
    key: str
    schema: dict
    path: str = ""
    credits: int = 0
    observed: bool = False

    @property
    def provider(self):
        return self.key.split(".")[0]

    @property
    def name(self):
        return self.key.split(".")[1]


def object_schema(properties, required=()):
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


def build_specs() -> dict[str, Spec]:
    identity = {
        "ticker": {"type": "string", "pattern": r"^[A-Za-z0-9][A-Za-z0-9&_.-]{0,39}$"},
        "exchange": {"enum": ["NSE", "BSE"]},
    }
    paging = {
        "page": {"type": "integer", "minimum": 1},
        "page_size": {"type": "integer", "minimum": 1},
    }
    dated = {
        "from": {"type": "string", "format": "date"},
        "to": {"type": "string", "format": "date"},
    }
    specs = [
        Spec(
            "bharatstock.search_stocks",
            object_schema(
                {
                    "q": {"type": "string", "minLength": 2, "maxLength": 100},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 10},
                },
                ["q", "limit"],
            ),
            "/v1/search",
        ),
        Spec(
            "bharatstock.get_stock_quote",
            object_schema(identity, ["ticker", "exchange"]),
            "/v1/stocks/{ticker}",
            observed=True,
        ),
        Spec(
            "bharatstock.get_stock_fundamentals",
            object_schema(identity, ["ticker", "exchange"]),
            "/v1/stocks/{ticker}/ratios",
            observed=True,
        ),
        Spec(
            "bharatstock.get_financials",
            object_schema(
                identity | paging | {"period_type": {"enum": ["quarterly", "annual"]}},
                ["ticker", "exchange", "period_type", "page", "page_size"],
            ),
            "/v1/stocks/{ticker}/financials",
            observed=True,
        ),
        Spec(
            "bharatstock.get_stock_prices",
            object_schema(
                identity | paging | dated, ["ticker", "exchange", "from", "to", "page", "page_size"]
            ),
            "/v1/stocks/{ticker}/prices",
            observed=True,
        ),
        Spec(
            "bharatstock.get_corporate_actions",
            object_schema(
                identity
                | paging
                | {
                    "action_type": {
                        "enum": ["dividend", "bonus", "split", "rights", "buyback", "other"]
                    }
                },
                ["ticker", "exchange", "page", "page_size"],
            ),
            "/v1/stocks/{ticker}/corporate-actions",
        ),
    ]
    for name, op in DRISHTI.items():
        schema = copy.deepcopy(op["inputSchema"])
        schema["additionalProperties"] = False
        if "$defs" in schema:
            # Remove the permissive arbitrary-object/string/null escape hatch.
            ref = next(b["$ref"] for b in schema["properties"]["query"]["anyOf"] if "$ref" in b)
            schema["properties"]["query"] = {"$ref": ref}
            schema["required"] = ["query"]
            schema["$defs"][ref.split("/")[-1]]["additionalProperties"] = False
        specs.append(
            Spec(
                "drishti." + name,
                schema,
                credits=op["publishedCredits"][0],
                observed=op["dataExecutionObserved"],
            )
        )
    return {s.key: s for s in specs}


class Registry:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.specs = build_specs()
        if settings.enabled_unverified - self.specs.keys():
            raise DomainError(
                "invalid_config", "MARGIN_ENABLE_OPERATIONS contains an unknown operation."
            )

    def spec(self, key: str) -> Spec:
        if not isinstance(key, str) or key not in self.specs:
            raise DomainError(
                "unknown_operation", "This operation is outside the reviewed first-slice registry."
            )
        return self.specs[key]

    def held_reason(self, spec: Spec) -> str | None:
        if self.settings.mode == "synthetic":
            return None
        key = (
            self.settings.bharatstock_key
            if spec.provider == "bharatstock"
            else self.settings.drishti_key
        )
        if not key:
            return "Provider key is not configured in the backend."
        if not spec.observed and spec.key not in self.settings.enabled_unverified:
            return "Live shape is untested; requires explicit MARGIN_ENABLE_OPERATIONS opt-in."
        return None

    def validate(self, request: OperationRequest) -> Spec:
        spec = self.spec(request.operation)
        if encoded_size(request.arguments) > 64 * 1024:
            raise DomainError("invalid_input", "Arguments exceed 64 KiB.")
        try:
            Draft202012Validator(spec.schema, format_checker=FormatChecker()).validate(
                request.arguments
            )
        except ValidationError as e:
            path = ".".join(str(p) for p in e.absolute_path) or "arguments"
            raise DomainError(
                "invalid_input", f"Invalid {path}; check the reviewed operation schema."
            ) from None
        reason = self.held_reason(spec)
        if reason:
            raise DomainError("held_operation", reason)
        a = request.arguments
        if spec.provider == "bharatstock":
            if "ticker" in a:
                self._symbol(a["ticker"])
            if spec.name == "get_financials":
                maximum = 8 if a["period_type"] == "quarterly" else 2
                if a["page_size"] > maximum:
                    raise DomainError(
                        "invalid_input",
                        "Financial history is bounded to eight quarterly/two annual rows per call.",
                    )
            if spec.name == "get_stock_prices":
                self._dates(a["from"], a["to"], 365)
                if a["page_size"] > 300:
                    raise DomainError("invalid_input", "Price page is bounded to 300 rows.")
            if spec.name == "get_corporate_actions" and a["page_size"] > 20:
                raise DomainError("invalid_input", "Corporate actions are bounded to 20 rows.")
        elif "query" in a:
            q = a["query"]
            ids = q.get("ids")
            if ids:
                ids_list = ids if isinstance(ids, list) else [ids]
                if len(ids_list) != 1 or not str(ids_list[0]).strip() or "," in str(ids_list[0]):
                    raise DomainError("invalid_input", "Refetch exactly one explicit record ID.")
                if any(v is not None for k, v in q.items() if k != "ids"):
                    raise DomainError(
                        "invalid_input", "Record IDs override filters; use IDs alone."
                    )
            else:
                selectors = [q.get("symbols"), q.get("scrip_codes")]
                present = [v for v in selectors if v]
                if len(present) != 1:
                    raise DomainError(
                        "invalid_input", "Select one symbol or scrip code explicitly."
                    )
                value = present[0]
                value = value[0] if isinstance(value, list) and len(value) == 1 else value
                if not isinstance(value, str) or "," in value:
                    raise DomainError(
                        "invalid_input",
                        "Select one company; index expansion and broad lists are disabled.",
                    )
                self._symbol(value)
                if spec.name != "get_symbols":
                    maximum = 365 if spec.name == "list_earnings" else 30
                    relative, start, end = q.get("lookback_days"), q.get("from"), q.get("to")
                    if relative is not None:
                        if start is not None or end is not None or not 1 <= relative <= maximum:
                            raise DomainError(
                                "invalid_input",
                                "Use one bounded lookback OR an explicit date pair.",
                            )
                    elif start and end:
                        self._dates(start, end, maximum)
                    else:
                        raise DomainError(
                            "invalid_input", "Supply an explicit bounded discovery window."
                        )
                    if (
                        not isinstance(q.get("page"), int)
                        or q["page"] < 1
                        or not isinstance(q.get("limit"), int)
                        or not 1 <= q["limit"] <= 20
                    ):
                        raise DomainError(
                            "invalid_input", "Supply page >= 1 and limit between 1 and 20."
                        )
        elif spec.name == "resolve_symbols":
            q = a["queries"]
            if isinstance(q, list):
                q = q[0] if len(q) == 1 else ""
            if not isinstance(q, str) or not 2 <= len(q.strip()) <= 100:
                raise DomainError("invalid_input", "Resolve one bounded company name.")
        elif spec.name == "get_earnings_filing":
            by_id = bool(a.get("earnings_id"))
            by_quarter = bool(a.get("symbol") and a.get("quarter"))
            if by_id == by_quarter or (by_id and (a.get("symbol") or a.get("quarter"))):
                raise DomainError(
                    "invalid_input", "Use one earnings ID OR a symbol with a discovered quarter."
                )
            if by_id and (
                not isinstance(a["earnings_id"], str)
                or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", a["earnings_id"])
            ):
                raise DomainError("invalid_input", "Use a bounded earnings ID from metadata.")
            if by_quarter:
                self._symbol(a["symbol"])
                if not re.fullmatch(r"q[1-4]_\d{2}", a["quarter"]):
                    raise DomainError(
                        "invalid_input", "Use a fiscal quarter key from filing metadata."
                    )
        return spec

    def estimate(self, request: OperationRequest) -> int:
        spec = self.spec(request.operation)
        detailed = request.arguments.get("query", {}).get("detailed")
        return spec.credits + (
            1 if detailed and spec.name in {"get_announcements", "list_earnings"} else 0
        )

    def _symbol(self, value):
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9&_.-]{0,39}", value) or value.upper() in {
            "NIFTY",
            "BANKNIFTY",
            "FINNIFTY",
            "SENSEX",
        }:
            raise DomainError(
                "invalid_input", "Use one security identifier; index aliases are disabled."
            )
        if self.settings.mode == "live" and value.upper().startswith("SYNTH"):
            raise DomainError(
                "invalid_input", "Fictional synthetic identities cannot be sent to live providers."
            )

    @staticmethod
    def _dates(start, end, maximum):
        try:
            a, b = date.fromisoformat(start), date.fromisoformat(end)
            valid = 0 <= (b - a).days <= maximum
        except (ValueError, TypeError):
            valid = False
        if not valid:
            raise DomainError(
                "invalid_input",
                f"Use ordered ISO date-only bounds spanning at most {maximum} days.",
            )

    def capabilities(self) -> list[dict]:
        return [
            {
                "operation": s.key,
                "provider": s.provider,
                "schema": copy.deepcopy(s.schema),
                "enabled": self.held_reason(s) is None,
                "held_reason": self.held_reason(s),
                "published_estimated_credits": s.credits,
                "data_execution_observed": s.observed,
                "schema_hash": schema_hash(s.schema),
            }
            for s in self.specs.values()
        ]
