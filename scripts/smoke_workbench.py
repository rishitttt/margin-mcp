"""Browser acceptance of complete user flows against a SYNTHETIC server only.

Run with --port and optionally --browser/--output. No real provider traffic.
"""

import argparse
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright


async def main(args):
    root = f"http://127.0.0.1:{args.port}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(executable_path=args.browser, headless=True)
        try:
            page = await browser.new_page(viewport={"width": 1400, "height": 1000})
            assert (await (await page.request.get(root + "/api/status")).json())[
                "mode"
            ] == "synthetic", "Refusing live browser actions"
            errors, external = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))

            async def local_only(route):
                if route.request.url.startswith(root + "/"):
                    await route.continue_()
                else:
                    external.append(route.request.url)
                    await route.abort()

            await page.route("**/*", local_only)

            async def ledger():
                return (await (await page.request.get(root + "/api/status")).json())["ledger"]

            async def preview_company():
                await page.locator("#company-preview").click()
                await page.locator("#plan:not([hidden])").wait_for()
                await page.wait_for_function("() => !previewBusy")
                return await page.evaluate("() => plan")

            async def run_plan():
                await page.locator("#run").click()
                await page.wait_for_function(
                    "() => !runBusy && ['completed','partial','failed','cancelled'].includes(document.getElementById('run-status').textContent)"
                )

            async def calculation():
                return json.loads(await page.locator("#analysis-result").text_content())

            await page.goto(root)
            await page.wait_for_function("() => document.body.dataset.ready === 'true'")
            initial = await ledger()
            assert not any(initial["http_attempts"].values()), (
                "Start a fresh SYNTHETIC server before this acceptance suite."
            )
            assert await page.locator("#financial-task").is_visible()
            assert not await page.locator("#retrieve-task").is_visible()
            assert not await page.locator("#manual-facts").get_attribute("open")
            # Missing prerequisites must fail before even creating a paid plan.
            await page.locator("#company-preview").click()
            await page.locator("#error:not([hidden])").wait_for()
            assert "monetary scale" in await page.locator("#error").inner_text()
            assert await ledger() == initial
            await page.locator("#company-unit").select_option("INR")
            preview = await preview_company()
            assert preview["data_operations"] == {"bharatstock": 1, "drishti": 0}
            # Editing a preview invalidates it immediately, without a call.
            await page.locator("#company-basis").select_option("standalone")
            assert not await page.locator("#plan").is_visible()
            assert await page.locator("#run").is_disabled()
            await page.locator("#company-basis").select_option("consolidated")
            await preview_company()
            assert await ledger() == initial
            await page.evaluate(
                """() => { const b=document.getElementById('run'); b.click(); b.dispatchEvent(new MouseEvent('click',{bubbles:true})); }"""
            )
            await page.wait_for_function(
                "() => !runBusy && document.getElementById('run-status').textContent === 'completed'"
            )
            assert (await calculation())["status"] == "success"
            assert await page.locator("[data-operation='finance.company_margins']").count() == 1
            assert await page.evaluate(
                "() => preparedFacts.size > 0 && [...preparedFacts.values()].filter(f => f.metric==='revenue').every(f => f.unit==='INR')"
            )
            first_id = await page.evaluate("() => sessionStorage.getItem('margin-last-run')")
            first = await ledger()
            assert (
                first["http_attempts"]["bharatstock"] - initial["http_attempts"]["bharatstock"] == 1
            )
            assert first["http_attempts"]["drishti"] == initial["http_attempts"]["drishti"]
            await page.locator("#company-function").select_option("finance.company_growth")
            assert (await preview_company())["data_operations"]["bharatstock"] == 0
            await run_plan()
            assert (await calculation())["status"] == "success"
            assert await ledger() == first
            # History restores results; loading facts must not overwrite calculation output.
            await page.locator("#run-history").select_option(first_id)
            await page.wait_for_function(
                "() => !runBusy && !!document.querySelector('[data-operation=\"finance.company_margins\"]')"
            )
            await page.locator("#prepare-source").evaluate("e => e.click()")
            await page.wait_for_function("() => !factsBusy")
            assert (await calculation())["function"] == "finance.company_margins"
            assert await ledger() == first
            await page.reload()
            await page.wait_for_function("() => document.body.dataset.ready === 'true'")
            assert await page.locator("#symbol").input_value() == "SYNTHA"
            assert await page.locator("#company-unit").input_value() == "INR"
            assert await page.locator("#run-history").input_value() == first_id
            assert await ledger() == first
            # Individual-fact mode suggests compatible inputs and also previews.
            await page.locator("#manual-facts > summary").click()
            await page.locator("#pair-function").select_option("finance.calculate_margins")
            assert await page.locator("#fact-a").input_value()
            await page.locator("#compare-facts").click()
            await page.locator("#plan:not([hidden])").wait_for()
            assert await ledger() == first
            await run_plan()
            assert (await calculation())["status"] == "success"
            # A different company clears old facts/units and cannot silently reuse them.
            assert await page.locator("#company-function option").count() == 9
            await page.locator("#company-unit").select_option("auto")
            await page.wait_for_function("() => !factsBusy && preparedFacts.size > 0")
            assert await page.evaluate(
                "() => [...preparedFacts.values()].every(f => f.unit_origin === 'provider_documentation')"
            )
            for function, expected in [
                ("finance.company_data_readiness", "success"),
                ("finance.company_profitability", "partial"),
                ("finance.company_cash_conversion", "partial"),
                ("finance.company_balance_sheet_metrics", "incomplete"),
            ]:
                await page.locator("#company-function").select_option(function)
                assert (await preview_company())["data_operations"]["bharatstock"] == 0
                await run_plan()
                assert (await calculation())["status"] == expected
                assert await ledger() == first
            await page.locator("#company-function").select_option("finance.company_margins")
            await page.locator("#company-unit").select_option("INR")
            await page.wait_for_function("() => !factsBusy")
            await page.locator("#symbol").fill("SYNTHB")
            await page.locator("#exchange").select_option("BSE")
            assert await page.evaluate("() => preparedFacts.size === 0")
            assert await page.locator("#company-unit").input_value() == ""
            assert await page.locator(".result-card").count() == 0
            await page.locator("#company-unit").select_option("INR")
            await page.locator("#company-fetch").uncheck()
            await page.locator("#company-preview").click()
            await page.locator("#error:not([hidden])").wait_for()
            assert "No matching retained" in await page.locator("#error").inner_text()
            assert await ledger() == first
            # Switching back restores only that listing's declared unit and local facts.
            await page.locator("#symbol").fill("SYNTHA")
            await page.locator("#exchange").select_option("NSE")
            await page.wait_for_function("() => !factsBusy && preparedFacts.size > 0")
            assert await page.locator("#company-unit").input_value() == "INR"
            assert (await preview_company())["data_operations"]["bharatstock"] == 0
            await run_plan()

            # Safe source-expiry UI: clear unusable selections without refetching.
            async def expired(route):
                await route.fulfill(
                    status=410,
                    content_type="application/json",
                    body=json.dumps(
                        {
                            "error": {
                                "code": "result_unavailable",
                                "message": "Test result expired; not refetched.",
                            }
                        }
                    ),
                )

            await page.route("**/facts*", expired)
            await page.locator("#prepare-source").click()
            await page.locator("#error:not([hidden])").wait_for()
            assert await page.evaluate("() => preparedFacts.size === 0")
            assert await ledger() == first
            await page.unroute("**/facts*", expired)
            await page.locator("#prepare-source").click()
            await page.wait_for_function("() => !factsBusy && preparedFacts.size > 0")
            # A held/stale preview response must not reappear after editing the listing.
            request_seen = asyncio.Event()
            release = asyncio.Event()

            async def delayed_preview(route):
                request_seen.set()
                await release.wait()
                await route.continue_()

            await page.route("**/api/analysis/plans", delayed_preview)
            await page.locator("#company-preview").click()
            await request_seen.wait()
            assert await page.locator("#symbol").is_disabled()
            await page.evaluate(
                "() => { const s=document.getElementById('symbol'); s.value='SYNTHB'; s.dispatchEvent(new Event('input')); }"
            )
            release.set()
            await page.wait_for_function("() => !previewBusy")
            assert not await page.locator("#plan").is_visible()
            await page.unroute("**/api/analysis/plans", delayed_preview)
            await page.locator("#symbol").fill("SYNTHA")
            await page.wait_for_function("() => !factsBusy")
            # The DCF tab/form is gone; every local function remains testable in Finance.
            assert await page.locator("#task-valuation, #dcf-form").count() == 0
            await page.locator("#local-tester > summary").click()
            assert await page.locator("#analysis-function option").count() == 16
            await page.locator("#analysis-function").select_option("finance.calculate_fcff")
            assert (
                "change_in_working_capital" in await page.locator("#analysis-schema").text_content()
            )
            await page.locator("#analysis-arguments").fill(
                json.dumps(
                    {
                        "ebit": "100",
                        "tax_rate": "0.25",
                        "depreciation": "10",
                        "capex": "20",
                        "change_in_working_capital": "5",
                        "amount_unit": "INR",
                    }
                )
            )
            await page.locator("#analysis-run").click()
            await page.locator("#plan:not([hidden])").wait_for()
            assert "100" in await page.locator(".plan-arguments pre").text_content()
            assert await ledger() == first
            await run_plan()
            assert (await calculation())["values"]["fcff"] == "60.00"
            assert await ledger() == first
            # DCF uses canonical timing/unit labels, not raw scalar auto-formatting.
            await page.locator("#analysis-function").select_option("finance.calculate_dcf")
            await page.locator("#analysis-arguments").fill(
                json.dumps(
                    {
                        "forecast_fcff": [10, 10, 10],
                        "wacc": 0.1,
                        "terminal_growth": 0,
                        "debt": 20,
                        "cash": 5,
                        "other_equity_adjustments": -2,
                        "diluted_shares": 10,
                        "amount_unit": "INR",
                        "valuation_date": "2026-11-27",
                        "company_type": "non_financial",
                    }
                )
            )
            await page.locator("#analysis-run").click()
            await page.locator("#plan:not([hidden])").wait_for()
            await run_plan()
            assert (await calculation())["report"]["version"] == "margin.dcf_report.v1"
            assert (
                "₹100.00"
                in await page.locator("#analysis-values tr")
                .filter(has_text="undiscounted")
                .inner_text()
            )
            assert (
                "₹75.13"
                in await page.locator("#analysis-values tr")
                .filter(has_text="Present value of terminal value")
                .inner_text()
            )
            assert await ledger() == first
            if args.output:
                args.output.mkdir(parents=True, exist_ok=True)
                await page.screenshot(path=str(args.output / "dcf-canonical.png"), full_page=True)

            # Invalid JSON cannot submit a plan or dispatch a request.
            await page.locator("#analysis-arguments").fill("{")
            assert not await page.locator("#plan").is_visible()
            await page.locator("#analysis-run").click()
            await page.locator("#error:not([hidden])").wait_for()
            assert await ledger() == first
            # A legacy saved tab migrates to Finance and never hides both views.
            await page.evaluate("sessionStorage.setItem('margin-task','valuation')")
            await page.reload()
            await page.wait_for_function("() => document.body.dataset.ready === 'true'")
            assert await page.locator("#financial-task").is_visible()
            assert await ledger() == first
            # Full provider catalog includes operations absent from the overview picker.
            await page.locator("#task-retrieve").click()
            await page.locator("#retrieval-tester > summary").click()
            assert await page.locator("#retrieval-function option").count() == 14
            await page.locator("#retrieval-function").select_option(
                "drishti.get_announcement_categories"
            )
            await page.locator("#retrieval-starter").click()
            await page.locator("#retrieval-run").click()
            await page.locator("#plan:not([hidden])").wait_for()
            assert await ledger() == first
            await run_plan()
            assert (
                await page.locator("[data-operation='drishti.get_announcement_categories']").count()
                == 1
            )
            assert "success" in await page.locator("#cards").inner_text()
            first = await ledger()
            # Held capability remains inspectable but cannot run from the tester.
            await page.evaluate(
                "() => { capabilities.get('drishti.get_announcement_categories').enabled = false; capabilities.get('drishti.get_announcement_categories').held_reason = 'Held for acceptance test'; showRetrievalContract(); }"
            )
            assert await page.locator("#retrieval-run").is_disabled()
            assert (
                "Held for acceptance test"
                in await page.locator("#retrieval-function-note").inner_text()
            )
            await page.locator("#retrieval-tester > summary").click()
            # Explicit retrieval selection, then earnings detail also previews its cost.
            await page.locator("#task-retrieve").click()
            assert await page.locator("input[name=module]:checked").count() == 1
            for name in ["quarterly", "prices", "news", "announcements", "earnings"]:
                await page.locator(f"input[value='{name}']").check()
            await page.locator("#preview").click()
            await page.locator("#plan:not([hidden])").wait_for()
            assert await ledger() == first
            await run_plan()
            assert await page.locator(".result-card").count() == 6
            assert await page.locator("svg.price-chart").count() == 1
            if args.output:
                args.output.mkdir(parents=True, exist_ok=True)
                await page.screenshot(
                    path=str(args.output / "workbench-desktop.png"), full_page=True
                )
            before_detail = await ledger()
            await page.get_by_role("button", name="Inspect this earnings record").click()
            await page.locator("#plan:not([hidden])").wait_for()
            assert await ledger() == before_detail
            await run_plan()
            text = await page.locator("#cards").inner_text()
            assert (
                "requires authorized resolution" in text
                and "Normalized/raw revenue units are missing or different" in text
            )
            assert "synthetic-private-key-never-forward" not in text and "api_key=" not in text
            await page.evaluate(
                """() => appendResult({operation:'drishti.get_news', provider:'drishti', mode:'synthetic', status:'success', payload_kind:'mcp_result', payload:{structuredContent:{data:[{headline:'<img src=x onerror=window.marginXss=true>',summary:'<script>window.marginXss=true</script>'}]}},receipt:{retrieved_at:'test'},warnings:[],citations:[]})"""
            )
            assert await page.locator(".result-card img").count() == 0
            assert await page.evaluate("window.marginXss === undefined")
            for task in ["financial", "retrieve"]:
                await page.locator("#task-" + task).click()
                await page.set_viewport_size({"width": 390, "height": 844})
                assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
                    task + " mobile overflow"
                )
                await page.set_viewport_size({"width": 1400, "height": 1000})
            await page.locator("#review-tester > summary").click()
            before_review = await ledger()
            expected_review = {
                spec["function"]
                for spec in (await (await page.request.get(root + "/api/protocols")).json())[
                    "functions"
                ]
            }
            await page.locator("#review-catalog").click()
            await page.wait_for_function(
                "expected => document.getElementById('review-function').options.length === expected + 1",
                arg=len(expected_review),
            )
            displayed_review = await page.locator("#review-function option").evaluate_all(
                "options => options.map(option => option.value).filter(Boolean)"
            )
            assert set(displayed_review) == expected_review
            await page.locator("#review-function").select_option("protocols.list_workflows")
            await page.locator("#review-starter").click()
            assert json.loads(await page.locator("#review-arguments").input_value()) == {}
            await page.locator("#review-run").click()
            await page.wait_for_function(
                "() => document.getElementById('review-result').textContent.includes('citation_review@1')"
            )
            await page.locator("#review-function").select_option("evidence.register_sources")
            await page.locator("#review-arguments").fill(
                json.dumps(
                    {
                        "sources": [
                            {
                                "issuer": "NSE:SYNTHA",
                                "title": "<script>fictional</script>",
                                "url": "https://example.invalid/fictional",
                                "kind": "source_locator",
                                "date": None,
                                "date_kind": "unknown",
                            }
                        ]
                    }
                )
            )
            await page.locator("#review-run").click()
            await page.wait_for_function(
                "() => document.getElementById('review-result').textContent.includes('source_id')"
            )
            assert await page.locator("#review-result script").count() == 0
            assert await ledger() == before_review
            await page.locator("#task-financial").click()
            if args.output:
                await page.screenshot(
                    path=str(args.output / "workbench-financial.png"), full_page=True
                )
                await page.set_viewport_size({"width": 390, "height": 844})
                await page.screenshot(
                    path=str(args.output / "workbench-mobile.png"), full_page=True
                )
            assert not errors, errors
            assert not external, external
            print(
                json.dumps(
                    {
                        "status": "passed",
                        "checks": [
                            "prerequisite validation before calls",
                            "preview invalidation",
                            "double-submit guard",
                            "one source fetch and local reuse",
                            "documented auto units and four new company paths with honest missing-data results",
                            "shared declared units",
                            "fact suggestions",
                            "history and reload without dispatch",
                            "company-switch isolation",
                            "missing source policy",
                            "expired source errors",
                            "stale asynchronous preview rejection",
                            "local catalog, explicit FCFF and malformed JSON",
                            "legacy DCF tab migration",
                            "full retrieval catalog and held-operation guard",
                            "retrieval and detail previews",
                            "escaping/redaction",
                            "two mobile task layouts",
                            "local citation/sentiment tester and escaped source registration without provider calls",
                            "no JS errors/external requests",
                        ],
                        "ledger": await ledger(),
                    },
                    indent=2,
                )
            )
        finally:
            await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--browser", default=None)
    parser.add_argument("--output", type=Path, default=None)
    asyncio.run(main(parser.parse_args()))
