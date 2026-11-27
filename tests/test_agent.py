import io
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from margin.core.config import Settings
from margin.core.service import ResearchService
from margin.interfaces.agent.cli import main
from margin.interfaces.agent.client import AgentClient, BridgeError
from margin.interfaces.workbench.app import create_app


@pytest.fixture
def bridge():
    service = ResearchService(Settings())
    with TestClient(create_app(service=service), base_url="http://127.0.0.1") as http:

        def factory(url, **kwargs):
            return AgentClient(url, http=http, **kwargs)

        def call(*args, observer=None):
            out = io.StringIO()
            code = main(list(args), client_factory=factory, output=out, observer=observer)
            return code, json.loads(out.getvalue())

        yield call, service, http


def submitted(call, body, *, company=False, key="agent-test-submission-01"):
    code, plan = call("company-preview" if company else "preview", "--json", json.dumps(body))
    assert code == 0, plan
    code, run = call(
        "run", plan["data"]["plan_id"], "--key", key, "--backend-id", plan["backend_id"]
    )
    assert code == 0, run
    code, finished = call("wait", run["data"]["run_id"], "--seconds", "3")
    assert code == 0 and finished["data"]["status"] not in {"queued", "running"}
    return plan, finished["data"]


def test_agent_catalog_discovery_has_costs_holds_and_full_selected_schemas(bridge):
    call, _, _ = bridge
    code, catalog = call("catalog")
    assert code == 0 and catalog["mode"] == "synthetic"
    assert list(map(len, catalog["data"].values())) == [13, 15, 9]
    assert all("schema" not in x for x in catalog["data"]["calculations"])
    _, selected = call("catalog", "--name", "finance.calculate_dcf")
    assert "forecast_fcff" in selected["data"]["calculations"][0]["schema"]["properties"]
    _, company = call("catalog", "--name", "finance.company_growth")
    schema = company["data"]["company_functions"][0]["planning_schema"]
    assert "fetch_missing" in schema["properties"] and "ticker" in schema["required"]
    _, status = call("status")
    assert "action_nonce" not in json.dumps(status)
    assert status["data"]["ledger"]["http_attempts"] == {"bharatstock": 0, "drishti": 0}
    assert call("catalog", "--name", "does.not.exist")[0] == 2


def test_separate_agent_invocations_share_budget_dedupe_and_retained_company_source(bridge):
    call, _, _ = bridge
    body = {
        "function": "finance.company_margins",
        "ticker": "SYNTHA",
        "exchange": "NSE",
        "money_unit": "INR",
        "fetch_missing": True,
    }
    plan, run = submitted(call, body, company=True)
    assert plan["data"]["data_operations"]["bharatstock"] == 1
    code, duplicate = call(
        "run",
        plan["data"]["plan_id"],
        "--key",
        "agent-test-submission-01",
        "--backend-id",
        plan["backend_id"],
    )
    assert code == 0 and duplicate["data"]["run_id"] == run["run_id"]
    _, calculated = call("result", run["run_id"], run["operations"][-1]["operation_id"])
    assert calculated["data"]["payload"]["status"] == "success"
    assert "margin_percent" in calculated["data"]["payload"]["values"]
    _, facts = call(
        "facts", run["run_id"], run["operations"][0]["operation_id"], "--money-unit", "INR"
    )
    assert facts["data"]["facts"] and facts["data"]["facts"][0]["unit_origin"] == "caller_declared"
    _, sources = call("sources")
    assert sources["data"]["sources"][0]["run_id"] == run["run_id"]
    reuse, reused = submitted(
        call, body | {"fetch_missing": False}, company=True, key="reuse-agent-02"
    )
    assert reuse["data"]["data_operations"] == {"bharatstock": 0, "drishti": 0}
    assert reused["status"] == "completed"
    _, status = call("status")
    assert status["data"]["ledger"]["http_attempts"]["bharatstock"] == 1
    assert len(call("runs")[1]["data"]["runs"]) == 2


