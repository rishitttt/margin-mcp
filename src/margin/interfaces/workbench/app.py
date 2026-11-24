"""Local-only HTTP adapter. No provider retrieval logic lives in routes."""

from __future__ import annotations

import argparse
import json
import secrets
from contextlib import asynccontextmanager
from dataclasses import replace
from importlib.resources import files

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.trustedhost import TrustedHostMiddleware

from margin.analysis.company import planning_capabilities
from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.core.service import ResearchService


def create_app(settings=None, service=None):
    @asynccontextmanager
    async def lifespan(app):
        app.state.service = service or ResearchService(settings or Settings.from_env())
        app.state.nonce = secrets.token_urlsafe(32)
        try:
            yield
        finally:
            await app.state.service.close()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])

    @app.exception_handler(DomainError)
    async def domain_error(request, error):
        code = (
            404
            if error.code == "not_found"
            else 410
            if error.code == "result_unavailable"
            else 409
            if error.code in {"idempotency_conflict", "capacity", "run_active"}
            else 400
        )
        return JSONResponse(
            {"error": {"code": error.code, "message": error.message}}, status_code=code
        )

    @app.middleware("http")
    async def local_requests(request: Request, call_next):
        if request.method not in {"GET", "HEAD"}:
            origin = request.headers.get("origin")
            if origin and origin != str(request.base_url).rstrip("/"):
                return JSONResponse(
                    {"error": {"code": "origin", "message": "Same-origin requests only."}},
                    status_code=403,
                )
            if not secrets.compare_digest(
                request.headers.get("x-margin-action", "").encode(),
                request.app.state.nonce.encode(),
            ):
                return JSONResponse(
                    {
                        "error": {
                            "code": "action_token",
                            "message": "Read local status before submitting an action.",
                        }
                    },
                    status_code=403,
                )
            if not request.headers.get("content-type", "").startswith("application/json"):
                return JSONResponse(
                    {"error": {"code": "content_type", "message": "JSON actions only."}},
                    status_code=415,
                )
            body = bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 64 * 1024:
                    return JSONResponse(
                        {"error": {"code": "request_size", "message": "Request exceeds 64 KiB."}},
                        status_code=413,
                    )
            request._body = bytes(body)
        response = await call_next(request)
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'self'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

    async def json_body(request):
        try:

            def invalid_constant(_):
                raise ValueError

            value = json.loads(await request.body(), parse_constant=invalid_constant)
        except (ValueError, RecursionError):
            raise DomainError("invalid_input", "Invalid JSON action body.") from None
        if not isinstance(value, dict):
            raise DomainError("invalid_input", "JSON body must be an object.")
        return value

    @app.get("/api/status")
    async def status(request: Request):
        return request.app.state.service.status() | {"action_nonce": request.app.state.nonce}

    @app.get("/api/capabilities")
    async def capabilities(request: Request):
        return {"operations": request.app.state.service.capabilities()}

    @app.get("/api/protocols")
    async def review_functions(request: Request):
        return {"functions": request.app.state.service.review_capabilities()}

    @app.post("/api/protocols/invoke")
    async def review_invoke(request: Request):
        body = await json_body(request)
        if set(body) != {"function", "arguments"} or not isinstance(body["arguments"], dict):
            raise DomainError("invalid_input", "Supply a review function and arguments object.")
        return request.app.state.service.review(body["function"], body["arguments"])

    @app.post("/api/protocols/import-source")
    async def review_import(request: Request):
        body = await json_body(request)
        if set(body) != {"run_id", "operation_id", "issuer"} or not all(
            isinstance(v, str) for v in body.values()
        ):
            raise DomainError("invalid_input", "Supply run_id, operation_id and declared issuer.")
        return request.app.state.service.import_review_sources(**body)

    @app.get("/api/analysis/functions")
    async def analysis_functions(request: Request):
        return {"functions": request.app.state.service.calculation_capabilities()}

    @app.get("/api/analysis/sources")
    async def analysis_sources(request: Request):
        return {"sources": request.app.state.service.financial_sources()}

    @app.get("/api/analysis/company-functions")
    async def company_functions():
        return {"functions": planning_capabilities()}

    @app.post("/api/analysis/plans")
    async def financial_plan(request: Request):
        body = await json_body(request)
        allowed = {
            "function",
            "ticker",
            "exchange",
            "period_type",
            "basis",
            "money_unit",
            "metric",
            "source",
            "fetch_missing",
        }
        if not {"function", "ticker", "exchange"} <= set(body) or not set(body) <= allowed:
            raise DomainError(
                "invalid_input", "Supply a company financial function and explicit source policy."
            )
        return request.app.state.service.plan_financial(**body)

    @app.post("/api/analysis")
    async def analysis(request: Request):
        body = await json_body(request)
        if set(body) != {"function", "arguments"} or not isinstance(body["arguments"], dict):
            raise DomainError("invalid_input", "Supply a function and arguments object only.")
        return request.app.state.service.calculate(body["function"], body["arguments"])

    @app.get("/api/runs/{run_id}/operations/{operation_id}/facts")
    async def financial_facts(
        run_id: str, operation_id: str, request: Request, money_unit: str | None = "auto"
    ):
        return request.app.state.service.prepare_facts(run_id, operation_id, money_unit)

    @app.post("/api/provider-connections/drishti")
    async def connect(request: Request):
        return await request.app.state.service.connect_drishti()

    @app.post("/api/plans")
    async def plans(request: Request):
        body = await json_body(request)
        if set(body) == {"operations"} and isinstance(body["operations"], list):
            ops = body["operations"]
        elif set(body) <= {"symbol", "exchange", "modules", "from", "to"} and {
            "symbol",
            "exchange",
            "modules",
        } <= set(body):
            if (
                not isinstance(body["symbol"], str)
                or not isinstance(body["exchange"], str)
                or not isinstance(body["modules"], list)
                or not all(isinstance(m, str) for m in body["modules"])
            ):
                raise DomainError("invalid_input", "Invalid company or module selection.")
            return request.app.state.service.plan_company(
                body["symbol"],
                body["exchange"],
                body["modules"],
                start=body.get("from"),
                end=body.get("to"),
            )
        else:
            raise DomainError(
                "invalid_input", "Supply explicit operations or a bounded company/module selection."
            )
        return request.app.state.service.create_plan(ops)

    @app.post("/api/runs", status_code=202)
    async def run(request: Request):
        body = await json_body(request)
        if set(body) != {"plan_id", "idempotency_key"} or not isinstance(body["plan_id"], str):
            raise DomainError("invalid_input", "Supply plan_id and idempotency_key only.")
        return await request.app.state.service.start_run(body["plan_id"], body["idempotency_key"])

    @app.get("/api/runs")
    async def recent_runs(request: Request):
        return {"runs": request.app.state.service.recent_runs()}

    @app.get("/api/runs/{run_id}")
    async def run_status(run_id: str, request: Request):
        return request.app.state.service.get_run(run_id)

    @app.get("/api/runs/{run_id}/operations/{operation_id}")
    async def result(run_id: str, operation_id: str, request: Request):
        return request.app.state.service.get_result(run_id, operation_id)

    @app.post("/api/runs/{run_id}/cancel")
    async def cancel(run_id: str, request: Request):
        return await request.app.state.service.cancel(run_id)

    static = files("margin.interfaces.workbench").joinpath("static")
    app.mount("/static", StaticFiles(directory=str(static)), name="static")

    @app.get("/")
    async def index():
        return FileResponse(str(static.joinpath("index.html")))

    return app


def main():
    import uvicorn

    parser = argparse.ArgumentParser(description="Run the local Margin research workbench")
    parser.add_argument("--mode", choices=["synthetic", "live"])
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--scenario", choices=["none", "drishti_unavailable", "empty_news", "unsafe_output"]
    )
    args = parser.parse_args()
    settings = Settings.from_env()
    overrides = {
        k: v
        for k, v in {"mode": args.mode, "synthetic_fault": args.scenario}.items()
        if v is not None
    }
    settings = replace(settings, **overrides)
    print(f"Margin workbench: http://127.0.0.1:{args.port} — {settings.mode.upper()} mode")
    uvicorn.run(
        create_app(settings),
        host="127.0.0.1",
        port=args.port,
        workers=1,
        reload=False,
        access_log=False,
        log_level="warning",
    )
