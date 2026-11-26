# Margin MCP adapter architecture and implementation plan

## 0.9.4 finance surface and preview clarity plan: 27 November 2026

User authorizes implementing the remaining simplification and related repairs, then
testing. Actual 0.9.3 autonomous and guided traces show competing legacy/fresh routes
and final summaries that ignore correct preview bindings. Catalog investigation finds
company mcp_execution still points to legacy planning, contrary to the preferred fresh
route. Fix that default, retaining explicit legacy_mcp_execution/planning_schema and
unchanged callable tools. Unknown-function recovery must use the same preferred route.

Add an optional finance frontend profile with four tools: status, scoped catalog,
company_finance and explicit-input calculate. No legacy preview/run/source/review/event
tools compete in this view. Profile catalog exposes only company/calculation functions
and only executable routes; selected schemas match actual callable inputs. It is a
frontend projection, not authorization or a budget reset; full/review/simple remain.
Use short finance-specific initialization instructions and truthful profile status.

Add transport-neutral preview summary fields separating inputs missing for preview
from inputs missing for execution, preview requests zero from potential execution B1/D0,
and completed preview from authorization to execute. MCP supplies the next tool and a
deterministic copyable summary. Finance view removes duplicate contract/legacy metadata
and unrelated envelope IDs from previews, retaining canonical binding/flags/warnings.
Canonical report rows and raw audit details on executions remain intact.

Repair legacy source_required recovery: distinguish that selected retained route from
fresh no-data preview, never demand a fetch to preview. Clarify local budget blocks
versus unknown account balance; no reset/purchase recommendation. Preserve guards,
strict schemas, keys/replay/units/math and original logs. Do not auto-execute or invent
permission from a preview; host task compliance remains an evaluation target.

Test scoped schemas/routes/hidden calls, source-required recovery, summary/binding
agreement across all nine functions and key/no-key cases, zero-key/zero-allowance
previews, blocked execution/replay, no-data/partial reports, and shared-owner projection
without state changes. Run full pytest/Ruff, official SDK (including finance zero-
budget and fixture execution/shared tests), saved-real HUL replay, immutable 0.9.4 wheel
scan/installed SDK. Actual provider calls remain zero. Active user 0.9.3 is untouched.
Provide manual version-matched B0/D0 setup and goal-only tasks with recorded calls and
final prose; separate changed-profile condition from prior full-profile failures.
No model acceptance is inferred from software checks. Paid trials need new allocation.

## 0.9.3 evaluated finance handoff/readiness repair plan: 27 November 2026

