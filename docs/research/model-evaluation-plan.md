# Margin model evaluation: proposed design

Research and documentation proposal, 28 November 2026. No new benchmark, task set,
answer key, runner or model/provider execution has been created by this change.
The user has now requested evaluation planning; earlier product-only scope notes do
not prohibit this documentation work. Keep the optional study outside product imports
and distributions. The [short professor note](../updates/professor-reference-2026-11-28.md)
summarizes this proposal. Older research documents remain historical, not measured
results for this study.

## Questions to investigate

1. Does access to Margin improve the same model's task accuracy and completion?
2. Which gains concern data access, deterministic calculation, evidence handling or
   workflow controls? Does the improvement vary across model configurations?
3. Which observed action patterns accompany success or failure: tool discovery,
   repair loops, unnecessary fetches, unit changes, ignored warnings, or invented facts?

Larger gains for smaller models are a hypothesis to test. Tool-use support in a model
card does not establish successful Margin use. Existing trials are product smoke
observations, not this benchmark's results.

## Recommended model cohort

Use four local configurations first. Three were shown installed in the user's earlier
inventory; exact files and current availability must still be checked at preflight.
This is a practical, reproducible starting cohort, not a latest-model leaderboard.

| Candidate | Reason for inclusion | Control required |
| --- | --- | --- |
| Qwen/Qwen3-4B | Adds a small model; same-family contrast with 8B | Pin the original hybrid-thinking checkpoint, not an ambiguously named newer variant |
| Qwen/Qwen3-8B | Existing local model and observed discovery/context issues | Pin revision, quantization, template and thinking setting |
| meta-llama/Llama-3.1-8B-Instruct | Existing, older cross-family control at a similar nominal size | Validate actual runtime tool parsing; no assumption of a dedicated thinking channel |
| openai/gpt-oss-20b | Existing alternative reasoning/tool-use architecture | Preserve its Harmony-compatible template and fixed reasoning effort |