def test_agent_dcf_plan_and_result_use_same_service_without_provider_calls(bridge):
    call, _, _ = bridge
    model = {
        "forecast_fcff": ["10", "10"],
        "wacc": "0.1",
        "terminal_growth": "0",
        "debt": "0",
        "cash": "0",
        "other_equity_adjustments": "0",
        "diluted_shares": "10",
        "amount_unit": "INR",
        "valuation_date": "2026-11-16",
        "company_type": "non_financial",
    }
    _, run = submitted(
        call, {"operations": [{"operation": "finance.calculate_dcf", "arguments": model}]}
    )
    _, result = call("result", run["run_id"], run["operations"][0]["operation_id"])
    from decimal import Decimal

    assert abs(Decimal(result["data"]["payload"]["values"]["value_per_share_inr"]) - 10) < Decimal(
        "1e-25"
    )
    assert call("status")[1]["data"]["ledger"]["http_attempts"] == {"bharatstock": 0, "drishti": 0}


def test_new_command_cannot_replenish_shared_allowance(bridge):
    call, service, _ = bridge
    service.ledger.limits["bharatstock"] = 1
    body = {
        "operations": [
            {
                "operation": "bharatstock.get_stock_quote",
                "arguments": {"ticker": "SYNTHA", "exchange": "NSE"},
            }
        ]
    }
    _, first = submitted(call, body, key="limited-first-01")
    assert first["status"] == "completed"
    _, second = submitted(call, body, key="limited-second-02")
    assert second["status"] == "failed"
    assert second["operations"][0]["error"]["code"] == "request_budget"
    assert call("status")[1]["data"]["ledger"]["http_attempts"]["bharatstock"] == 1


def test_rejected_inputs_are_never_handed_to_pilot_observer(bridge):
    call, _, _ = bridge
    observed = []
    code, _ = call(
        "preview",
        "--json",
        '{"secret":"do-not-record-cli-input"}',
        observer=lambda *event: observed.append(event),
    )
    assert code == 2
    assert "do-not-record-cli-input" not in json.dumps(observed)


def test_mode_restart_expiry_and_malformed_source_fail_without_hidden_calls(bridge):
    call, service, _ = bridge
    assert call("--expect-mode", "live", "status")[1]["error"]["code"] == "mode_mismatch"
    assert (
        call("run", "someplan", "--key", "submission01", "--backend-id", "old")[1]["error"]["code"]
        == "backend_changed"
    )
    assert call("result", "bad/path", "op")[1]["error"]["code"] == "invalid_input"
    body = {"function": "finance.company_margins", "ticker": "SYNTHA", "exchange": "NSE"}
    assert (
        call("company-preview", "--json", json.dumps(body))[1]["error"]["code"] == "source_required"
    )
    bad = body | {"source": {"run_id": [], "operation_id": "x"}}
    assert call("company-preview", "--json", json.dumps(bad))[1]["error"]["code"] == "invalid_input"
    _, run = submitted(
        call,
        {
            "operations": [
                {
                    "operation": "bharatstock.get_stock_quote",
                    "arguments": {"ticker": "SYNTHA", "exchange": "NSE"},
                }
            ]
        },
    )
    before = service.status()["ledger"]
    service._buffers.clear()
    assert (
        call("result", run["run_id"], run["operations"][0]["operation_id"])[1]["error"]["code"]
        == "result_unavailable"
    )
    assert service.status()["ledger"] == before


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1",
        "http://example.com",
        "http://user:pass@localhost",
        "http://localhost/path",
        "http://localhost?key=x",
        "http://localhost:bad",
    ],
)
def test_agent_rejects_remote_or_credential_bearing_origins(url):
    with pytest.raises(BridgeError, match="loopback"):
        AgentClient(url)


def test_transport_uncertainty_does_not_retry_or_echo_credentials():
    calls = []

    def transport(request):
        calls.append(request)
        if request.url.path == "/api/status":
            return httpx.Response(200, json={"mode": "live", "action_nonce": "private-local-nonce"})
        raise httpx.ReadTimeout("sensitive text must not be forwarded")

    with httpx.Client(transport=httpx.MockTransport(transport)) as http:
        c = AgentClient(http=http)
        c.status()
        with pytest.raises(BridgeError) as caught:
            c.run("plan01", "submit-once-01", c.backend_id)
        assert caught.value.uncertain and "sensitive" not in caught.value.message
        assert len(calls) == 2


def test_agent_sanitized_observations_and_recorder_failure_preserve_result(bridge, capsys):
    call, _, _ = bridge
    observed = []
    call("status", observer=lambda *event: observed.append(event))
    assert observed[0][0] == "status" and "action_nonce" not in json.dumps(observed)

    def broken(*_):
        raise OSError("disk unavailable")

    code, result = call("status", observer=broken)
    assert code == 3 and result["data"]["mode"] == "synthetic"
    assert "do not resubmit" in capsys.readouterr().err
