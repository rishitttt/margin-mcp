"use strict";

const $ = id => document.getElementById(id);
let nonce = "", mode = "synthetic", capabilities = new Map();
let plan = null, submissionKey = null, submitted = false, activeRun = null, pollGeneration = 0;
let runBusy = false, connectionBusy = false, connectionError = "", metadataSignature = null;
let factsBusy = false, factLoadGeneration = 0, factLoadKey = "", factLoadPromise = null;
let task = "financial", previewBusy = false, draftRevision = 0, planContext = "", selectedCompanyKey = "";
const lockedControls = new Map();
const calculationCatalog = new Map();
const reviewCatalog = new Map();
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
function showError(error) { $("error").textContent = error.message || String(error); $("error").hidden = false; $("error").scrollIntoView?.({block: "center"}); }
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
function invalidatePlan() { draftRevision++; plan = null; submissionKey = null; submitted = false; $("plan").hidden = true; $("run").disabled = true; }
function setTask(next, persist = true) {
  if (runBusy || connectionBusy || previewBusy) return;
  next = ["financial", "retrieve"].includes(next) ? next : "financial";
  task = next; invalidatePlan(); clearError();
  for (const panel of document.querySelectorAll?.("[data-task-panel]") || []) panel.hidden = panel.dataset.taskPanel !== next;
  for (const button of document.querySelectorAll?.("[data-task]") || []) button.setAttribute("aria-pressed", String(button.dataset.task === next));
  if (persist) sessionStorage.setItem("margin-task", next);
  updateTaskContext();
}
function updateTaskContext() {
  const c = company(false);
  $("task-context").textContent = c.symbol ? `${c.symbol} / ${c.exchange} · ${task === "financial" ? "choose a function → preview → run" : "select data → preview → run"}` : "Enter a company ticker on the left to begin.";
}
function setBusy(value) {
  runBusy = value;
  const busy = value || connectionBusy || previewBusy;
  for (const control of document.querySelectorAll?.(".task-panel input,.task-panel select,.task-panel textarea,.task-panel button,#company-form input,#company-form select,#company-form button,[data-task],#run-history") || []) {
    if (busy) { if (!lockedControls.has(control)) lockedControls.set(control, control.disabled); control.disabled = true; }
    else if (lockedControls.has(control)) { control.disabled = lockedControls.get(control); lockedControls.delete(control); }
  }
  for (const id of ["preview", "load-company", "search-directory", "company-preview", "analysis-run"]) $(id).disabled = busy;
  $("connect").disabled = busy;
  $("run").disabled = busy || submitted || !plan;
  $("compare-facts").disabled = busy || factsBusy || !preparedFacts.size;
  $("prepare-source").disabled = busy || factsBusy;
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
  if (nonce && nonce !== status.action_nonce) {
    invalidatePlan(); financialSources.clear(); resetFacts(); renderSources();
    $("result-context").textContent = "The server restarted. Previous in-memory results are unavailable; preview a new run when ready.";
    $("cards").replaceChildren();
  }
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
  const signature = JSON.stringify(status.providers.drishti);
  if (metadataSignature !== null && metadataSignature !== signature && capabilities.size) await refreshProviderCatalog();
  metadataSignature = signature;
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
async function refreshProviderCatalog() {
  const selected = new Map([...document.querySelectorAll("#modules input")].map(input => [input.value, input.checked]));
  const previous = $("retrieval-function").value;
  const response = await api("/api/capabilities");
  capabilities = new Map(response.operations.map(spec => [spec.operation, spec]));
  setupModules();
  for (const input of document.querySelectorAll("#modules input")) input.checked = !input.disabled && (selected.get(input.value) || false);
  setupRetrievalCatalog();
  if (capabilities.has(previous)) { $("retrieval-function").value = previous; showRetrievalContract(); }
  invalidatePlan();
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
    input.checked = id === "snapshot" && !input.disabled;
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
function company(validate = true) {
  const c = {symbol: ($("symbol").value || "").trim().toUpperCase(), exchange: $("exchange").value};
  if (validate && (!/^[A-Z0-9][A-Z0-9&_.-]{0,39}$/.test(c.symbol) || !["NSE", "BSE"].includes(c.exchange))) throw new Error("Enter a valid ticker and exchange before previewing.");
  return c;
}
async function previewRequest(path, body, context) {
  if (runBusy || previewBusy || connectionBusy) return;
  invalidatePlan(); const revision = draftRevision;
  previewBusy = true; setBusy(false);
  try {
    const selected = await api(path, body);
    if (revision !== draftRevision) return;
    showPlan(selected, context);
    $("plan").scrollIntoView?.({behavior: "auto", block: "nearest"});
  } finally { previewBusy = false; setBusy(runBusy); }
}
async function preview() {
  const selected = [...document.querySelectorAll("input[name=module]:checked")].map(el => el.value);
  if (!selected.length) throw new Error("Select at least one data module before previewing.");
  const c = company();
  await previewRequest("/api/plans", {...c, modules: selected, from: $("price-from").value, to: $("price-to").value}, `${c.symbol} / ${c.exchange} · selected data`);
}
function showPlan(selected, context = "Explicit operation plan") {
  plan = selected;
  planContext = context; $("plan-context").textContent = context;
  submissionKey = crypto.randomUUID(); submitted = false;
  $("plan-body").replaceChildren();
  for (const op of plan.operations) {
    $("plan-body").append(node("div", op.operation + (op.execution_kind === "local_calculation" ? " · local calculation" : " · provider request"), "plan-op"));
    const inputs = node("details", undefined, "plan-arguments");
    inputs.append(node("summary", "Inspect planned arguments"), node("pre", JSON.stringify(op.arguments, null, 2)));
    $("plan-body").append(inputs);
  }
  const calls = Object.values(plan.data_operations).reduce((a,b) => a+b, 0);
  $("plan-body").append(node("p", `${calls} provider data operations · ${plan.operations.length - calls} local calculations · ${plan.estimated_credits} estimated Drishti credits`, "plan-total"));
  for (const op of plan.operations.filter(op => op.operation.startsWith("finance.company_"))) {
    const a = op.arguments;
    $("plan-body").append(node("p", `${a.source_run_id ? "Reuse retained" : "Fetch"} ${a.period_type} financials · ${a.basis} · ${a.money_unit || "unknown units"} (auto uses reviewed provider documentation; explicit scales are caller declarations).`, "small"));
  }
  $("run").disabled = false; $("run").textContent = "Run selected operations"; $("plan").hidden = false;
}
async function submitPlan(selectedPlan, key) {
  if (runBusy || submitted) return;
  if (connectionBusy) throw new Error("Wait for Drishti connection checks to finish.");
  setBusy(true);
  try {
    if (mode === "live" && selectedPlan.operations.some(op => op.operation.startsWith("drishti."))) {
      const status = await refreshStatus();
      const info = status.providers.drishti;
      if (info.state !== "connected" || !info.metadata_fresh) {
        $("provider-settings").open = true;
        throw new Error("Drishti is not ready. Click Connect / refresh Drishti and wait for Connected before running this plan. No run was submitted.");
      }
    }
    const run = await api("/api/runs", {plan_id: selectedPlan.plan_id, idempotency_key: key});
    submitted = true; $("run").textContent = "Submitted · preview again for another run";
    $("plan").hidden = true;
    sessionStorage.setItem("margin-last-run", run.run_id);
    $("results-panel").scrollIntoView?.({behavior: "auto", block: "nearest"});
    await watch(run.run_id, planContext);
  } catch (error) { setBusy(false); throw error; }
}
async function direct(operations) {
  await previewRequest("/api/plans", {operations}, operations.map(o => operationLabel(o.operation)).join(" + "));
}
function operationLabel(operation) {
  const labels = {"finance.company_margins":"Net profit margin", "finance.company_cashflow_metrics":"Cash flow and capex", "finance.company_growth":"Period growth", "finance.company_cagr":"Annual endpoint CAGR", "finance.company_ttm":"Trailing twelve months", "finance.calculate_dcf":"DCF · explicit inputs", "finance.compare_periods":"Period comparison", "finance.calculate_margins":"Profit margin", "finance.calculate_cashflow_metrics":"Cash-flow metrics", "bharatstock.get_financials":"Financial statements"};
  return labels[operation] || operation.split(".")[1].replaceAll("_", " ");
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
function metrics(parent, data, labels = {}) {
  const grid = node("div", undefined, "metric-grid");
  for (const [key, value] of Object.entries(data).filter(([, v]) => v === null || ["string", "number", "boolean"].includes(typeof v)).slice(0, 12)) {
    const numeric = typeof value === "number" || (typeof value === "string" && /^-?\d+(\.\d+)?$/.test(value));
    const cell = node("div", undefined, numeric ? "metric" : "metric text-metric"); cell.append(node("div", labels[key] || key, "label"), node("div", format(value), "value")); grid.append(cell);
  }
  parent.append(grid);
}
function earningsArguments(row) {
  const rawId = row.earnings_id ?? row.id;
  if (typeof rawId === "string" && /^[A-Za-z0-9_-]{1,128}$/.test(rawId)) return {earnings_id: rawId, detailed: true};
  if (typeof row.symbol === "string" && /^[A-Za-z0-9][A-Za-z0-9&_.-]{0,39}$/.test(row.symbol)
      && typeof row.quarter === "string" && /^q[1-4]_\d{2}$/.test(row.quarter)) return {symbol: row.symbol, quarter: row.quarter, detailed: true};
  return null;
}
function appendResult(result, runId = null) {
  const card = node("article", undefined, "result-card"); card.dataset.operation = result.operation;
  const heading = node("div", undefined, "result-heading"); heading.append(node("h3", operationLabel(result.operation)), node("span", result.status === "incomplete" ? "Needs more information" : result.status, "badge subtle"));
  card.append(heading, node("div", `${result.provider} · ${result.mode} · ${result.receipt.retrieved_at} · ${result.payload_kind === "analysis" ? "local arithmetic / source inputs unverified" : "evidence: provider record / unverified"}`, "context"));
  if (result.error) card.append(node("p", result.error.message, "notice error"));
  let data = providerData(result);
  if (result.operation === "drishti.get_earnings_filing" && data?.data && !Array.isArray(data.data)) data = data.data;
  if (result.coverage?.field_units) card.append(node("p", "Field units: " + Object.entries(result.coverage.field_units).map(([path, unit]) => path + " = " + unit).join(" · "), "small"));
  if (result.operation === "bharatstock.get_financials") card.append(node("p", "Monetary totals: INR · EPS: INR/share (provider documentation). Definitions and reporting scope still require review.", "small"));
  if (result.payload_kind === "analysis") {
    const output = result.payload || {status: result.status, issues: [result.error?.message || "Calculation unavailable."]};
    renderCalculation(card, output, false);
    showCalculation(output);
  } else if (data) {
    const rows = Array.isArray(data) ? data : data.data;
    if (Array.isArray(rows)) {
      if (result.operation.endsWith("get_stock_prices")) chart(card, rows);
      const events = result.provider === "drishti" && ["drishti.get_news", "drishti.get_announcements", "drishti.list_earnings"].includes(result.operation);
      if (events) for (const row of rows) {
        const event = node("div", undefined, "event-card");
        const title = row.specific_title || row.title || row.headline || (result.operation === "drishti.list_earnings" ? "Provider earnings record" : "Provider event record");
        event.append(node("h4", format(title)), node("p", [row.symbol, row.quarter, row.published_at || row.date].filter(Boolean).map(format).join(" · "), "context"));
        if (row.summary) event.append(node("p", format(row.summary)));
        if (row.sentiment) event.append(node("span", "Provider text tone: " + format(row.sentiment), "badge subtle"));
        if (result.operation === "drishti.list_earnings") {
          const args = earningsArguments(row);
          if (args) {
            const button = node("button", "Inspect this earnings record", "quiet record-button");
            button.addEventListener("click", action(() => direct([{operation: "drishti.get_earnings_filing", arguments: args}])));
            event.append(button);
          } else event.append(node("p", "No usable detail selector returned; inspect the provider payload. No ID or quarter has been guessed.", "small"));
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
        pick.addEventListener("click", () => { $("symbol").value = row.symbol; $("exchange").value = row.exchange; companyChanged(); $("company-context").textContent = row.company_name + " · " + (row.isin || "ISIN not supplied"); });
        card.append(pick);
      }
    } else if (typeof data === "object") {
      metrics(card, data);
      if (data.latest_price) metrics(card, data.latest_price);
      const earnings = data.earnings_table || data;
      for (const basis of ["standalone", "consolidated"]) if (earnings[basis] && typeof earnings[basis] === "object") {
        card.append(node("p", basis + " provider fields (definitions/units as supplied)", "small"));
        table(card, Object.entries(earnings[basis]).map(([field, value]) => ({field, value})), ["field", "value"]);
      }
      const a = result.receipt.arguments || {};
      if (data.company_name && a.ticker === company(false).symbol && a.exchange === company(false).exchange) $("company-context").textContent = [data.company_name, data.exchange, data.isin].filter(Boolean).join(" · ");
    }
  }
  if (runId && result.operation === "bharatstock.get_financials" && ["success", "empty"].includes(result.status)) {
    rememberFinancialSource({run_id: runId, operation_id: result.operation_id, arguments: result.receipt.arguments || result.receipt.selectors, retrieved_at: result.receipt.retrieved_at});
    const prepare = node("button", "Prepare financial facts · local only", "quiet");
    prepare.addEventListener("click", action(async () => {
      $("financial-source").value = runId + ":" + result.operation_id;
      setTask("financial"); $("manual-facts").open = true;
      await prepareSelectedSource();
      $("analysis-panel").scrollIntoView({behavior: "auto", block: "start"});
    }));
    card.append(prepare);
  }
  if (runId && ["drishti.get_news", "drishti.get_announcements", "drishti.list_earnings", "drishti.get_earnings_filing"].includes(result.operation) && result.status === "success") {
    const importButton = node("button", "Import retained text for citation / sentiment · local only", "quiet");
    importButton.addEventListener("click", action(async () => {
      const c = company();
      const output = await api("/api/protocols/import-source", {run_id: runId, operation_id: result.operation_id, issuer: c.exchange + ":" + c.symbol});
      $("review-tester").open = true;
      $("review-result").textContent = JSON.stringify(output, null, 2);
      await loadReviewCatalog();
      $("review-tester").scrollIntoView({block: "start"});
    }));
    card.append(importButton);
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
async function watch(runId, context = "") {
  const generation = ++pollGeneration; activeRun = runId; setBusy(true);
  $("cards").replaceChildren(); $("restore").hidden = true;
  $("analysis-result").textContent = "No calculation output retained for this run.";
  const seen = new Set();
  try {
    for (;;) {
      const run = await api("/api/runs/" + runId);
      if (generation !== pollGeneration) return;
      $("run-status").textContent = run.status; $("trace").replaceChildren();
      if (context) $("result-context").textContent = context;
      for (const operation of run.operations) {
        const row = node("div", undefined, "trace-row");
        row.append(node("code", operation.operation), node("span", operation.status, "state " + operation.status), node("span", operation.receipt ? operation.receipt.elapsed_ms + " ms" : "—", "duration")); $("trace").append(row);
        if (!["queued", "running"].includes(operation.status) && !seen.has(operation.operation_id)) {
          seen.add(operation.operation_id);
          try {
            const result = await api(`/api/runs/${runId}/operations/${operation.operation_id}`);
            appendResult(result, runId);
            if (result.operation === "bharatstock.get_financials" && ["success", "empty"].includes(result.status) && financialSources.get($("financial-source").value)?.operation_id === result.operation_id) {
              try { await prepareSelectedSource(); }
              catch (e) { $("fact-note").textContent = "Could not prepare financial facts: " + e.message; }
            }
          }
          catch (e) { $("cards").append(node("p", operation.operation + ": " + (operation.error?.message || e.message), "notice")); }
        }
      }
      await refreshStatus();
      if (!["queued", "running"].includes(run.status)) break;
      await new Promise(resolve => setTimeout(resolve, 250));
    }
    await refreshHistory(runId);
    await refreshSources();
  } finally { if (generation === pollGeneration) { activeRun = null; setBusy(false); } }
}

async function refreshHistory(selected = "") {
  const response = await api("/api/runs");
  const placeholder = node("option", "Choose a previous run"); placeholder.value = "";
  $("run-history").replaceChildren(placeholder);
  for (const run of response.runs) {
    const scope = run.listing ? run.listing.symbol + " / " + run.listing.exchange : run.operations.some(op => /^(drishti|bharatstock)\./.test(op)) ? "Provider query" : "Explicit inputs";
    const label = `${scope} · ${operationLabel(run.operations.at(-1) || "local.calculation")} · ${run.status}`;
    const option = node("option", label); option.value = run.run_id; option.dataset.context = label;
    $("run-history").append(option);
  }
  if (selected) $("run-history").value = selected;
  return response.runs;
}

const preparedFacts = new Map();
const financialSources = new Map();
function rememberFinancialSource(source) {
  const key = source.run_id + ":" + source.operation_id;
  financialSources.set(key, source);
  renderSources(key);
}
function renderSources(prefer = "") {
  const c = company(false), previous = prefer || $("financial-source").value;
  $("financial-source").replaceChildren();
  const sources = [...financialSources.entries()].filter(([,s]) => s.arguments?.ticker === c.symbol && s.arguments.exchange === c.exchange);
  for (const [key, source] of sources) {
    const a = source.arguments;
    const option = node("option", `${a.ticker} / ${a.exchange} · ${a.period_type} · ${source.retrieved_at}`);
    option.value = key; $("financial-source").append(option);
  }
  if (sources.some(([key]) => key === previous)) $("financial-source").value = previous;
  if (!sources.length) {
    const option = node("option", "No retained financials for this company · preview a financial function first"); option.value = ""; $("financial-source").append(option);
  }
  $("financial-readiness").textContent = `${sources.length ? "Retained financials available; matching periods can be reused." : "No retained financials for this company; the preview can include one request."} Choose Auto for documented units; explicit declarations stay labelled. Missing data remains unavailable.`;
}
async function refreshSources() {
  const response = await api("/api/analysis/sources");
  const previous = $("financial-source").value;
  financialSources.clear();
  for (const source of response.sources) financialSources.set(source.run_id + ":" + source.operation_id, source);
  renderSources(previous);
  if (!$("financial-source").value) resetFacts();
}
function resetFacts() {
  factLoadGeneration++; factLoadPromise = null; factsBusy = false;
  preparedFacts.clear();
  for (const id of ["fact-a", "fact-b"]) { const option = node("option", "No matching financial facts yet"); option.value = ""; $(id).replaceChildren(option); }
  $("fact-a-start").value = ""; $("fact-b-start").value = "";
  $("fact-note").textContent = "Run a financial function or retrieve annual/quarterly financials for the selected company.";
  setBusy(runBusy);
}
function companyChanged() {
  invalidatePlan(); clearError(); updateTaskContext();
  const c = company(false), key = c.symbol + ":" + c.exchange;
  if (key === selectedCompanyKey) return;
  selectedCompanyKey = key;
  sessionStorage.setItem("margin-company", JSON.stringify(c));
  $("company-context").textContent = c.symbol ? `${c.symbol} / ${c.exchange} · requested listing; verify identity in the response.` : "Enter an explicit ticker and exchange.";
  const savedUnit = sessionStorage.getItem("margin-unit:" + key);
  $("company-unit").value = ["auto", "INR", "INR_thousand", "INR_lakh", "INR_crore"].includes(savedUnit) ? savedUnit : "";
  $("cards").replaceChildren(node("p", "No run selected for this company. Preview a task or choose a previous run.", "small"));
  $("result-context").textContent = c.symbol ? `${c.symbol} / ${c.exchange}` : "";
  $("run-status").textContent = "Ready";
  $("analysis-result").textContent = "No calculation selected.";
  $("run-history").value = "";
  resetFacts(); renderSources();
  if ($("financial-source").value) prepareSelectedSource().catch(e => { $("fact-note").textContent = e.message; });
}
async function prepareSelectedSource() {
  const source = financialSources.get($("financial-source").value);
  if (!source) throw new Error("No retained financials. Run Annual or Quarterly financials, or preview a financial function above.");
  const unit = $("company-unit").value;
  const key = source.run_id + ":" + source.operation_id + ":" + unit;
  if (factLoadPromise && factLoadKey === key) return factLoadPromise;
  const generation = ++factLoadGeneration;
  factLoadKey = key; factsBusy = true; setBusy(runBusy);
  factLoadPromise = (async () => {
    try {
      const response = await api(`/api/runs/${source.run_id}/operations/${source.operation_id}/facts` + (unit ? "?money_unit=" + encodeURIComponent(unit) : ""));
      if (generation === factLoadGeneration) loadFacts(response);
    } catch (e) {
      if (generation === factLoadGeneration) loadFacts({status: "incomplete", facts: [], warnings: [e.message]});
      throw e;
    } finally {
      if (generation === factLoadGeneration) { factsBusy = false; factLoadPromise = null; setBusy(runBusy); }
    }
  })();
  return factLoadPromise;
}
function loadFacts(response) {
  const previous = {"fact-a": $("fact-a").value, "fact-b": $("fact-b").value};
  preparedFacts.clear();
  for (const id of ["fact-a", "fact-b"]) { const option = node("option", "Choose a fact"); option.value = ""; $(id).replaceChildren(option); }
  for (const f of response.facts) {
    preparedFacts.set(f.fact_id, f);
    for (const id of ["fact-a", "fact-b"]) {
      const option = node("option", `${f.metric} · ${f.period_end || "unknown period"} · ${f.basis || "basis unknown"} · ${format(f.value)} ${f.unit || "unit unknown"}`);
      option.value = f.fact_id; $(id).append(option);
    }
  }
  for (const id of ["fact-a", "fact-b"]) if (preparedFacts.has(previous[id])) $(id).value = previous[id];
  if (!preparedFacts.has(previous["fact-a"])) $("fact-a-start").value = "";
  if (!preparedFacts.has(previous["fact-b"])) $("fact-b-start").value = "";
  $("fact-note").textContent = `${response.facts.length} facts from the selected retained result. Unit selections and entered start dates are caller declarations, not independent verification.`;
  suggestFacts();
}
function selectedFact(id) {
  const f = preparedFacts.get($(id).value);
  if (!f) throw new Error("Prepare a retained financial result and select both facts first.");
  const copy = JSON.parse(JSON.stringify(f)), start = $(id + "-start").value;
  if (start) { copy.period_start = start; copy.source.caller_declared_period_start = start; }
  return copy;
}
function suggestFacts(reset = false) {
  const fn = $("pair-function").value;
  $("fact-a-label").textContent = fn === "finance.compare_periods" ? "A · previous period" : fn === "finance.calculate_margins" ? "A · profit measure" : "A · operating cash flow";
  $("fact-b-label").textContent = fn === "finance.compare_periods" ? "B · current period" : fn === "finance.calculate_margins" ? "B · revenue" : "B · capex";
  if (!reset && $("fact-a").value && $("fact-b").value) return;
  const facts = [...preparedFacts.values()].filter(f => f.value !== null && f.period_end);
  const latest = facts.map(f => f.period_end).sort().at(-1);
  let a, b;
  if (fn === "finance.compare_periods") {
    const revenues = facts.filter(f => f.metric === "revenue").sort((a,b) => a.period_end.localeCompare(b.period_end));
    b = revenues.at(-1); a = revenues.filter(f => f.basis === b?.basis && f.period_end < b.period_end).at(-1);
  } else {
    a = fn === "finance.calculate_margins" ? facts.find(f => f.metric === "profit_from_continuing_operations" && f.value !== null && f.period_end === latest) || facts.find(f => f.metric === "net_profit" && f.period_end === latest) : facts.find(f => f.metric === "cash_flow_operating" && f.period_end === latest);
    b = facts.find(f => f.metric === (fn === "finance.calculate_margins" ? "revenue" : "capex") && f.period_end === a?.period_end && f.basis === a?.basis);
  }
  $("fact-a").value = a?.fact_id || ""; $("fact-b").value = b?.fact_id || "";
}
function showCalculation(result) {
  $("analysis-result").textContent = JSON.stringify(result, null, 2);
  $("analysis-status").textContent = result.status;
  const parent = $("analysis-values"); parent.replaceChildren();
  renderCalculation(parent, result);
}
function renderCalculation(parent, result, includeWarnings = true) {
  if (!result) return;
  if (result.report?.version === "margin.dcf_report.v1") {
    parent.append(node("p", result.report.title, "context"));
    table(parent, result.report.rows, ["label", "display", "unit", "status"]);
    parent.append(node("p", "Input origin: " + result.report.input_origin, "small"));
    if (includeWarnings) for (const warning of result.report.warnings || []) parent.append(node("p", warning, "small"));
    return;
  }

  if (result.selection) {
    const s = result.selection, dates = Array.isArray(result.inputs) ? [...new Set(result.inputs.map(f => f.period_end).filter(Boolean))].sort().join(" → ") : "";
    parent.append(node("p", [s.ticker + " / " + s.exchange, s.basis, s.period_type, dates, s.money_unit === "auto" ? "documented provider units" : s.money_unit ? s.money_unit + " · caller-declared scale" : "units unknown"].filter(Boolean).join(" · "), "context"));
  }
  for (const issue of result.issues || []) parent.append(node("p", issue, "notice"));
  if (result.status === "incomplete") parent.append(node("p", "Review the missing inputs above and preview a corrected calculation. No automatic retry or extra page was requested.", "small"));
  if (result.values) {
    const scalar = Object.fromEntries(Object.entries(result.values).filter(([key, value]) => !["formula", "terminal_formula", "discount_convention", "equity_bridge"].includes(key) && (value === null || typeof value !== "object"))
      .map(([key, value]) => [key, typeof value === "string" && /^-?\d+(\.\d+)?$/.test(value) && Math.abs(Number(value)) <= Number.MAX_SAFE_INTEGER ? Number(value) : value]));
    metrics(parent, scalar, {margin_percent:"Margin (%)", cfo_minus_capex:"Operating cash flow minus capex", capex_coverage:"Capex coverage (×)", percentage_change:"Change (%)", absolute_change:"Absolute change", cagr_percent:"CAGR (%)", enterprise_value:"Enterprise value", equity_value:"Equity value", value_per_share_inr:"Value per share (INR)"});
    if (Array.isArray(result.values.forecast)) table(parent, result.values.forecast, ["year", "fcff", "discount_factor", "present_value"]);
    if (result.values.calculation_readiness) {
      table(parent, Object.entries(result.values.calculation_readiness).map(([functionName, check]) => ({function:functionName, status:check.status, issues:check.issues || [], components:check.components || {}})), ["function", "status", "issues", "components"]);
      parent.append(node("p", "Valuation: " + JSON.stringify(result.values.valuation_readiness), "small"));
    }
  } else if (result.facts) table(parent, result.facts, ["metric", "value", "unit", "period_end", "basis"]);
  else if (result.fact) table(parent, [result.fact], ["metric", "value", "unit", "period_end", "basis"]);
  if (result.components) table(parent, Object.entries(result.components).map(([metric, check]) => ({metric, status:check.status, unit:check.unit, missing:check.issue || [...(check.missing_fields || []), ...(check.requires_positive || [])], formula:check.formula})), ["metric", "status", "unit", "missing", "formula"]);
  if (includeWarnings) for (const warning of result.warnings || []) parent.append(node("p", warning, "small"));
}
async function calculateLocal(fn, args) {
  await direct([{operation: fn, arguments: args}]);
}
$("company-preview").addEventListener("click", action(async () => {
  const c = company();
  if (!$("company-unit").value) { $("company-unit").focus(); throw new Error("Choose the monetary scale before previewing a calculation. No provider request has been made. Use Retrieve data if you only want to inspect the source first."); }
  await previewRequest("/api/analysis/plans", {function: $("company-function").value, ticker: c.symbol, exchange: c.exchange,
    period_type: $("company-period").value, basis: $("company-basis").value, metric: $("company-metric").value,
    money_unit: $("company-unit").value || null, fetch_missing: $("company-fetch").checked}, `${c.symbol} / ${c.exchange} · ${operationLabel($("company-function").value)}`);
}));
$("prepare-source").addEventListener("click", action(prepareSelectedSource));
$("financial-source").addEventListener("change", action(prepareSelectedSource));
$("company-unit").addEventListener("change", action(async () => {
  invalidatePlan(); sessionStorage.setItem("margin-unit:" + selectedCompanyKey, $("company-unit").value);
  if ($("financial-source").value) await prepareSelectedSource();
}));
$("company-function").addEventListener("change", () => {
  configureFunction(); invalidatePlan();
});
function configureFunction() {
  const fn = $("company-function").value;
  if (fn.endsWith("_ttm")) $("company-period").value = "quarterly";
  if (fn.endsWith("_cagr")) $("company-period").value = "annual";
  $("company-period").disabled = fn.endsWith("_ttm") || fn.endsWith("_cagr");
  const metric = fn.endsWith("_ttm") || fn.endsWith("_cagr") || fn.endsWith("_growth");
  $("company-metric").disabled = !metric;
}
for (const id of ["company-period", "company-basis", "company-metric", "company-fetch"]) $(id).addEventListener("change", invalidatePlan);
$("pair-function").addEventListener("change", () => { suggestFacts(true); invalidatePlan(); });
for (const id of ["fact-a", "fact-b", "fact-a-start", "fact-b-start"]) $(id).addEventListener("change", invalidatePlan);
$("compare-facts").addEventListener("click", action(async () => {
  if (!$("company-unit").value) throw new Error("Choose the monetary scale above before calculating selected facts.");
  const a = selectedFact("fact-a"), b = selectedFact("fact-b"), fn = $("pair-function").value;
  const args = fn === "finance.compare_periods" ? {previous: a, current: b}
    : fn === "finance.calculate_margins" ? {profit: a, revenue: b} : {cfo: a, capex: b};
  $("analysis-arguments").value = JSON.stringify(args, null, 2);
  await calculateLocal(fn, args);
}));
function showCalculationContract() {
  const spec = calculationCatalog.get($("analysis-function").value);
  $("analysis-schema").textContent = spec ? JSON.stringify(spec.schema, null, 2) : "Choose a function to inspect its inputs.";
  $("analysis-function-note").textContent = spec ? `Version ${spec.function_version} · local arithmetic · 0 provider calls. ${spec.note}` : "";
}
async function loadCalculationCatalog() {
  const previous = $("analysis-function").value;
  const response = await api("/api/analysis/functions");
  calculationCatalog.clear();
  const placeholder = node("option", "Choose a function"); placeholder.value = "";
  $("analysis-function").replaceChildren(placeholder);
  for (const spec of response.functions) {
    calculationCatalog.set(spec.function, spec);
    const option = node("option", spec.function); option.value = spec.function; $("analysis-function").append(option);
  }
  if (calculationCatalog.has(previous)) $("analysis-function").value = previous;
  showCalculationContract();
}
async function loadReviewCatalog() {
  const result = await api("/api/protocols");
  reviewCatalog.clear();
  const placeholder = node("option", "Choose a review function"); placeholder.value = "";
  $("review-function").replaceChildren(placeholder);
  for (const spec of result.functions) {
    reviewCatalog.set(spec.function, spec);
    const option = node("option", spec.function); option.value = spec.function; $("review-function").append(option);
  }
}
$("review-catalog").addEventListener("click", action(loadReviewCatalog));
$("review-function").addEventListener("change", () => {
  const spec = reviewCatalog.get($("review-function").value);
  $("review-schema").textContent = spec ? JSON.stringify(spec.schema, null, 2) : "Choose a function.";
});
$("review-starter").addEventListener("click", action(() => {
  const spec = reviewCatalog.get($("review-function").value);
  if (!spec) throw new Error("Choose a review function first.");
  $("review-arguments").value = JSON.stringify(starterArguments(spec.schema), null, 2);
}));
$("review-run").addEventListener("click", action(async () => {
  const functionName = $("review-function").value;
  if (!reviewCatalog.has(functionName)) throw new Error("Choose a review function first.");
  $("review-run").disabled = true;
  try {
    const output = await api("/api/protocols/invoke", {function: functionName, arguments: JSON.parse($("review-arguments").value)});
    $("review-result").textContent = JSON.stringify(output, null, 2);
  } finally { $("review-run").disabled = false; }
}));
$("analysis-catalog").addEventListener("click", action(async () => { invalidatePlan(); await loadCalculationCatalog(); }));
$("analysis-function").addEventListener("change", () => { invalidatePlan(); showCalculationContract(); });
function setupRetrievalCatalog() {
  const placeholder = node("option", "Choose an operation"); placeholder.value = "";
  $("retrieval-function").replaceChildren(placeholder);
  for (const spec of capabilities.values()) {
    const option = node("option", spec.operation + (spec.enabled ? "" : " · held"));
    option.value = spec.operation; $("retrieval-function").append(option);
  }
  showRetrievalContract();
}
function showRetrievalContract() {
  const spec = capabilities.get($("retrieval-function").value);
  $("retrieval-schema").textContent = spec ? JSON.stringify(spec.schema, null, 2) : "Choose an operation to inspect its inputs.";
  $("retrieval-function-note").textContent = spec ? `${spec.provider} · ${spec.published_estimated_credits} estimated Drishti credits · ${spec.enabled ? "Enabled for explicit testing" : spec.held_reason}. JSON arguments below are the request selectors.` : "";
  $("retrieval-run").disabled = runBusy || previewBusy || connectionBusy || !spec?.enabled;
  $("retrieval-starter").disabled = runBusy || previewBusy || connectionBusy || !spec;
}
// A schema skeleton, not a data/forecast generator. Blank selectors need user input.
function starterArguments(schema, root = schema, key = "") {
  if (schema.$ref) {
    const resolved = schema.$ref.split("/").slice(1).reduce((value, part) => value?.[part], root);
    return resolved ? starterArguments(resolved, root, key) : null;
  }
  if (schema.anyOf || schema.oneOf) return starterArguments((schema.anyOf || schema.oneOf).find(s => s.type !== "null") || {}, root, key);
  const c = company(false);
  if (["ticker", "symbol"].includes(key)) return c.symbol;
  if (key === "exchange") return c.exchange;
  if (key === "q") return c.symbol;
  if (schema.enum) return schema.enum[0];
  if (schema.type === "object" || schema.properties) return Object.fromEntries((schema.required || []).map(name => [name, starterArguments(schema.properties?.[name] || {}, root, name)]));
  if (schema.type === "array") return Array.from({length: Math.min(schema.minItems || 1, 4)}, () => starterArguments(schema.items || {}, root, key === "symbols" ? "symbol" : ""));
  if (schema.type === "boolean") return false;
  if (["integer", "number"].includes(schema.type)) return Math.max(schema.minimum || 0, 1);
  if (key === "from") return $("price-from").value;
  if (key === "to") return $("price-to").value;
  return "";
}
$("retrieval-function").addEventListener("change", () => { invalidatePlan(); showRetrievalContract(); });
$("retrieval-starter").addEventListener("click", action(() => {
  const spec = capabilities.get($("retrieval-function").value);
  if (!spec) throw new Error("Choose a retrieval operation first.");
  invalidatePlan();
  $("retrieval-arguments").value = JSON.stringify(starterArguments(spec.schema), null, 2);
  $("retrieval-function-note").textContent += " Starter loaded: complete blank fields and review the contract before previewing.";
}));
$("retrieval-run").addEventListener("click", action(async () => {
  const spec = capabilities.get($("retrieval-function").value);
  if (!spec?.enabled) throw new Error(spec?.held_reason || "Choose an enabled retrieval operation first.");
  await direct([{operation: spec.operation, arguments: JSON.parse($("retrieval-arguments").value)}]);
}));
$("analysis-run").addEventListener("click", action(async () => {
  if (!$("analysis-function").value) throw new Error("Choose a local calculation first.");
  await calculateLocal($("analysis-function").value, JSON.parse($("analysis-arguments").value));
}));

$("company-form").addEventListener("submit", action(async () => { const c = company(); await direct([{operation: "bharatstock.get_stock_quote", arguments: {ticker: c.symbol, exchange: c.exchange}}]); }));
$("search-directory").addEventListener("click", action(() => direct([{operation: "bharatstock.search_stocks", arguments: {q: $("symbol").value.trim(), limit: 5}}])));
$("preview").addEventListener("click", action(preview));
$("run").addEventListener("click", action(async () => { if (!plan) throw new Error("Preview a plan first."); await submitPlan(plan, submissionKey); }));
$("cancel").addEventListener("click", action(async () => { if (activeRun) await api(`/api/runs/${activeRun}/cancel`, {}); }));
$("restore").addEventListener("click", action(() => watch(sessionStorage.getItem("margin-last-run"))));
$("run-history").addEventListener("change", action(async () => {
  const id = $("run-history").value;
  if (id) { invalidatePlan(); sessionStorage.setItem("margin-last-run", id); await watch(id, $("run-history").selectedOptions[0]?.dataset.context || "Retained run"); }
}));
$("connect").addEventListener("click", action(connectDrishti));
for (const id of ["symbol", "exchange"]) {
  $(id).addEventListener("input", companyChanged); $(id).addEventListener("change", companyChanged);
}
for (const id of ["price-from", "price-to"]) $(id).addEventListener("change", invalidatePlan);
for (const button of document.querySelectorAll?.("[data-task]") || []) button.addEventListener("click", () => setTask(button.dataset.task));
for (const element of document.querySelectorAll?.("#analysis-arguments,#analysis-function,#retrieval-arguments,#retrieval-function") || []) element.addEventListener("input", invalidatePlan);

action(async () => {
  await refreshStatus();
  const response = await api("/api/capabilities"); capabilities = new Map(response.operations.map(c => [c.operation, c])); setupModules();
  setupRetrievalCatalog(); await loadCalculationCatalog();
  let saved = null;
  try { saved = JSON.parse(sessionStorage.getItem("margin-company")); } catch { /* Invalid local preference is ignored. */ }
  if (saved && typeof saved.symbol === "string" && ["NSE", "BSE"].includes(saved.exchange)) { $("symbol").value = saved.symbol; $("exchange").value = saved.exchange; }
  else if (mode === "synthetic") $("symbol").value = "SYNTHA";
  selectedCompanyKey = company(false).symbol + ":" + company(false).exchange;
  const savedUnit = sessionStorage.getItem("margin-unit:" + selectedCompanyKey);
  if (["auto", "INR", "INR_thousand", "INR_lakh", "INR_crore"].includes(savedUnit)) $("company-unit").value = savedUnit;
  configureFunction();
  const savedTask = sessionStorage.getItem("margin-task");
  setTask(["retrieve", "financial"].includes(savedTask) ? savedTask : "financial", false);
  const end = new Date(), start = new Date(end); start.setUTCDate(end.getUTCDate() - 90);
  $("price-to").value = end.toISOString().slice(0, 10); $("price-from").value = start.toISOString().slice(0, 10);
  $("restore").hidden = !sessionStorage.getItem("margin-last-run");
  await refreshSources(); const history = await refreshHistory();
  if ($("financial-source").value) {
    try { await prepareSelectedSource(); } catch (e) { $("fact-note").textContent = e.message; }
  }
  const last = sessionStorage.getItem("margin-last-run");
  const lastRecord = history.find(r => r.run_id === last);
  if (lastRecord && (!lastRecord.listing || (lastRecord.listing.symbol === company(false).symbol && lastRecord.listing.exchange === company(false).exchange))) {
    const label = [...$("run-history").options].find(o => o.value === last).dataset.context;
    await watch(last, label);
  }
  document.body.dataset.ready = "true";
  // Local-only status reads also observe a connection started by another tab.
  setInterval(() => {
    if (!runBusy && !connectionBusy) refreshStatus().catch(() => {
      $("connection-status").textContent = "Cannot reach the local server. Check the terminal before submitting another action.";
    });
  }, 5000);
})()
