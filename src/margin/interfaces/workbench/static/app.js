"use strict";

const $ = id => document.getElementById(id);
let nonce = "", mode = "synthetic", capabilities = new Map();
let plan = null, submissionKey = null, submitted = false, activeRun = null, pollGeneration = 0;
let runBusy = false, connectionBusy = false, connectionError = "";
const MODULES = [
  ["snapshot", "Snapshot", "bharatstock.get_stock_quote"],
  ["quarterly", "Quarterly financials", "bharatstock.get_financials"],
  ["annual", "Annual financials", "bharatstock.get_financials"],
  ["ratios", "Valuation ratios", "bharatstock.get_stock_fundamentals"],
  ["prices", "EOD price history", "bharatstock.get_stock_prices"],
  ["actions", "Corporate actions", "bharatstock.get_corporate_actions"],
  ["news", "Company news", "drishti.get_news"],
  ["announcements", "Announcements", "drishti.get_announcements"],
  ["earnings", "Earnings discovery", "drishti.list_earnings"],
];

function node(tag, text, className) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (className) el.className = className;
  return el;
}
function showError(error) { $("error").textContent = error.message || String(error); $("error").hidden = false; }
function clearError() { $("error").hidden = true; }
function action(fn) { return async event => { event?.preventDefault(); clearError(); try { await fn(); } catch (e) { showError(e); } }; }
async function api(path, body) {
  const response = await fetch(path, body === undefined ? {cache: "no-store"} : {
    method: "POST", headers: {"Content-Type": "application/json", "X-Margin-Action": nonce}, body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) { const err = new Error(data.error?.message || "Local request failed."); err.code = data.error?.code; throw err; }
  return data;
}
function invalidatePlan() { plan = null; submissionKey = null; submitted = false; $("plan").hidden = true; }
function setBusy(value) {
  runBusy = value;
  for (const id of ["preview", "load-company", "search-directory"]) $(id).disabled = value || connectionBusy;
  $("connect").disabled = value || connectionBusy;
  $("run").disabled = value || connectionBusy || submitted;
  $("cancel").hidden = !value;
}
function showConnection(info) {
  const pending = connectionBusy || info.state === "connecting";
  const ready = info.state === "synthetic" || (info.state === "connected" && info.metadata_fresh);
  $("connect").disabled = runBusy || pending;
  $("connect").textContent = pending ? "Connecting…" : ready ? "Drishti connected · check status" : "Connect / refresh Drishti";
  $("connection-status").textContent = connectionError ? "Connection failed: " + connectionError
    : pending ? "Connecting and checking schemas. This can take up to a minute. Please wait; no data run has started."
    : ready ? "Connected. Preview and run your selected operations. Earlier blocked results are unchanged; they were not retried."
    : info.state === "connected" ? "Connection metadata has expired. Refresh before a new Drishti run."
    : "Not connected. Connect once and wait for confirmation before running Drishti operations.";
}
function format(value) {
  if (value === null || value === undefined) return "— (not returned)";
  if (typeof value === "number") return Number.isFinite(value) ? new Intl.NumberFormat("en-IN", {maximumFractionDigits: 8}).format(value) : "Unusable numeric value";
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}
async function refreshStatus() {
  const status = await api("/api/status");
  nonce = status.action_nonce; mode = status.mode;
  $("mode").textContent = mode.toUpperCase() + (mode === "synthetic" ? " · FICTIONAL DATA" : " · EXPLICIT LIVE ACTIONS");
  $("mode-note").textContent = mode === "synthetic"
    ? "Synthetic mode: fictional companies and values. No real provider calls. Request counts and credits are simulated/estimated." + (status.synthetic_scenario !== "none" ? " Scenario: " + status.synthetic_scenario + "." : "")
    : "Live mode: each Run uses configured backend credentials and local allowances. Untested operations stay held unless explicitly enabled. No page-load data fetch.";
  $("budget").replaceChildren();
  const ledger = status.ledger;
  const rows = [
    ["BharatStock HTTP attempts", `${ledger.http_attempts.bharatstock} / ${ledger.http_limits.bharatstock}`],
    ["Drishti HTTP attempts", `${ledger.http_attempts.drishti} / ${ledger.http_limits.drishti}`],
    ["Drishti estimated credits", `${ledger.completed_estimated_credits} + ${ledger.reserved_credits} held / ${ledger.estimated_credit_limit}`],
    ["Drishti connection", status.providers.drishti.state],
  ];
  for (const [label, value] of rows) { const row = node("div", undefined, "budget-row"); row.append(node("span", label), node("strong", value)); $("budget").append(row); }
  if (status.uncertain_providers.length) $("budget").append(node("p", "Uncertain outcome: " + status.uncertain_providers.join(", ") + ". Reconcile before restarting.", "small"));
  showConnection(status.providers.drishti);
  return status;
}
async function connectDrishti() {
  if (connectionBusy) return;
  connectionBusy = true; connectionError = ""; setBusy(runBusy);
  $("connect").textContent = "Connecting…";
  $("connection-status").textContent = "Checking the current connection…";
  let timer = null, polling = false;
  try {
    const status = await refreshStatus(); // Refreshes the action nonce after a server restart too.
    const info = status.providers.drishti;
    if (info.state !== "synthetic" && !info.metadata_fresh && info.state !== "connecting") {
      timer = setInterval(async () => {
        if (polling) return;
        polling = true;
        try { await refreshStatus(); } catch { /* The action response reports its final error. */ }
        finally { polling = false; }
      }, 1000);
      await api("/api/provider-connections/drishti", {});
    }
  } catch (error) { connectionError = error.message; throw error; }
  finally {
    if (timer !== null) clearInterval(timer);
    connectionBusy = false; setBusy(runBusy);
    try { await refreshStatus(); } catch (error) { showError(error); }
  }
}
function setupModules() {
  $("modules").replaceChildren();
  const holds = new Map();
  for (const [id, label, operation] of MODULES) {
    const wrapper = node("label"); const input = document.createElement("input");
    input.type = "checkbox"; input.value = id; input.name = "module";
    const capability = capabilities.get(operation);
    input.disabled = !capability?.enabled;
    if (input.disabled && capability?.held_reason) holds.set(capability.held_reason, true);
    input.checked = ["snapshot", "quarterly", "news", "announcements"].includes(id) && !input.disabled;
    wrapper.title = capability?.held_reason || "Explicit selection only; no automatic enrichment.";
    wrapper.append(input, node("span", label + (input.disabled ? " · held" : "")));
    $("modules").append(wrapper);
    input.addEventListener("change", invalidatePlan);
  }
  $("access-note").replaceChildren();
  for (const reason of holds.keys()) {
    $("access-note").append(node("p", reason, "small"));
  }
  if ([...holds.keys()].some(reason => reason.includes("MARGIN_ENABLE_OPERATIONS"))) {
    $("access-note").append(node("p", "Held means a local test restriction, not a provider subscription rejection. Update MARGIN_ENABLE_OPERATIONS in the server environment and restart to enable the selected live tests.", "small"));
  }
}
function company() { return {symbol: $("symbol").value.trim().toUpperCase(), exchange: $("exchange").value}; }
async function preview() {
  const selected = [...document.querySelectorAll("input[name=module]:checked")].map(el => el.value);
  plan = await api("/api/plans", {...company(), modules: selected, from: $("price-from").value, to: $("price-to").value});
  submissionKey = crypto.randomUUID(); submitted = false;
  $("plan-body").replaceChildren();
  for (const op of plan.operations) $("plan-body").append(node("div", op.operation, "plan-op"));
  $("plan-body").append(node("p", `${plan.operations.length} explicit data operations · ${plan.estimated_credits} estimated Drishti credits`, "plan-total"));
  $("run").disabled = false; $("run").textContent = "Run selected operations"; $("plan").hidden = false;
}
async function submitPlan(selectedPlan, key) {
  if (connectionBusy) throw new Error("Wait for Drishti connection checks to finish.");
  setBusy(true);
  try {
    if (mode === "live" && selectedPlan.operations.some(op => op.operation.startsWith("drishti."))) {
      const status = await refreshStatus();
      const info = status.providers.drishti;
      if (info.state !== "connected" || !info.metadata_fresh) {
        throw new Error("Drishti is not ready. Click Connect / refresh Drishti and wait for Connected before running this plan. No run was submitted.");
      }
    }
    const run = await api("/api/runs", {plan_id: selectedPlan.plan_id, idempotency_key: key});
    submitted = true; $("run").textContent = "Submitted · preview a new plan to fetch again";
    sessionStorage.setItem("margin-last-run", run.run_id);
    await watch(run.run_id);
  } catch (error) { setBusy(false); throw error; }
}
async function direct(operations) {
  const selected = await api("/api/plans", {operations});
  await submitPlan(selected, crypto.randomUUID());
}
function providerData(result) {
  if (result.payload_kind === "rest_json") return result.payload;
  const payload = result.payload || {};
  if (payload.structuredContent || payload.structured_content) return payload.structuredContent || payload.structured_content;
  for (const block of payload.content || []) { try { if (block.type === "text") return JSON.parse(block.text); } catch { /* Inspect payload fallback. */ } }
  return payload;
}
function table(parent, rows, columns) {
  if (!rows.length) { parent.append(node("p", "Valid empty result. No additional page was fetched.", "small")); return; }
  const cols = (columns || [...new Set(rows.flatMap(r => Object.keys(r)))]).slice(0, 9);
  const wrap = node("div", undefined, "table-wrap"); const tab = node("table");
  const head = node("tr"); for (const col of cols) head.append(node("th", col));
  tab.append(head);
  for (const row of rows.slice(0, 20)) { const tr = node("tr"); for (const col of cols) tr.append(node("td", format(row[col]))); tab.append(tr); }
  wrap.append(tab); parent.append(wrap);
  if (rows.length > 20) parent.append(node("p", `Showing 20 of ${rows.length} retained rows; full values remain in the sanitized payload.`, "small"));
}
function chart(parent, rows) {
  const points = rows.filter(r => Number.isFinite(r.close) && typeof r.trade_date === "string").sort((a, b) => a.trade_date.localeCompare(b.trade_date));
  if (!points.length) return;
  const low = Math.min(...points.map(r => r.close)), high = Math.max(...points.map(r => r.close));
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg"); svg.classList.add("price-chart");
  svg.setAttribute("viewBox", "0 0 650 155"); svg.setAttribute("role", "img"); svg.setAttribute("aria-label", "Returned EOD close values, no normalization or return calculation");
  const line = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
  line.setAttribute("points", points.map((r, i) => `${12 + i / Math.max(1, points.length - 1) * 626},${135 - (r.close - low) / (high - low || 1) * 115}`).join(" "));
  svg.append(line); parent.append(svg);
  const note = node("div", undefined, "chart-note"); note.append(node("span", points[0].trade_date), node("span", "Reported close · price scale as supplied"), node("span", points.at(-1).trade_date)); parent.append(note);
}
function metrics(parent, data) {
  const grid = node("div", undefined, "metric-grid");
  for (const [key, value] of Object.entries(data).filter(([, v]) => v === null || ["string", "number", "boolean"].includes(typeof v)).slice(0, 12)) {
    const cell = node("div", undefined, "metric"); cell.append(node("div", key, "label"), node("div", format(value), "value")); grid.append(cell);
  }
  parent.append(grid);
}
function appendResult(result) {
  const card = node("article", undefined, "result-card"); card.dataset.operation = result.operation;
  const heading = node("div", undefined, "result-heading"); heading.append(node("h3", result.operation.split(".")[1].replaceAll("_", " ")), node("span", result.status, "badge subtle"));
  card.append(heading, node("div", `${result.provider} · ${result.mode} · ${result.receipt.retrieved_at} · evidence: provider record / unverified`, "context"));
  if (result.error) card.append(node("p", result.error.message, "notice error"));
  const data = providerData(result);
  if (data) {
    const rows = Array.isArray(data) ? data : data.data;
    if (Array.isArray(rows)) {
      if (result.operation.endsWith("get_stock_prices")) chart(card, rows);
      const events = result.provider === "drishti" && rows.some(r => r.headline || r.earnings_id);
      if (events) for (const row of rows) {
        const event = node("div", undefined, "event-card");
        event.append(node("h4", row.headline || "Provider earnings record"), node("p", [row.symbol, row.quarter, row.published_at || row.date].filter(Boolean).join(" · "), "context"));
        if (row.summary) event.append(node("p", row.summary));
        if (row.sentiment) event.append(node("span", "Provider text tone: " + row.sentiment, "badge subtle"));
        if (row.earnings_id) {
          const button = node("button", "Inspect this earnings record", "quiet record-button");
          button.addEventListener("click", action(() => direct([{operation: "drishti.get_earnings_filing", arguments: {earnings_id: row.earnings_id, detailed: true}}])));
          event.append(button);
        }
        card.append(event);
      } else if (result.operation.endsWith("get_financials")) {
        // Observed REST field names, preserved verbatim; no inferred unit/basis aliases.
        const columns = ["period_end_date", "fiscal_year", "quarter", "period_type", "consolidation_type", "revenue", "net_profit", "eps", "cash_flow_operating"]
          .filter(key => rows.some(row => Object.hasOwn(row, key)));
        table(card, rows, columns.length ? columns : undefined);
      } else table(card, rows);
      if (result.operation.endsWith("search_stocks")) for (const row of rows) {
        const pick = node("button", "Select " + row.symbol + " / " + row.exchange, "quiet");
        pick.addEventListener("click", () => { $("symbol").value = row.symbol; $("exchange").value = row.exchange; $("company-context").textContent = row.company_name + " · " + (row.isin || "ISIN not supplied"); invalidatePlan(); });
        card.append(pick);
      }
    } else if (typeof data === "object") {
      metrics(card, data);
      if (data.latest_price) metrics(card, data.latest_price);
      if (data.consolidated) { card.append(node("p", "Consolidated provider fields (definitions/units as supplied)", "small")); table(card, [data.consolidated]); }
      if (data.company_name) $("company-context").textContent = [data.company_name, data.exchange, data.isin].filter(Boolean).join(" · ");
    }
  }
  const warnings = node("div", undefined, "warning-list"); for (const warning of result.warnings) warnings.append(node("p", warning));
  if (result.warnings.length) card.append(warnings);
  for (const citation of result.citations) {
    const line = node("div", undefined, "source");
    if (citation.requires_resolution || new URL(citation.locator).hostname.endsWith(".invalid")) line.append(node("span", citation.locator + " · " + (citation.requires_resolution ? "requires authorized resolution" : "fictional source locator")));
    else { const link = node("a", citation.locator); link.href = citation.locator; link.target = "_blank"; link.rel = "noopener noreferrer"; line.append(link); }
    line.append(node("span", " · source locator, claim not verified")); card.append(line);
  }
  const details = node("details", undefined, "payload"); details.append(node("summary", "Sanitized provider payload & receipt"), node("pre", JSON.stringify({payload: result.payload, receipt: result.receipt, coverage: result.coverage}, null, 2)));
  card.append(details); $("cards").append(card);
}
async function watch(runId) {
  const generation = ++pollGeneration; activeRun = runId; setBusy(true);
  $("cards").replaceChildren(); $("restore").hidden = true;
  const seen = new Set();
  try {
    for (;;) {
      const run = await api("/api/runs/" + runId);
      if (generation !== pollGeneration) return;
      $("run-status").textContent = run.status; $("trace").replaceChildren();
      for (const operation of run.operations) {
        const row = node("div", undefined, "trace-row");
        row.append(node("code", operation.operation), node("span", operation.status, "state " + operation.status), node("span", operation.receipt ? operation.receipt.elapsed_ms + " ms" : "—", "duration")); $("trace").append(row);
        if (!["queued", "running"].includes(operation.status) && !seen.has(operation.operation_id)) {
          seen.add(operation.operation_id);
          try { appendResult(await api(`/api/runs/${runId}/operations/${operation.operation_id}`)); }
          catch (e) { $("cards").append(node("p", operation.operation + ": " + (operation.error?.message || e.message), "notice")); }
        }
      }
      await refreshStatus();
      if (!["queued", "running"].includes(run.status)) break;
      await new Promise(resolve => setTimeout(resolve, 250));
    }
  } finally { if (generation === pollGeneration) { activeRun = null; setBusy(false); } }
}

$("company-form").addEventListener("submit", action(async () => { const c = company(); await direct([{operation: "bharatstock.get_stock_quote", arguments: {ticker: c.symbol, exchange: c.exchange}}]); }));
$("search-directory").addEventListener("click", action(() => direct([{operation: "bharatstock.search_stocks", arguments: {q: $("symbol").value.trim(), limit: 5}}])));
$("preview").addEventListener("click", action(preview));
$("run").addEventListener("click", action(async () => { if (!plan) throw new Error("Preview a plan first."); await submitPlan(plan, submissionKey); }));
$("cancel").addEventListener("click", action(async () => { if (activeRun) await api(`/api/runs/${activeRun}/cancel`, {}); }));
$("restore").addEventListener("click", action(() => watch(sessionStorage.getItem("margin-last-run"))));
$("connect").addEventListener("click", action(connectDrishti));
for (const id of ["symbol", "exchange", "price-from", "price-to"]) $(id).addEventListener("change", invalidatePlan);

action(async () => {
  await refreshStatus();
  const response = await api("/api/capabilities"); capabilities = new Map(response.operations.map(c => [c.operation, c])); setupModules();
  if (mode === "synthetic") $("symbol").value = "SYNTHA";
  const end = new Date(), start = new Date(end); start.setUTCDate(end.getUTCDate() - 90);
  $("price-to").value = end.toISOString().slice(0, 10); $("price-from").value = start.toISOString().slice(0, 10);
  $("restore").hidden = !sessionStorage.getItem("margin-last-run");
  // Local-only status reads also observe a connection started by another tab.
  setInterval(() => {
    if (!runBusy && !connectionBusy) refreshStatus().catch(() => {
      $("connection-status").textContent = "Cannot reach the local server. Check the terminal before submitting another action.";
    });
  }, 5000);
})()
