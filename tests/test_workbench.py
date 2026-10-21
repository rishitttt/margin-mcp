import time

import pytest
from fastapi.testclient import TestClient

from margin.core.config import Settings
from margin.interfaces.workbench.app import create_app


@pytest.fixture
def client():
    with TestClient(create_app(Settings()), base_url="http://127.0.0.1") as client:
        yield client


def headers(client):
    return {
        "X-Margin-Action": client.get("/api/status").json()["action_nonce"],
        "Origin": "http://127.0.0.1",
    }


def wait(client, run_id):
    for _ in range(100):
        result = client.get("/api/runs/" + run_id).json()
        if result["status"] not in {"queued", "running"}:
            return result
        time.sleep(0.01)
    raise AssertionError("Run did not complete")


def test_page_status_capabilities_and_preview_are_provider_side_effect_free(client):
    assert client.get("/").status_code == 200
    assert client.get("/static/app.js").status_code == 200
    assert client.get("/api/capabilities").status_code == 200
    result = client.post(
        "/api/plans",
        headers=headers(client),
        json={"symbol": "SYNTHA", "exchange": "NSE", "modules": ["snapshot", "news"]},
    )
    assert result.status_code == 200 and result.json()["estimated_credits"] == 1
    assert client.get("/api/status").json()["ledger"]["http_attempts"] == {
        "bharatstock": 0,
        "drishti": 0,
    }
    assert "default-src 'self'" in client.get("/").headers["content-security-policy"]


def test_http_run_dedupe_reload_and_sanitized_detail(client):
    h = headers(client)
    plan = client.post(
        "/api/plans",
        headers=h,
        json={
            "operations": [
                {
                    "operation": "drishti.get_earnings_filing",
                    "arguments": {"earnings_id": "synth-record-1"},
                }
            ]
        },
    ).json()
    body = {"plan_id": plan["plan_id"], "idempotency_key": "workbench-double-01"}
    a = client.post("/api/runs", headers=h, json=body)
    b = client.post("/api/runs", headers=h, json=body)
    assert a.status_code == b.status_code == 202
    assert a.json()["run_id"] == b.json()["run_id"]
    run = wait(client, a.json()["run_id"])
    operation_id = run["operations"][0]["operation_id"]
    response = client.get(f"/api/runs/{run['run_id']}/operations/{operation_id}")
    assert response.status_code == 200
    assert (
        "synthetic-private-key-never-forward" not in response.text
        and "api_key=" not in response.text
    )
    assert response.json()["citations"][0]["requires_resolution"]
    before = client.get("/api/status").json()["ledger"]
    client.get("/")
    client.get("/api/status")
    client.get(f"/api/runs/{run['run_id']}/operations/{operation_id}")
    assert client.get("/api/status").json()["ledger"] == before


def test_local_actions_require_nonce_origin_and_json(client):
    body = {"symbol": "SYNTHA", "exchange": "NSE", "modules": ["snapshot"]}
    assert client.post("/api/plans", json=body).status_code == 403
    h = headers(client)
    assert (
        client.post(
            "/api/plans", json=body, headers=h | {"Origin": "https://other.invalid"}
        ).status_code
        == 403
    )
    assert (
        client.post(
            "/api/plans", content="x", headers=h | {"Content-Type": "text/plain"}
        ).status_code
        == 415
    )
    assert client.post("/api/plans", json={"large": "x" * 66000}, headers=h).status_code == 413
    assert client.get("/api/status", headers={"Host": "attacker.invalid"}).status_code == 400


def test_backend_keys_are_not_returned_and_bad_json_does_not_echo_input():
    key = "a-private-configured-test-key"
    with TestClient(
        create_app(Settings(bharatstock_key=key, drishti_key=key)), base_url="http://127.0.0.1"
    ) as client:
        assert key not in client.get("/api/status").text
        assert key not in client.get("/api/capabilities").text
        h = headers(client)
        result = client.post(
            "/api/plans", headers=h | {"Content-Type": "application/json"}, content='{"x": NaN}'
        )
        assert result.status_code == 400
        result = client.post(
            "/api/plans",
            headers=h,
            json={
                "operations": [
                    {"operation": "bharatstock.search_stocks", "arguments": {"q": key, "limit": 2}}
                ]
            },
        )
        assert result.status_code == 400 and key not in result.text


def test_core_does_not_import_web_framework():
    import ast
    from pathlib import Path

    root = Path(__file__).parents[1] / "src/margin/core"
    for path in root.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.ImportFrom):
                assert not (node.module or "").startswith(
                    ("fastapi", "starlette", "margin.interfaces")
                )
