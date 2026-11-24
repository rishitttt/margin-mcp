# Live two-ticker skill pilot

**25 November publication boundary:** evaluator numerical answers are loaded from an ignored private JSON file, not embedded in the builder. `research/evaluation/build.py --gold-file PATH` must receive the separately reviewed key (local default: `reports/private/evaluation/gold-inputs-2026-11-16.json`). Missing/mismatched keys fail before package creation. Source/task code may be pushed; evaluator inputs and generated private archives remain excluded. Old runner/evaluator ZIPs stay frozen.

The optional `research/evaluation/` tooling builds separate runner and evaluator ZIPs. It
is not a product dependency or an MCP server. The fixed v1 task set has 16 tasks covering
RELIANCE/TCS identity, annual/quarterly financial retrieval, margins, growth/CAGR, cash-flow
metrics, market data, events, missing-data/context checks and retained-source reuse. FCFF,
DCF, sensitivity and scenarios are excluded. Each agent makes fresh live calls; no captured
preparation dataset or evaluator answer key is shipped to the runner.

## Build and run

From the repo root with the development environment installed:

```sh
.venv/bin/python -m research.evaluation.build --output-dir reports/private/packages/new-live-test-copy
```

The destination must be new. Build performs no provider calls. It packages the supplied
trial keys only into the ignored runner's `private/providers.env`, as explicitly authorized
for private local testing. The separate evaluator contains no keys. Do not publish these
archives or put evaluator files within the tested agent's accessible workspace.

Extract the runner outside the development repository and follow **START_HERE.md**. Setup
creates a recorded session, installs the included wheel, and copies a skill into the fresh
workspace. The operator starts one shared live backend with B10/D40 HTTP/10 estimated-credit
allowances and the reviewed-operation flags given in that guide. The fresh agent reads
TASK.md, fills answers.json/report.md, records the final JSON with finish and exports a
sanitized submission.zip with `margin_local.py submit`. Send only that submission for eval.
All extracted copies share real account quotas; process limits are not account-wide caps.

## Visible explanations

Every ordinary helper call should supply `--why "one brief tool-choice explanation"` before
the subcommand. The CLI validates a nonempty, single-line summary up to 280 characters,
prints it to stderr, includes it in JSON and records it before dispatch when configured.
A pre-dispatch logging failure stops the call. Notes remain available for observations.
These are agent-authored visible summaries, not hidden reasoning, full host transcripts or
proof of faithful reasoning. The source and installed Margin skill both describe this.

## Evaluator limits

The private evaluator includes source-backed annual financial targets, independent Decimal
calculations, source URLs/page pins and a RIL source PDF. TCS's primary PDF was parsed via
web research; direct local download returned 403. Independent human financial approval is
pending and declared in gold.json. The stdlib-only grade.py checks selected numeric fields,
periods/units/basis, supplied evidence references, live-mode/budget signals and tool coverage.
News relevance, source support, failure attribution and definitions require manual review.
The automatic percentage is not an overall scientific score. Hashes detect changes since
export; they do not authenticate a local agent's events. Separate ZIPs are not filesystem
isolation; for strong isolation mount only the runner into the tested host.

Preparation found quarterly starts/CFO missing (TTM/cash flow must not invent them), an
announcement schema hold, an empty historical earnings list, and a TCS capex-definition
difference. Current-run price/capex receipt arithmetic is scored separately from independent
issuer truth. The evaluator documents these without leaking them into task-specific hints.

16 November preparation: four successful B financial calls; 23 D SDK HTTP attempts plus
eight direct diagnostics (two mistakenly used the frontend origin); five successful/empty
D data operations and one pre-dispatch announcement block. Estimated D credits 5; observed
balance 961→958. Do not infer current remaining account quotas from that snapshot.

Validation: 126 offline tests; Ruff check/format; relocated portable synthetic process
acceptance with visible --why logging, recorded final JSON, sanitized submission export and
offline reading. Process acceptance used an existing interpreter (`--skip-install`) and no
live provider calls; a clean dependency download on every host remains unverified. The first returned live agent run was evaluated on 16 November: 38/38 automatic checks, valid schema/hashes, 79 tool observations with linked one-line summaries, and B10/D11 HTTP attempts with five estimated credits. Manual review found correct arithmetic/missing-data handling, one recovered oversized preview, and announcement catalog/metadata disagreement. Four company wrappers and successful TTM/earnings-detail remain untested. Private detailed results are under reports/private/eval-results/2026-11-16-run-01/. A single run is not a validated scientific score. Private artifacts are local only, not committed/pushed.