**Implemented after plan eb6dbaf.** 575 offline tests/source and installed-wheel SDK
checks and saved-real handoff replay pass without new provider/model calls; active 0.9.2 untouched. See
[implementation](../implementation.md) and [zero-budget tests](../mcp.md#finance-handoffs-and-readiness-093).
The evaluated plan below remains the design record.

User explicitly asks to evaluate/implement the remaining fixes. Source evidence:
0.9.2 HUL convenience previews caused two invented generic plan references before
recovery; autonomous readiness stopped at three separate previews; forced readiness
succeeded but prose confused coverage/authenticity/empty rows/replay. B3/D0 model
allowance is exhausted. Preserve frozen initial and guided conditions; no new real
provider/model call, active upgrade, restart or budget refill during implementation.

Add transport-neutral next_steps to fresh-company previews: canonical valid financial
inputs, execute=true, preserved caller key/projection/wait options, explicit required
key when absent, authorization still required and no created plan_id. MCP annotates
that step with the actual same tool and top-level schema, excluding margin_run. No
new ID, nonce, plan store, automatic call or key mint. Preserve numeric/guard behavior.

Separate unretained plan IDs (plan_unavailable) from retained but timed-out plans
(plan_expired). Financial plan-error guidance names the two real generic previews
versus the non-plan convenience route. Keep legacy routes and valid plan replay.

Clarify readiness goal selection for multiple metric groups, cash-conversion ratios
versus cycle days, the limited inventory-adjusted liquidity ratio, literal financial
labels, and explicit-input DCF's calculator route. Add report readiness scope metadata:
eligibility/completeness of mapped fields is not source verification; empty numeric
rows are intentional; no-data assessment remains incomplete/not_assessed. Finished
request lifecycle metadata distinguishes same-key replay from new work/fresh data.
All host guidance remains advisory; no LLM or claim that final prose is enforced.

Test nine executable preview bindings and caller-key/no-key projections, no hidden
fetch/state creation, no extra data on replay, unknown/expired plan distinctions,
no-data readiness and unverified-scope consistency, strict schemas and unchanged
review handoffs. Run full offline/Ruff plus source/isolated installed-wheel SDK checks
and saved-real-response replay. Publish immutable0.9.3 wheel and migration/test docs;
active 0.9.2 untouched. First post-upgrade model checks should be zero-request previews
with configured key and B0/D0; fresh live allowance must be explicitly allocated later.

## 0.9.2 execution-contract and live acceptance plan: 27 November 2026

**Implemented after plan 13ca0a4:** 558 offline tests and source SDK checks pass. No
real provider/model call. Manual key-enabled B3/D0 setup and three goal-only tasks
are ready; active 0.9.1 remains untouched. See implementation for evidence/limits.

The user requests completing/testing the finance flow and reports57 BharatStock
requests remaining (correcting3). Reserve the first model batch at3 requests; do not
spend any on operator probes. Active0.9.1 remains unchanged until manual setup.

Observed0.9.1 discovery selects the right function but still omits provider bounds,
execute/idempotency/allowance rules and speculates about Drishti. Add a compact shared
company execution contract from the actual fresh-finance implementation: BharatStock
only, preview0, new execution max B1/D0, zero Drishti credits, execute=true/stable key/
loaded key/remaining allowance, no session_id input, bounded pages and output locations.
Expose it in company catalog and previews, with small per-function provider/bound/ref
fields; preserve existing routes and put exact selected-schema advice in tools. Do
not change finance math, auth/budget/idempotency enforcement or profile/tool counts.
No server LLM, source verification, hidden fetching or broad schema API break.

Test contract/implementation consistency, deep-copy isolation, no-call catalog discovery,
preview bounds and unchanged guards; run regression and source/installed SDK checks.
No real provider/model calls during this build. Publish a new immutable0.9.2 wheel,
manual key-enabled backend setup capped B3/D0 and three goal-only model tasks (INFY
annual growth, HUL margin, INFY readiness). Fresh chat per task, same shared owner,
actual model/context/preset/profile recorded, exact reports/caller failures retained
privately. Score planning separately from numerical/period/unit/source fidelity. New
live tests must preserve all first attempts and must not reset allowance to recover.

## 0.9.1 no-fabrication guidance plan: 27 November 2026

**Implemented after plan 1d0c925; broader user-requested fixes included.** 544 offline
tests and source SDK checks pass; saved real HUL replay covers all nine company
functions (seven success/two correct partial scope holds), no new API call. See
[implementation](../implementation.md) for findings and limits. Active 0.9.0 unchanged.

The full-profile autonomous discovery trial failed: Qwen selected annual TTM instead
of growth, then invented revenue/date in malformed calculator JSON. Two backend calls,
one valid guarded error and one host parse failure; no provider data call. Actual
reported prompt17,611/generated496 versus configured30,183 does not establish overflow.
Preserve the first attempt privately, including caller-only failures, not hidden thought.

User explicitly requires the MCP to tell models not to fabricate. Add concise shared
instructions, status/catalog data_policy and recovery guidance to financial errors:
only actual tool-returned or explicit user inputs; hypothetical inputs only when the
user requests an example and labels/context stay hypothetical; no invented facts/dates
or numeric workaround after a held/invalid call. Discovery-only means no financial
answer. Put company-first routing and growth-vs-TTM semantics near the top, with exact
company function meanings generated from existing definitions. Ask for one schema,
not all calculator schemas. Keep explicit-input math usable for real supplied inputs.

This is an advisory host protocol, not source authentication or a guarantee that models
comply. Do not block arbitrary numbers, infer provenance from model brand/why, run a
server LLM, weaken math/period/unit guards or change any function/route/profile counts.
A focused company profile remains a possible later experiment; do not claim one added.

The user additionally requests a broader failure audit before testing. Reproduce
catalog/default disagreements (especially TTM), impossible stock-to-TTM inputs that
could waste a fetch, and one-year CAGR consistency against ordinary annual growth.
Fix demonstrated issues, express known period constraints in schemas, and add adverse
cases across all retrieval/calculation/company routes. Preserve valid hypotheses,
units, quote/hash guards and distinction between software fixtures and actual source
validation. Do not turn schema/help changes into guaranteed model semantic correctness.

Test identical policy across initialization profiles/status/catalog, safe error recovery,
explicit-user hypothetical math, annual-TTM refusal/no network, schema source and route
compatibility. Run offline regression plus official-SDK source/isolated-wheel checks,
replay already returned real inputs without API calls, release a new immutable0.9.1
wheel and document manual upgrade. Leave active0.9.0 installation/config/budgets alone;
no more live requests are authorized. Model success requires a fresh post-upgrade trial.

## 0.9.0 review-flow repair plan: 26 November 2026

**Implemented after plan commit 9e43879.** 470 offline tests plus source/installed-wheel
SDK checks pass; see [implementation](../implementation.md) and
[manual install/test](../mcp.md#two-step-review-090). Active 0.8.2 remains untouched;
real model acceptance is pending. The evaluated plan below remains the design record.

User explicitly requests fixing the failures, skipping the demo. The preset reached
Qwen, but it passed URLs/passage IDs as handles, discarded the known record date,
selected inventory-only and claimed completion without assessments. Keep the original
conditions/captures; do not solve these by weakening reference/quote/unit guards.

### Selected implementation

Add two core functions with generated typed MCP tools: review.prepare /
margin_prepare_review and review.submit / margin_submit_review. Preparation accepts
one supplied text, issuer/title/URL, explicit record/publication dates, ordered claim
texts and optional sentiment scope. Margin registers the passage, assigns claim/source
IDs and creates the existing immutable citation/sentiment packets internally. Return
one opaque review_id, source text/declared dates, assessment targets and a bound next
step. No source/passage/packet IDs, hashes or host_profile bookkeeping in model input.

Submission takes that review_id, reviewer, ordered claim verdicts/exact quote strings/
rationales and the optional sentiment annotation. Bind real child references internally;
reuse the existing submission/quote/hash/issuer/date/aggregation/audit guards. Produce
one compact report with input context, all verdict rows, support-audit status separately
from assessment coverage, sentiment counts/balance and unverified-source limitations.
Semantics remain host-supplied; Margin runs no LLM or browser.

Store review sessions in the same bounded transient TTL/capacity policy, not a database.
Preparation and submission are atomic across all review stores. Identical replay is
idempotent; changed submissions conflict. No partial accepted citation when sentiment
fails, no session lifetime extension and no hidden refetch. Validate the complete
submission and preserve underlying frozen child packets/hashes.

Keep all old functions and profiles. Full surface becomes 37 tools, advanced review
16, and optional review-simple exposes only status/prepare/submit (three). Exclude raw
registration/numeric/capability toggles from this frontend view; it is still not an
authorization boundary. Scoped instructions demand actual user input, registered text,
returned review_id and actual final reports. Error messages distinguish malformed URLs/
claim IDs from issued handles; do not diagnose expiry for a never-issued identifier.

### Dates, trust and honest limits

Represent record_date and publication_date explicitly in the prepared context. Require
the date selected for sentiment scope and reject unknown/missing selected dates before
creating state; preserve unknown publication, never mark record date as publication.
Submission order/count must match prepared claims. Missing fields fail before state;
the host must ask the user rather than generate sample material. A model can still
fabricate a syntactically valid task/source; the server cannot authenticate that origin
without a trusted input channel. Do not claim missing-input honesty or final prose is
guaranteed. No final-answer interception or independent source verifier is added.

### Validation and release

Test the logged URL-as-ID/date-loss/capability-toggle cases through the new contracts,
partial or extra submissions, forged quotes, wrong/expired sessions, immutable replay,
capacity rollback, safe sanitization, unsupported dates, ambiguous provenance and
complete-but-insufficient outcomes. Verify profile/catalog/schema parity and shared
owner state with SDK checks; replay real saved text separately as operator input, not
model gold. Run required suite/lint, build/check/install a new immutable 0.9.0 wheel.
No API purchase/call, active backend restart/install or allowance reset. The current
installed 0.8.2 remains unchanged until a deliberate user upgrade and new model test.

## 0.8.2 plain-anchor registration repair: 26 November 2026

The latest host run registered actual passages but both attempts failed sanitization.
Backend logs contain already-cleaned inputs, whose offline replay succeeds. Read-only
LM Studio caller inspection establishes the omitted difference: passage locator ends
in #CLAIM1. Existing Sanitizer removes fragments; ReviewService rejects any changed
input. This is a reproducible Margin registration friction point, separate from later
model-invented handles/hashes and date-scope changes. Caller metadata identifies
qwen/qwen3-8b with load.contextLength=30183, not an established context overflow.

Plan before code: version 0.8.2 permits only removal of plain ASCII anchor fragments
on evidence.register_sources source.url/passages[].locator. Require sanitizer.url's
private flag false and exact equality to the original URL with only its fragment
removed; permit an identifier-shaped fragment at most 100 chars, not query/signature/
encoded credential payloads. All other sanitization changes remain rejected; no
global sanitizer change, arbitrary text rewrite, field dropping, secret echo or
fetch. Return safe field-path normalization receipts/warnings, never original values.
Retain current validation, passage IDs, packet hashes/TTL and strict references.

Test the exact two caller payloads offline and fictional benign anchor cases, signed/
credential/encoded fragments, simultaneous text changes, existing schema checks,
quote round trips and unchanged network counters. Run full tests/lint, SDK and a new
immutable wheel check. Do not replace 0.8.1, install/restart the active backend or reset
allowances. A later host retry must still preserve unknown publication/record_date
and use actual returned references; the fix cannot prevent fabricated final prose.

The user separately reports a host-side margin_check_numeric_claim rejection for
unit=level on a CMMI maturity claim. This tool compares financial facts, not arbitrary
ordinal/certification levels. Keep the financial unit/basis schema unchanged. Clarify
its description and review instructions, test that level remains rejected before
dispatch, and route such semantic claims through passage review. Do not conflate that
expected schema guard with registration failures from another attempt.

Robustness extension requested by the user: exercise control characters/whitespace/
case normalization in URLs, partial assessments, missing passages, wrong kinds/IDs,
date scope and unsafe payloads. Require exact raw URL minus fragment, preventing a
URL parser from silently normalizing extra characters. Add response-only
assessment_coverage to preparation/submission/render/aggregation so read-operation
success is distinct from complete host assessment. Preserve existing status meanings,
immutable snapshots and independent-source/market-coverage caveats. No auto-coercion,
invented dates/units, forced semantic verdict or new live provider test.
Audit also exposes coverage and status_meaning; unsupported claims may legitimately
keep its status incomplete after every assessment is submitted. Keep credential-key
redaction global and expose safe formula metadata through aggregation_policy instead
of the legacy redacted policy field. Diagnostic paths must be schema-owned and omit
all caller values/unknown keys.

## Instruction delivery review: 26 November 2026

After the enabled-but-unused trial, an explicit MCP instruction elicited calls but the
user confirms the actual Infosys task/text was omitted. The model should request missing
input. Instead it invented another task/locator/quote; existing reference/quote/kind guards
rejected three calls and left review incomplete. Do not diagnose context overflow, missing
MCP connectivity or schema drift from this evidence. No runtime repair or new package is
implemented in this review; preserve the failed caller trajectory separately.

### Observed external approaches

- MCP initialization includes optional server instructions, which clients may place in
  the model prompt; this is advisory guidance, not a guaranteed system-prompt injection.
  [Specification](https://modelcontextprotocol.io/specification/2025-11-25/schema#initializeresult)
- Standard MCP prompts are discoverable, parameterized, user-controlled templates.
  They do not automatically become startup instructions. Margin currently exposes tools
  and initialization instructions, not a prompts/list/get interface.
  [MCP prompts](https://modelcontextprotocol.io/specification/2025-11-25/server/prompts)
- GitHub's current official server documents optional bundled workflow skills under
  --features=skills/Insiders, disabled by default and filtered by available tools. Its
  toolset configuration also narrows the tool surface/context. This is a concrete
  project-specific delivery choice, not a universally implemented MCP skills primitive.
  [GitHub MCP](https://github.com/github/github-mcp-server#mcp-skills)
- Microsoft's Playwright project documents MCP and CLI+SKILLS alternatives, recommending
  the latter for coding-agent cases where context efficiency matters. That does not prove
  adding a full skill alongside all MCP schemas reduces context in LM Studio.
  [Playwright](https://github.com/microsoft/playwright-mcp#playwright-mcp-vs-playwright-cli)
- Agent Skills defines workflow folders loaded by compatible agents. A skill is not
  installed/loaded merely because an MCP connects or a user attaches an arbitrary ZIP.
  [Skills overview](https://agentskills.io/home)
- LM Studio documents reusable presets containing system prompts and generation settings.
  That supports a compact preset experiment; its inspected MCP/preset docs do not establish
  native Agent Skills auto-loading or what this particular model actually received.
  [Presets](https://lmstudio.ai/docs/app/presets)

### Margin recommendation and experiment conditions

Keep the portable MCP's schemas, task triggers and next-step bindings; strengthen missing-
input/completion wording in a later separately planned runtime change if evidence warrants
it. Use the existing repo skill for skills-compatible hosts, with detailed references
loaded only as needed. For LM Studio offer the short system-prompt text in the MCP guide;
do not paste the entire 18-KiB skill plus all tools into a small context by default.
No host configuration/global skill is changed by this review.

Compare MCP-only, MCP+short host preset and MCP+skill (on a host supporting skills), with
the same complete task, model/settings/context and available tools. Record exact prompt/
skill/version hashes, host capabilities and first attempts. A missing-task case separately
expects clarification with no invented inputs or source access. An artifact-required
task measures workflow execution; a natural answer task permits optional tool selection.
Do not attribute benefits of added workflow instructions solely to MCP transport, or
penalize without-Margin answers for lacking Margin-specific IDs. No hidden reasoning is
required: preserve calls/results, visible summaries, final answer and observed recovery.

## 0.8.1 optional citation protocol plan and evaluation: 26 November 2026

The user asks whether to remove citation verification or retain a protocol for hosts
with suitable tools, and authorizes planning, implementation and testing. Keep it as
an optional evidence-review protocol. The successful guided 0.8.0 run establishes a
supplied-summary round trip, not original authentication or unguided usability.

### Decision and boundaries

Removing citation functions loses useful quote/reference checks and working handoffs.
Mandatory citation review adds irrelevant work to ordinary retrieval/math. Running a
Margin-side browser/LLM changes the product and cost model. Select optional host-side
review, advertised with exact schemas and next steps; preserve all existing functions,
tool names, profiles, packet hashes, TTLs and strict submission guards. No new provider
call, key purchase, active backend upgrade/restart or budget reset is part of this build.

The existing host_search declaration does not prove source-reading access. Add optional
host_profile.host_read_sources alongside the existing fields; absent means unknown,
not false or inferred from model brand. Declared capability is not verified competence.
Existing callers remain valid. structured_assessment=false still prohibits semantic
submission; a no-browser host may assess text supplied by the user/provider.

### Implementation

1. Return compact citation_protocol response guidance, outside frozen packet hashes:
   optional status, supplied-text-only review boundary, declared reader availability,
   claims without usable passages and the appropriate host action. Never infer a
   supported verdict or original verification from capability declarations.
2. Expose the same policy in workflow discovery. Describe optional original reading
   through the host's own browser/file reader/other MCP: inspect identity/date/basis,
   read the actual document, register exact original passages and prepare a new packet.
   Do not relabel summaries, mutate existing packets, fetch in Margin or invent a reader
   tool. Missing text allows insufficient_evidence or an unreviewed inventory.
3. Explain task selection in MCP instructions/descriptions and the portable skill:
   finance/retrieval do not require citation review, source authenticity remains
   unverified, and search access is separate from source reading and judgment ability.
4. Add an operator checklist with goal-only prompts for unguided finance/retrieval,
   supplied-text citation/sentiment, no-reader and reader-enabled hosts. Keep expected
   outcomes separate from tested-agent input. Also cover false quotes, insufficient/
   contradicted claims, mixed/missing labels, date scope and expired references.

### Acceptance and remaining gates

Offline tests must cover reader true/false/unknown, search without a reader,
inventory-only hosts, no-passage sources, original-reading registration guidance,
metadata/hash separation, strict wrong-quote rejection and unchanged zero-network
behavior. Test the generated typed schemas and an SDK review-profile round trip;
run required lint/format/suite and build a new immutable 0.8.1 wheel. Preserve 0.8.0.
These checks are software validation, not a new real-model or original-source trial.

After delivery, test first attempts in fresh model chats with user goals and ordinary
constraints only. Record actual model/context/profile/settings, host tool availability,
calls/errors/recovery, answer fidelity and optional visible why summaries. Separately
budget any new live retrieval; current review-only/zero-budget setup cannot fetch.
Then broaden real company/function coverage, freeze the release/tasks and conduct
the independent with/without-Margin benchmark. Public release/clean-install checks
remain separate; no PyPI publication or hosted deployment is included here.

## 0.8.0 review repair plan and evaluation: 26 November 2026

User authorized planning and implementation after the failed 0.7.0 review trial.
One generic review call guessed fields/run-derived packet refs; the subsequent host
attempts confused function identifiers with tools and malformed the call envelope.
No review-schema lookup is recorded. The review error incorrectly groups schema
failures with credentials/size errors. Generated thinking text is a fallible self-report,
not proof of hidden causes or context overflow. Preserve the original evidence.

### Evaluated approach

Instructions alone and a large union on margin_review keep the failed translation or
add branching complexity. Select ten thin typed review tools generated by deep copy
from protocols.schemas.SCHEMAS, plus an optional focused frontend profile. Full mode
grows from 25 to 35 tools; review mode advertises 14 local tools: ten typed review
functions, status/catalog, retained-result reading and source import. Do not claim a
small-model improvement before real-host testing; measure schema/instruction bytes.

The typed tools are margin_review_workflows, margin_register_sources,
margin_prepare_verification, margin_submit_assessment, margin_render_citations,
margin_audit_answer, margin_check_numeric_claim, margin_prepare_sentiment,
margin_submit_annotations and margin_aggregate_sentiment. Exact inputs come from the
host-advertised tool inputSchema; do not add function/arguments wrappers. The original
margin_review router remains in full mode for existing callers and exact catalog
function schemas remain available. Catalog prefers a typed route for review functions
and preserves an explicit generic alternative. No schema duplication or name aliases.

### Architecture and state

Core ReviewService retains zero inference/network behavior. Separate finite-JSON/size,
sanitization and schema errors using bounded schema-owned validation_summary. Do not
echo caller values/dynamic names, imply credential detection on schema failure or
silently coerce guessed fields. Keep existing invalid_input codes and all quote,
reference/hash, issuer/date, immutability/TTL, capacity and capability checks.

Add core next_steps descriptors after source registration/preparation/submission/
rendering. Bind only real source/packet references; do not invent reviewer, semantic
verdicts, annotations or final claim manifests. Expose required host input and valid
claim/source IDs. MCP decorates descriptors with the actual typed tool and binding;
other core interfaces retain function-based hints. Hints are response metadata outside
the frozen packet hash/snapshot. Existing next_action/required_output remain compatible.
Inventory-only hosts receive local render/aggregate hints, not a semantic submission.
Explain packet expires_at independently of original_document_verified and never refetch.

Add --tool-profile all|review to the stdio frontend, default all. A thin view over
either standalone MarginMCP or shared RemoteMCP filters definitions/calls, scopes
catalog discovery to review, exposes its profile in status and uses concise matching
server instructions. The shared backend remains the same full state owner, so changing
only a version-matched frontend profile does not restart it or lose source/packet IDs.
Profiles control advertised/callable frontend tools, not user authorization or a public
security boundary; other full clients retain the same owner/budgets. Backend logs
record underlying calls; frontend profile metadata/instructions are client-view details
and must be recorded in experiment configuration separately. Review mode cannot expose
provider connect/run/finance through catalog or forwarding. Unknown tools are errors,
not aliases or automatic execution. No database, host-brand branch or stronger LLM.

### Checks and release boundary

Test schema parity/isolation, each direct versus generic core route, the exact logged
bad input and corrected input, nonfinite/oversized/sanitized inputs without secret
reflection, real returned references versus fabricated/run IDs, wrong quotes/workflow,
inventory-only, expiry, immutable hash snapshots and no network. Exercise full citation
and sentiment round trips through typed tools, verify advertised next-step bindings,
and official SDK standalone/shared profile switching without extra provider attempts.
Test profile call/catalog rejection before forwarding, output schemas and text/structured
agreement, log counts and backend identity. Measure full/review definitions separately.

Publish this plan before runtime edits. Ship version 0.8.0 with a separately validated
wheel/checksum; older artifacts remain immutable. Update docs/skill and deliberate
installed instructions only; preserve connection configuration. No new authenticated
provider/model calls, purchases, active mtest installation/restart or allowance reset.
Use fictional fixtures and optionally saved sanitized text only, never call them
independent gold or real model acceptance. Active user backend is 0.7.0 with its one
estimated data credit spent. A later controlled upgrade/profile host test is separate.

## 0.7.0 typed retrieval preview plan and evaluation: 25 November 2026

The user authorized evaluation/planning before implementation. The 0.6.2 model fetched
the correct announcement schema but omitted arguments.query three times. Core rejection
was correct; generic arguments at the MCP boundary and unspecific retrieval errors
made recovery harder. The first status prompt also requested a package version that
margin_status did not expose. Preserve original private evidence; no schema drift or
provider failure was established.

### Alternatives evaluated

| Approach | Benefit | Cost/decision |
| --- | --- | --- |
| Keep generic routing with instructions only | Smallest tool surface | Does not address the observed wrapper translation; retain as compatibility path |
| Embed every operation schema in generic preview via a large union | All nested contracts inline | Repeats many schemas and adds complex branching for small hosts; defer |
| Seven typed Drishti previews | Every admitted operation directly typed | Three extra discovery helpers were not involved in this failure; defer those |
| Four typed event previews generated from reviewed schemas | Removes the failed wrapper step for current news/filing work | Select: 25 total tools, unchanged underlying operation inventory; measure schema bytes |

### Implementation boundary

Add margin_preview_news, margin_preview_announcements, margin_preview_earnings and
margin_preview_earnings_filing. Discovery tools expose the exact reviewed query object's
properties at their top level, plus optional why. The adapter constructs arguments.query
once; detail already has top-level ID or symbol/quarter selectors. Generate schemas by
projection/deep copy from Registry.specs; do not maintain a second provider schema by
hand. Preserve reviewed constraints/defaults including extraction=false; runtime selector,
date, limit, readiness and cost guards remain authoritative. These tools only call the
existing create_plan service. Execution still requires margin_run/session/idempotency;
no connection, provider data fetch or auto-refresh occurs during discovery/preview.

Keep generic margin_preview and its catalog mcp_execution route compatible. Add a
separate direct_preview route naming the typed tool, top-level binding and tools/list
inputSchema as its exact input authority. Its flat shape differs deliberately from the
core operation schema. Generic callers must obtain the selected exact schema through
margin_catalog(name=..., include_schemas=true), not memory, example prose or provider
documentation. Direct callers use the actual typed tool definition; both are generated
from the reviewed registry. Upstream native discovery checks compatibility only; changed
contracts remain quarantined until reviewed, never auto-approved from new documentation.
Make these distinctions explicit in MCP instructions, tool descriptions, catalog and skill.

Use the existing bounded schema-owned validation_summary for retrieval errors, including
missing query and allowed fields. Do not echo caller values, arbitrary property names,
dynamic keys or SDK diagnostics; preserve strict rejection and no automatic coercion.
Add data.package_version to margin_status, separate from envelope.contract_version.

### Validation and release

Test schema generation against all four reviewed contracts, direct/generic equivalent
plans, missing/misnested/unknown fields, extraction=true rejection, detail selector
guards, connection holds and zero-network previews. Exercise actual run/import after a
typed preview with fictional transports, shared backend/official SDK routes, status
version distinction and output schemas. Replay the logged flat/nested input offline.
Check generic legacy behavior, schema mutation isolation and sensitive-field redaction.
Measure tools/list schema size rather than claiming tokenizer/context compatibility.

No new authenticated provider/model calls, subscriptions, active mtest installation or
backend restart in this build. Publish this plan before runtime changes, release 0.7.0
with a new immutable wheel/checksum after tests, and preserve 0.6.1/0.6.2 artifacts.
Update owning docs/function guide/skill and deliberate installed instructions without
changing connection settings. A later user-led model acceptance remains necessary;
software tests do not establish improved model behavior. Final-prose enforcement,
wider native Drishti admission and the separate benchmark remain outside this patch.

**0.6.1 metadata patch:** per-metric formulas replace inherited report formulas;
comparison details add an explicit mapping while preserving the legacy percentage
formula field. Math, units, tools and response versions are unchanged. The latest
live audit separates tool metadata defects from model prose/omissions; see
[implementation](../implementation.md) and the [focused plan](fetch-and-calculate.md).
No final-answer verifier or new data access is added.

**0.6.0 reporting:** company response v2 adds a deterministic report projection,
consistent reporting units and matching row values/displays. Raw calculation fields are
opt-in details; the same request key projects them without fetching again. The
[published reporting plan](fetch-and-calculate.md#060-reporting-contract-plan-25-november-2026)
owns this change. No new tool, provider, inference, database or host-enforced final-
prose verifier is added. Underlying math/retention guards remain; model copying is
a separate behavioral test. [MCP usage](../mcp.md) owns migration.

**0.5.0 fresh-finance extension:** [self-contained company finance](fetch-and-calculate.md) adds one typed tool over a reusable core coordinator. Explicit execution fetches once, prepares facts and calculates, without previous result handles or raw-source buffers. Only bounded compact answers and request keys remain for process-local duplicate protection. Existing 20 tools, shared/standalone modes and underlying math are preserved; total now 21. This authorized convenience path supersedes the mandatory separate preview/run requirement for this tool only. Its default remains a no-call preview.

**0.4.0 fidelity/reconnect implementation:** twenty tools now include six directly typed common functions, and retained financial results include deterministic financial_view output. Optional shared mode routes short-lived stdio frontends through bounded owner-only Unix IPC to one explicitly started backend. That backend owns the unchanged core, credentials, ledger, results and optional journal. Standalone mode remains. This supersedes the earlier fixed-fourteen-tool/direct-only boundary for the authorized pass; historical design/results below are preserved. [Current operations guide](../mcp.md) owns setup/lifecycle.

Planned and implemented **25 November 2026**, after core checkpoint `6b22f57` was pushed and validated
with 194 tests. The implementation plan was pushed as `07b981a` before runtime work. The tested alpha is package 0.3.0 with 14 tools, 220 offline tests and source/isolated-wheel SDK stdio acceptance. [MCP usage](../mcp.md) owns commands and host configuration. This replaces the historical
proposal; its earlier text remains in Git history. [Core architecture](core-workbench.md),
[finance contracts](../financial-analysis.md), [review workflows](../review-workflows.md)
and [finance support](finance-data-support.md) remain authoritative for underlying behavior.

## Scope and architecture

Build a Python **local stdio MCP server** over the installed official SDK `mcp==2.2.0`.
The existing REST and upstream Drishti MCP adapters remain. No extra web backend, npm
package, database, Margin-side LLM, sampling fallback or public HTTP service is required.
The workbench and agent CLI remain available separately; each independently launched
backend has its own counters, not a shared account-wide allowance.

```mermaid
flowchart TD
    H[Host model and MCP client] -->|stdio| M[Margin MCP adapter]
    M --> C[One ResearchService for the process]
    C --> P[Preview, idempotent runs, budgets and receipts]
    P --> B[BharatStock REST]
    P --> D[Drishti hosted MCP]
    C --> F[Typed facts and deterministic finance]
    C --> R[Citation and sentiment review handoffs]
    M --> L[Optional private sanitized JSONL tool log]
```

The transport adapter calls public core methods, not HTTP routes or private run buffers.
Expose a stable workflow surface rather than 47 largely overlapping flat tools. All
13 retrieval, 15 local finance/fact and nine company operations remain discoverable;
ten review functions are separately discoverable in the same catalog. Nested names
must match those reviewed allowlists. Never expose Drishti's generic native executor.

## Public tool surface

| MCP tool | Core behavior | Provider calls |
| --- | --- | --- |
| `margin_status` | Mode, process ID, provider readiness and ledger | none |
| `margin_catalog` | Summary or filtered exact schemas for retrieval/calculation/company/review | none |
| `margin_preview` | Preview one to eight approved retrieval/local-calculation operations | none |
| `margin_company_preview` | Resolve retained financials versus one explicitly allowed dependency | none |
| `margin_run` | Submit existing plan with process ID and idempotency key; optional bounded wait | only planned operations |
| `margin_run_status` | Inspect a run, optionally wait at most 30 seconds | no new operations |
| `margin_result` | Retrieve one retained sanitized result | none; never refetch |
| `margin_sources` | Available retained financial responses | none |
| `margin_facts` | Typed facts with `auto`, explicit scale or unknown policy | none |
| `margin_calculate` | One of 15 explicit-input calculations directly | none |
| `margin_cancel` | Explicitly cancel a run, preserving uncertain-dispatch accounting | no retry |
| `margin_connect_drishti` | Explicit upstream metadata lifecycle action, guarded by process ID | bounded metadata HTTP |
| `margin_review` | One of ten local citation/sentiment functions | none/model-free |
| `margin_review_sources` | Import retained source text into the review store | none |

Catalog summaries omit bulky schemas by default. Exact schemas are requested by name
and group. Preview operations still receive strict core validation, holds, bounds and
cost estimates. Company functions retain the existing `fetch_missing: false` default.
Independent calculations and review actions do not require a preview since they cannot
fetch data. Partial/incomplete financial results are valid domain outcomes, not invented
values or transport failures. Pure calculations have no hidden source lookup.

## Lifecycle and contracts

- Create one core service in MCP lifespan; close all tasks/providers on EOF/shutdown.
  Tool listing, initialization and status must not connect to providers.
- Generate an opaque process/session ID and a per-call ID for log correlation. Preview returns it; run and Drishti connection
  require it. A restarted process rejects old handles before paid dispatch.
- Preserve core plan expiration, idempotency keys, shared concurrency/allowances and
  Drishti metadata checks. Run/status waiting is bounded to 30 seconds and shielded;
  cancelling a tool-call waiter does not silently replay/cancel an already submitted run.
  Use `margin_cancel` for explicit run cancellation. Retry submission only with the same
  plan/key; uncertain upstream outcomes are not automatically retried.
- Return both structured JSON and JSON text for older clients. The envelope contains
  adapter contract version, process/call IDs, mode, tool and data or safe error. Financial
  definitions, units, source paths, unverified labels, receipts and limits stay intact.
- Validate tool schemas and 64-KiB input bounds before dispatch. Reject unknown keys,
  nonfinite numbers, arbitrary operation names and credential-bearing arguments.
  Sanitize errors and bound output; never print secrets, raw exceptions or HTTP headers.
- Protocol messages alone use stdout; diagnostics use stderr. No real keys in config
  examples, tool arguments, source, Git, skills or bundled wheel metadata.
- Optional `why` is one visible line (1–280 chars), an agent self-report rather than
  hidden reasoning. Optional operator-configured JSONL recording stores sanitized
  request/result events. Logging is off by default, private 0600, and outside product
  imports of the research harness. Pre-dispatch write failure stops execution; a
  post-dispatch failure returns the available result with an explicit warning.
- Annotate read-only/idempotent/local versus provider actions accurately. Annotations
  are advisory and do not replace admission/validation. Tool names/schemas are stable;
  current provider availability comes from status/catalog rather than dynamic removal.

## Implementation sequence

1. **Push current core**: source/private-data/secret review, regression suite, commit/push
   checkpoint. Completed: `6b22f57`, no private captures or numerical gold included.
2. **Plan before code**: publish this architecture, mapping and acceptance checklist;
   update AGENTS/context to replace the old no-MCP gate. No runtime changes in this step.
3. **Thin adapter**: `src/margin/interfaces/mcp/{server,tools,recording}.py`, module launcher
   and `margin-mcp` entry point. Explicit `--mode`, optional local credential file and
   optional recording path; normal provider configuration continues through environment.
4. **Tests**: direct handler contract/guard tests, SDK client over real stdio subprocess,
   complete fictional retrieval/finance/review workflows, restart/idempotency/cancellation,
   logging, output redaction and shutdown. Existing core/CLI/workbench tests must pass.
5. **Package and document**: build/install the wheel in a separate target, exercise its
   stdio launcher, provide host-neutral configuration and a fresh-chat starter. Host
   inference/benchmark runs remain a separately labelled next gate.
6. **Push adapter**: final source/artifact scan, commit and push the tested alpha. Retain
   diagnostics privately; do not rebuild old 16-November evaluation archives.

## Acceptance gates

| Gate | Required observation |
| --- | --- |
| Protocol | SDK initialize, stable 14-tool list, valid tool schemas/results, text and structured output, clean stdout/EOF |
| Full reachability | Catalog accounts for all 37 retrieval/finance and ten review functions; exact schemas discoverable |
| Cost/state | No startup/list/status/preview/fact/review fetch; repeated run key dispatches once; stale process rejected |
| Domain limits | Unknown/missing/held inputs remain explicit; scope/unit/TTM safeguards survive transport |
| Lifecycle | Explicit cancellation and shutdown drain tasks and close upstream sessions; no automatic retry |
| Logs | Why is optional/validated; logs off by default; configured logs are sanitized, private, ordered and bounded |
| Packaging | Wheel includes adapter/entry point, excludes credentials/research answers/private results; isolated launch works |
| Host | Actual MCP SDK transport exercised; model-host decision quality is not inferred from protocol tests |

First implementation validation uses fictional software fixtures, clearly labelled,
with **zero authenticated provider/model API requests**. The earlier real core results
are evidence for provider behavior, not a new MCP-host test. Any later real MCP probe
needs its own bounded budget; paid plans are not a prerequisite for packaging.

Reference baseline: [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
and [official Python SDK](https://py.sdk.modelcontextprotocol.io/). The installed pinned
SDK's constructor callbacks/lifespan/stdio APIs were inspected locally; do not copy v1
decorator examples or silently upgrade dependencies for this adapter.


## Alpha implementation result: 25 November

The source adapter and isolated wheel each completed 27 actual stdio SDK calls across
all 14 tools, with 54 private sanitized log events and matching text/structured results.
Protocol negotiation was 2025-11-25. The catalog exposed 13/15/9/10 operations by group.
Provider/model calls were zero: the acceptance companies and annotations are fictional
software fixtures. Core financial/data guards remain covered separately, including
previous real-source tests. Additional lifecycle/invalid-input/logging tests bring the
suite to 220. Per-call IDs were added to the planned envelope for explicit log correlation.

An isolated target import and console-script launch passed using existing pinned
dependencies. Clean dependency installation on other platforms, real-model host behavior
and a newly budgeted live MCP pass remain unverified. No host settings were changed.
The wheel and source scans exclude credentials, private answers and provider captures.

## Distribution and live-release evaluation: 25 November

This section is researched planning, not a new release, hosting deployment or conformance
claim. Public standards and provider terms were checked on 25 November 2026. The current
0.3.0 alpha remains a local stdio application with 2025-11-25 transport acceptance.

### Recommended distribution

Release the local Python application first, using separately supplied provider credentials.
Publish a tagged, scanned wheel and source distribution through GitHub Releases, then
PyPI after clean installation and host acceptance. Users install the application and
configure a stdio-capable host to launch `margin-mcp`. No Margin-operated financial data
server, mandatory skill, npm rewrite, or public service is needed for that release.

| Form | What users receive | Evaluation for Margin |
| --- | --- | --- |
| Python wheel / source distribution | Installable application, dependency metadata and console launcher | Primary distribution; already has a wheel, release pipeline still needed |
| MCPB desktop bundle | ZIP-based `.mcpb` plus `manifest.json`, runtime/dependency setup and configuration | Optional later convenience for supporting desktop hosts; test Python/platform support |
| OCI/container image | Reproducible runtime launching stdio or a separately implemented HTTP adapter | Optional deployment artifact; containerization alone adds no remote MCP endpoint |
| Hosted Streamable HTTP | An HTTPS URL configured in a compatible host | Later service offering; requires authenticated user isolation and operational controls |
| MCP Registry entry | Versioned discovery metadata pointing to a package or remote endpoint | Optional discoverability step; does not deploy or host Margin |

MCPB is a desktop distribution format, not a prerequisite for MCP interoperability. Its
manifest supports Python servers and sensitive user configuration. Bundled dependency and
Python availability still need platform validation. See the [MCPB specification](https://github.com/modelcontextprotocol/mcpb/blob/main/MANIFEST.md).
The [Python publishing guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
describes tagged wheel/source releases and PyPI Trusted Publishing without a long-lived
publishing token. No package-name availability, PyPI ownership or registry namespace has
been established for Margin.

### Standards and measured gaps

The current dated MCP specification is **2026-07-28**. It uses `server/discover` and
per-request metadata rather than the older initialization handshake. Inspection of the
installed Python SDK 2.2.0 found modern and legacy implementation paths; our tests use
`ClientSession.initialize()` and demonstrate only the legacy negotiated version. Test
both eras before advertising compatibility; do not upgrade dependencies blindly or
assume every host supports the same revision. [Specification](https://modelcontextprotocol.io/specification/2026-07-28),
[SDK version negotiation](https://py.sdk.modelcontextprotocol.io/protocol-versions/).

| Requirement or practice | Margin assessment / action |
| --- | --- |
| JSON-RPC framing, tool discovery, valid declared capabilities and revision behavior | Legacy stdio exercised; add modern discovery/request-envelope coverage and publish a compatibility matrix |
| Protocol-only stdout; diagnostics on stderr | Implemented and transport-tested |
| Input validation and structured output conforming to advertised schemas | Implemented at envelope/core level; schemas for nested results remain broad and should become more informative |
| Protocol versus tool execution errors | Unknown tool names now return JSON-RPC errors in patch 0.3.1, tested over stdio; provider/business failures remain tool errors |
| Cancellation, expired handles, no duplicate paid dispatch | Existing tests cover key cases; repeat across supported protocol eras and actual hosts |
| Tools versus optional resources, prompts and extensions | A tools-only server is valid; none of the optional features is mandatory for our release |
| Python package release metadata and provenance | Add chosen code license, project URLs, support/changelog and release automation; confirm dependency license/security compatibility |
| Honest product semantics | Preserve missing-data/unit/scope caveats and host-reported citation/sentiment labels; packaging does not authenticate original sources |

The [tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
distinguishes unknown-tool/malformed-request protocol errors from actionable execution
errors. An advertised output schema must match structured results. Richer per-tool output
schemas and simpler high-frequency financial tools are usability improvements, not a
requirement to flatten all 47 nested functions. Test small-model discovery first.
The [stdio binding](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/stdio)
requires clean newline-delimited JSON-RPC on stdout.

### Release sequence and acceptance

1. **Standards repair:** correct protocol error mapping; exercise modern and legacy
   discovery/list/call/cancel/shutdown and malformed-input wire behavior. Record supported
   revisions and exact SDK/test-tool versions. Keep initial tests offline.
2. **Releasable artifact:** choose the code license with the project owners; complete
   metadata/changelog, build wheel and source distribution, scan both for credentials,
   provider captures, private logs and evaluator answers. Install from the artifacts on
   clean macOS/Linux/Windows environments with supported Python versions. Existing
   isolated-target acceptance reused dependencies and does not satisfy this gate.
3. **Independent clients and real data:** test with MCP Inspector, then at least two
   actual target hosts. Use a separately recorded one-company live plan and explicit
   provider HTTP/credit bounds. Verify source units, financial results and data reuse,
   quota/access failures, cancellation and duplicate submission behavior. Never charge
   production credentials during broad conformance/fault scenarios.
4. **Private beta and evaluation:** distribute the versioned artifact to the team;
   collect setup failures and workflow traces. Compare catalog-based versus simpler
   discovery if smaller models struggle. Run matched with/without-Margin tasks with
   independent answers; log tool inputs/outputs and visible one-line self-reports,
   not hidden reasoning. The optional professor harness remains separate.
5. **Public local release:** after the gates, tag and publish artifacts, verify a fresh
   installation, then publish registry metadata if desired. Hosted deployment follows
   its own gates below; public software distribution and data-serving rights differ.

[MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) provides interactive
and CLI clients. The [official conformance framework](https://github.com/modelcontextprotocol/conformance)
provides revision-filtered wire/schema checks; select applicable tools-only scenarios.
Its documented server target is an HTTP URL, so do not assume its full server suite can
run against our current stdio launcher unchanged. Inspector and our SDK subprocess tests
can cover stdio while HTTP-specific conformance follows the HTTP adapter.

### Hosted service: separate architecture gate

Use a new Streamable HTTP adapter over the same core, exposed behind TLS at an endpoint
such as `https://<chosen-domain>/mcp`. The modern revision accepts POST and removes the
standalone GET stream and protocol sessions. Legacy-compatible serving must retain the
older revision's behavior when that revision is negotiated. Do not copy an old SSE-only
deployment recipe. The SDK should implement wire behavior; validate it at the deployed
proxy as well. [HTTP transport specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports/streamable-http).

For a restricted service that spends provider credits, implement interoperable OAuth
authorization, protected-resource discovery and token audience/issuer/expiry/scope checks.
Authorization is optional in MCP generally; it is our service requirement, not a universal
condition for a local server. Stdio instead takes operator credentials locally.
Authenticate users independently of provider keys and opaque run handles. Never forward
a Margin access token upstream as a provider credential.
[Authorization specification](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization).

Before exposing the endpoint, add:

- Identity-scoped core/run/review state and authorization on every handle lookup; never
  share today's one process-wide service and result buffers across arbitrary users.
- Atomic provider-account and user allowances across processes/restarts, plus bounded
  concurrency and idempotency. A small operational ledger/store is not a financial corpus.
- Explicit provider-key ownership model: user credentials stored as protected secrets,
  or Margin-owned subscriptions with applicable end-user/re-exposure rights. Local BYOK
  reduces shared-secret hosting work but does not waive provider restrictions.
- Host/Origin allowlists, applicable CORS, request/time/output bounds, abuse protection,
  sanitized metrics, opt-in private recording, retention/deletion, health/readiness checks
  and controlled shutdown/rollback. Treat provider narratives as untrusted source text.
- Tenant-isolation, wrong-audience, expired-token, quota-race, restart, proxy-streaming and
  sustained-load tests using fictional upstreams before a bounded real acceptance pass.

Modern MCP transport statelessness does not remove application state: our retained plans,
results, review packets and cost accounting still need ownership, TTL and routing/storage.
Start with a controlled single instance or explicit workspace routing; add workers only
after state and ledger behavior are defined. See [SDK deployment guidance](https://py.sdk.modelcontextprotocol.io/run/deploy/)
and [MCP security guidance](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices).

### Registry and provider permissions

The official registry accepts local-package or remote metadata through `server.json` and
`mcp-publisher`. A candidate GitHub namespace is `io.github.rishitttt/margin`, subject to
ownership authentication and availability. PyPI entries require the package README's
`mcp-name:` marker to match the registry server name. Registry schema versions are
independent of MCP wire revisions; generate against the publishing schema current at
release time. Registration is optional for using a configured server and is not evidence
of financial accuracy or host compatibility. [Publishing guide](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/quickstart.mdx),
[package ownership requirements](https://github.com/modelcontextprotocol/registry/blob/main/docs/modelcontextprotocol-io/package-types.mdx).

Published provider terms distinguish ordinary querying, internal model evaluation and
third-party serving. BharatStock lists internal model evaluation on Developer/Pro and
separate conditions for distributed/productized uses. Drishti distinguishes internal
use, permitted display/programmatic re-exposure and redistribution; its platform/order
agreement may govern. Confirm the actual agreements for our benchmark and any hosted
aggregation before promising those uses. This public-page review does not establish our
account permissions. No plan purchase or provider contact was made.
[BharatStock terms](https://bharatstockapi.com/terms),
[Drishti terms](https://drishti.manasija.in/legal/terms-and-conditions).

## Implementation plan: financial fidelity and reconnects, 25 November

Authorized after the live HINDUNILVR review. Preserve the raw payload, financial guards,
existing 14 workflow tools and historical evaluation archives. Initial implementation
and saved-response checks make zero authenticated provider/model calls.

1. Add a shared deterministic financial view to retained financial results: reviewed
   statement INR versus EPS INR/share, exact crore conversion, stable metric labels,
   period/basis/source paths, missing values and continuing/total-profit warnings. Never
   infer a unit from magnitude, rename operating profit as PBT/EBIT or authenticate a
   provider record by formatting it. Bound the view and retain raw data unchanged.
2. Add six directly typed MCP tools for margins, unit conversion, period comparison,
   cashflow metrics, profitability and balance-sheet metrics. Copy actual core schemas;
   remove the function-selector/nested-arguments step for these tools. Keep generic
   calculation/catalog access, exact validation and explicit input provenance. Measure
   discovery schema size; this is not a decision to inline all review/provider schemas.
3. Add optional local shared-backend mode: an explicitly started `margin-backend`
   process owns one ResearchService, stable process ID, quotas, idempotency and TTL-bound
   buffers. Short-lived stdio frontends connect over a private filesystem Unix socket.
   Use no HTTP dependency/public listener, maintained corpus, automatic provider call or
   automatic allowance reset. The backend owns credentials and optional sanitized logs;
   proxy processes never receive keys. Socket-directory/socket permissions, framing and
   request/output bounds, single-backend ownership and fail-closed version/epoch checks
   are required. Do not retry an ambiguous local RPC. A backend restart still invalidates
   handles and counters; filesystem persistence of licensed data/account-wide spending
   is outside this change. Shared mode initially targets macOS/Linux; standalone stdio
   remains available. No silent worker autostart/restart after a failure.
4. Test exact schemas and financial guards; real SDK stdio; two successive frontends
   using one backend for preview/submit/result/facts, source reuse and unchanged quota;
   idempotent duplicate submission; backend restart/stale IDs; malformed framing,
   unavailable backend, private logs and shutdown. Reprocess the saved real HUL response
   separately from fictional regression data. No new paid request is necessary.
5. Build and scan a new wheel, validate installed-package shared mode outside checkout,
   update source/installed skill deliberately, docs and private evidence, push the
   implementation. Start/configure the local mtest backend only with a zero-provider
   startup and preserved credential/allowance settings; host/model acceptance is then
   a distinct user retest. Keep the professor's evaluator independent.

The backend is an application-state owner, not protocol-level MCP sessions or a public
multi-user service. Do not weaken `session_changed` or bypass the preview/run boundary to
work around LM Studio lifecycle behavior. This plan supersedes the earlier no-extra-
backend assumption only for the explicitly requested optional local shared mode.
