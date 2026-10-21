"""Optional browser acceptance against a running SYNTHETIC workbench only.

python scripts/smoke_workbench.py --port 8765 --browser '/path/to/Chrome'
No actual provider calls, credentials or user browser profile are used.
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
            page = await browser.new_page(viewport={"width": 1400, "height": 1050})
            errors, external = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))

            async def local_only(route):
                if route.request.url.startswith(root + "/"):
                    await route.continue_()
                else:
                    external.append(route.request.url)
                    await route.abort()

            await page.route("**/*", local_only)
            await page.goto(root)
            await page.wait_for_function(
                "() => document.getElementById('symbol').value === 'SYNTHA'"
            )
            status = await (await page.request.get(root + "/api/status")).json()
            assert status["mode"] == "synthetic", "Refusing browser actions on a live workbench"
            initial = status["ledger"]["http_attempts"].copy()
            await page.get_by_role("button", name="Preview operation plan").click()
            await page.locator("#plan:not([hidden])").wait_for()
            preview = await (await page.request.get(root + "/api/status")).json()
            assert preview["ledger"]["http_attempts"] == initial
            await page.evaluate("""() => {
              const b = document.getElementById('run');
              b.click(); b.dispatchEvent(new MouseEvent('click', {bubbles:true}));
            }""")
            await page.wait_for_function(
                "() => document.getElementById('run-status').textContent === 'completed'"
            )
            await page.wait_for_function(
                "() => document.querySelectorAll('.result-card').length === 4"
            )
            financials = page.locator("[data-operation='bharatstock.get_financials']")
            assert await financials.locator("th").all_text_contents() == [
                "period_end_date",
                "fiscal_year",
                "quarter",
                "period_type",
                "consolidation_type",
                "revenue",
                "net_profit",
                "eps",
                "cash_flow_operating",
            ]
            assert "2026-06-30" in await financials.inner_text()
            assert "consolidated" in await financials.inner_text()
            first = await (await page.request.get(root + "/api/status")).json()
            assert first["ledger"]["http_attempts"]["bharatstock"] - initial["bharatstock"] == 2
            assert first["ledger"]["http_attempts"]["drishti"] - initial["drishti"] == 2
            await page.reload()
            await page.wait_for_function(
                "() => document.getElementById('symbol').value === 'SYNTHA'"
            )
            await page.get_by_role("button", name="Restore last run").click()
            await page.wait_for_function(
                "() => document.querySelectorAll('.result-card').length === 4"
            )
            restored = await (await page.request.get(root + "/api/status")).json()
            assert restored["ledger"] == first["ledger"], "Reload/restore must not dispatch"
            for name in ["prices", "earnings"]:
                await page.locator(f"input[value='{name}']").check()
            await page.get_by_role("button", name="Preview operation plan").click()
            await page.locator("#run").click()
            await page.wait_for_function(
                "() => document.getElementById('run-status').textContent === 'completed'"
            )
            await page.wait_for_function(
                "() => document.querySelectorAll('.result-card').length === 6"
            )
            await page.locator("svg.price-chart").wait_for()
            if args.output:
                args.output.mkdir(parents=True, exist_ok=True)
                await page.screenshot(
                    path=str(args.output / "workbench-desktop.png"), full_page=True
                )
            await page.get_by_role("button", name="Inspect this earnings record").click()
            await page.wait_for_function(
                "() => document.querySelectorAll('.result-card').length === 1 && document.getElementById('run-status').textContent === 'completed'"
            )
            assert (
                await page.get_by_text("requires authorized resolution", exact=False).count() >= 1
            )
            text = await page.locator("body").inner_text()
            assert "synthetic-private-key-never-forward" not in text and "api_key=" not in text
            assert "Returned normalized revenue and raw revenue differ" in text
            await page.evaluate(
                """() => appendResult({operation:'drishti.get_news', provider:'drishti', mode:'synthetic', status:'success', payload_kind:'mcp_result', payload:{structuredContent:{data:[{headline:'<img src=x onerror=window.marginXss=true>',summary:'<script>window.marginXss=true</script>'}]}},receipt:{retrieved_at:'test'},warnings:[],citations:[]})"""
            )
            assert await page.locator(".result-card img").count() == 0
            assert await page.evaluate("window.marginXss === undefined")
            await page.set_viewport_size({"width": 390, "height": 844})
            assert await page.evaluate("document.documentElement.scrollWidth <= innerWidth"), (
                "Mobile layout overflows"
            )
            if args.output:
                await page.screenshot(
                    path=str(args.output / "workbench-mobile.png"), full_page=True
                )
            assert errors == [], errors
            assert external == [], external
            final = await (await page.request.get(root + "/api/status")).json()
            print(
                json.dumps(
                    {
                        "status": "passed",
                        "checks": [
                            "local assets",
                            "preview has no side effects",
                            "double submit deduplicated",
                            "reload/restore no refetch",
                            "numeric/event/chart views",
                            "earnings citation redaction and conflict",
                            "escaped provider text",
                            "mobile layout",
                            "no external page requests",
                            "no JavaScript exceptions",
                        ],
                        "ledger": final["ledger"],
                    },
                    indent=2,
                )
            )
        finally:
            await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument(
        "--browser",
        default=None,
        help="System Chromium/Chrome executable; otherwise Playwright's installed browser",
    )
    parser.add_argument(
        "--output", type=Path, default=None, help="Optional local screenshot directory"
    )
    asyncio.run(main(parser.parse_args()))