The [Qwen 4B](https://huggingface.co/Qwen/Qwen3-4B) and
[Qwen 8B](https://huggingface.co/Qwen/Qwen3-8B) cards document thinking controls and
agentic use. [Meta's model card](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct)
documents tool-use formats. The [gpt-oss card](https://huggingface.co/openai/gpt-oss-20b)
documents native tool use, reasoning effort and Harmony. Its approximately 21B total/
3.6B active parameters do not make it a simple dense-model size comparison. The card's
16GB memory claim is not a guarantee for this host with a large context/KV cache.

Match quantization/runtime formats where feasible, but interpret different weights,
templates or backends as different configurations; do not attribute all differences
to parameter count. Freeze settings within each model's with/without pair.

**Extensions, not prerequisites:**

- [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) and
  [Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) offer a newer small-model pair.
  Add them if the installed runtime supports their architecture/templates. Select them
  before scoring; do not replace a poorly performing model after seeing held-out results.
- [GPT-6.2 Sol](https://developers.openai.com/api/docs/models/gpt-6.2-sol) is an optional
  hosted reference. Its current API documentation supports function calling; use the
  [Responses API](https://developers.openai.com/api/docs/guides/deployment-checklist).
  Budget inference separately from provider credits. The local client can dispatch
  emitted function calls to a local stdio MCP client; no public Margin endpoint is
  needed. API envelopes may differ, but preserve tool semantics and record schema hashes.
- The already-installed R1 distills can be supplementary reasoning tests, subject to
  tool-call preflight. The [14B card](https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-14B)
  is not evidence that a particular LM Studio template parses every Margin call.
  Do not infer unsupported tool use from the distill's mathematics performance or
  treat the user's truncated model labels as exact checkpoint identifiers.
- GPT-5 mini was considered but its [current official page](https://developers.openai.com/api/docs/models/gpt-5-mini)
  marks it deprecated; it is not the preferred new hosted reference.

These are recommendations inferred from documented capabilities and the existing
inventory, not comparative performance findings. Obtain/pin exact available versions;
if a hosted service exposes only a mutable alias, record returned model ID/date and
acknowledge service drift rather than promising immutable weights.

## Master set and reference answers

Propose 48 tasks: eight calibration tasks, then 40 scored tasks fixed before the main
experiment. Start with INFY and HINDUNILVR, with explicit exchange, period, reporting
basis and as-of scope. Do not generalize two-company findings to the whole market.

Allocate five scored tasks to each group:

1. Financial/source retrieval and reporting periods.
2. News, announcements and earnings discovery/relevance.
3. Growth, CAGR and eligible TTM.
4. Margins and other profitability measures.
5. Cash-flow and balance-sheet metrics.
6. FCFF/DCF/sensitivity with explicit shared assumptions.
7. Claim support, citation handling and content sentiment.
8. Missing/incompatible inputs, unit conversion, refusals and duplicate protection.

Final counts/wording depend on calibration and independently checkable evidence, not
an attempt to force equal coverage of unavailable data. DCF questions must not ask a
model to invent a correct company forecast. Deliberately false claims are test inputs,
not fabricated provider observations. Ordinary prompts name the goal, not the correct
Margin function. Guided repairs are diagnostic follow-ups, separately scored.

The reference package remains hidden from tested models. Build it independently from
original issuer documents where possible, reviewed formulas and independently checked
calculations; do not use Margin's own output or another model's prose as sole ground
truth. Record exact dates, units, basis, definition, source location and acceptable
tolerance. Keep provider-data accuracy separate from correctly processing that data.

For semantic claims and sentiment, prepare a human-reviewed rubric with acceptable
judgments and evidence boundaries. Double-review an agreed sample, adjudicate disputes
and report disagreement. Do not assume one sentiment label is objectively correct or
infer investor sentiment from announcement tone. Grade dates, relevance, quote fidelity
and unsupported inferences independently of a positive/neutral label.

## Paired with/without-Margin design

Every scored item is answered by the same model in both conditions. Keep task wording,
common instructions, evidence access, output format, decoding/reasoning settings,
context limit and time/action budgets matched within the pair. The declared Margin
tools/instructions necessarily differ; record that difference. Use fresh conversations
and isolated experiment state, randomize condition order, and run three repetitions.
Four models × 40 tasks × two conditions × three repetitions = 960 scored responses before
calibration or optional extensions. This is a proposed model-run count, not an estimate
of paid API requests or provider credits.

The shared question should not demand “use Margin” when that interface is absent in
one arm. Use neutral goal-based questions and a common instruction allowing available
tools. A correct answer without a call can pass answer grading while recording non-use
in the enabled condition; it is not evidence that Margin caused that answer. Explicit
tool-following checks, if included, are separately labelled interface tasks.

Separate two tracks rather than silently confounding access with reasoning:

| Track | Without Margin | With Margin | What the difference measures |
| --- | --- | --- | --- |
| Supplied-data calculations/review | Same real evidence packet and declared assumptions, no Margin | Identical packet plus local Margin tools; provider allowance zero | Assistance from calculations, structured review and guards |
| Fresh retrieval/end-to-end research | Same allowed host search/read tools and source scope, no Margin | Same host tools plus Margin provider access | End-to-end utility, including provider-access benefit |

Record baseline inability to obtain a source rather than inventing an answer. A
retrieval gain is not automatically evidence of better financial reasoning. If we
need to isolate the interface from provider access, add a separately budgeted third
condition exposing the same raw provider API/data without Margin normalization or
calculators. Do not advertise that optional ablation as already implemented.

For pure arithmetic tasks, any non-Margin calculator/Python access must be explicitly
fixed in both arms or tested as a separate stronger baseline; do not quietly give
one host general tools the other lacks. Browser/read capability is likewise a declared
condition. Review tasks without a reader use supplied passages, not imaginary access.

Fresh live calls remain the requested retrieval mode. Fix date ranges/periods rather
than relying on a drifting “latest”; run pairs near in time, record actual returned
data/as-of times and preserve private receipts for grading. If observations differ,
flag the pair as data-mismatched and report it separately. Do not reuse a single stale
number as the gold answer to all future live calls. A small permitted test archive is
an experiment artifact, not a product corpus; raw data retention/sharing follows the
provider's permissions. No capture/redistribution permission is presumed.

## Preflight and experimental controls

- Record checkpoint/revision or artifact hash, quantization, runtime/host versions,
  hardware, templates, MCP package/tool profile/schema hash, decoding parameters,
  reasoning setting, context allocation and token/action/output limits.
- Test a simple tool call, validation failure and complete result round trip before
  scoring. Setup/parser failures are visible outcomes; do not silently substitute a
  different model. Calibrate with the eight separate tasks, then freeze configuration.
- Target a common 32K context only if the hardware and full prompt/tool inventory fit,
  including answer/reasoning headroom. Measure actual token usage; do not assume 4K is
  enough. Qwen3's card documents native 32,768 tokens. No silent truncation or unnoticed
  RoPE-scaling change. If full 39 cannot fit, report the incompatibility; a focused
  profile is a separately declared study condition, not an unreported rescue.
- Preserve model-specific supported sampling settings rather than imposing an invalid
  universal temperature. For example, Qwen's thinking-mode card discourages greedy
  decoding. Keep choices and reasoning effort identical across that model's pair;
  seeds are recorded only where honored, not presented as guaranteed determinism.
- Use no hints or edits mid-scored task. Do not change Margin/model settings after
  seeing test answers. Freeze the study release; evaluate fixes as a new version.
- Allocate a separate reconciled experiment budget before any live calls. Fresh trial
  state is not renewed upstream quota. Never restart the user's active owner to rescue
  a run. New trial keys are unique; duplicate-protection tests reuse the same key within
  their own trial. Meter failed requests and Drishti lifecycle traffic too.

## Capturing reasoning and action traces

Keep three distinct evidence streams, joined through experiment/task/trial IDs:

| Stream | Contents | Interpretation |
| --- | --- | --- |
| Actual actions | Tools advertised, calls/arguments, returned data/errors, timing, retries, provider attempts | Observable behavior, including a tool that was never called |
| Visible choice summaries | One short line before important actions; Margin's optional why field | Self-reported rationale, not hidden reasoning or proof of causality |
| Exposed model reasoning | Native emitted thinking text or provider reasoning summaries, where available | A model output channel whose presence and faithfulness vary |

Use the same brief-choice instruction in both arms. Without Margin, capture its visible
decision notes directly; with Margin, additionally retain why/decision_summary. Do not
ask for a reconstructed long explanation after failure and label it a contemporaneous
trace. Mark missing rationale as missing. A post-hoc rationale is separately labelled.

**Existing Margin logging:** opt-in --record-dir/--record-file records sanitized
request/response JSONL with call/session IDs and timestamps. It does not capture final
assistant prose, model thinking, every host-side parse rejection or arbitrary user
messages. Capture those through the host as well. Verify recording_enabled and actual
events; never infer use of Margin from a convincing answer.

**Proposed local capture:** use an isolated LM Studio evaluation host. Its
[native streaming events](https://lmstudio.ai/docs/developer/rest/streaming-events)
include reasoning deltas, tool-call arguments/results/failures and final-message deltas.
Store the stream and final answer separately from Margin logs. These events are for
the documented native chat endpoint; do not assume every compatible endpoint/UI export
has the same fields. Validate event availability for the exact installed version/model.

The official [CLI model-I/O log command](https://lmstudio.ai/docs/cli/serve/log-stream)
can provide a diagnostic fallback:

```sh
lms log stream --source model --filter input,output --json
```

This is a documented command, not an executed collection in this proposal. Scope it
to the isolated study host; it may expose unrelated chats if used on a shared desktop
session. Model-I/O text alone is not a substitute for structured execution receipts.

Qwen's emitted thinking blocks and gpt-oss's exposed analysis can be retained when the
runtime provides them. Llama may have no dedicated reasoning channel: mark it
unavailable, not “no reasoning.” For hosted OpenAI models, request supported
[reasoning summaries](https://developers.openai.com/api/docs/guides/reasoning#reasoning-summaries)
if desired; raw internal reasoning is not returned. Opaque/encrypted continuity data
is not readable reasoning and should not be decoded or scored as such.

Generated explanations can be unfaithful, as demonstrated by
[Turpin et al.'s primary study](https://arxiv.org/abs/2305.04388). Analyze agreement
between explanations and actual actions; do not equate length or confidence with
correctness, or conclude that a stated rationale identifies the model's true internal
cause. The comparable primary trace across all models is the action sequence plus
brief visible choices, not unequal amounts of native thinking text.

Proposed private run artifacts: manifest.json, host-events.jsonl, margin-tools.jsonl,
final-answer.json, exposed-reasoning.jsonl (or unavailable marker), and grading.json.
Include prompt/schema hashes, outputs, error class, tool-not-used/truncation flags,
timing and reported token counts. Preserve absent fields as unknown. Sanitize keys,
signed URLs and sensitive content before sharing; host logs do not automatically
inherit Margin's sanitization. No public raw-log release is implied.

## Scoring and pattern analysis

Use a shared answer format: final answer, metric/value/unit/period/basis where relevant,
evidence references, missing inputs and limitations. Keep evaluator-only expected
answers and grades out of model-visible packets. Grade both backend result correctness
and final prose fidelity: a correct tool result followed by wrong units is a failed
answer even if the calculation engine passed.

Common answer fields use the shared evidence identifiers/locators; the without-Margin
arm must not be required to invent Margin packet/request IDs. Actual Margin call
records are additional process evidence. Tool-selection and schema-repair metrics are
scored only where that interface is available, not as automatic baseline failures.

Report per-model and per-task-family paired differences in numeric accuracy, scope/
unit correctness, unsupported-claim rate, claim support, relevance handling and task
completion. Add latency, tokens, provider attempts/cost estimates, invalid calls,
repair-loop length and timeouts. Failure to obtain data is distinct from financial
miscalculation. No-provider-call constraints and replay behavior receive their own
checks. Sentiment scores use the human rubric; Margin's host verdict is not the oracle.

Average repeats within question before estimating paired improvements; confidence
intervals should resample questions, not pretend repeated answers are independent
new tasks. Disclose the limited issuer/task coverage. Audit a sample blind to model/
condition where possible; no single unreviewed LLM judge supplies all grades.

Code trace patterns such as right tool first, catalog overload, invented identifiers,
validation-repair loops, ignored source/scope holds, extra fetches, skipped execution,
and correct-tool/wrong-final-answer. Relate them to success within model and condition.
Treat inferred motives as hypotheses, not established mechanisms. Repeat tasks from
the master set, not task-specific operator coaching.

## Next steps before running

Confirm hardware and exact installed artifacts; calibrate capture and tool parsing;
create/review the master set and hidden references; freeze settings/tasks; estimate
provider/model budgets from the final task mix; then obtain a fresh allocation and
execute randomized paired trials. No model download, inference purchase, provider
request, active-owner change or collection has been performed for this plan.
