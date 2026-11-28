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

Updated after the user's request to include Luna, Sol and Inkling and to consider new
local downloads. Plan four local candidates plus two hosted references; final inclusion
requires preflight, not success on held-out questions. Model choice is not limited to
what was installed during the earlier trials.

### Hardware and actual installed Inkling

Read-only checks on 28 November found an Apple M4 Pro with 24 GiB unified memory
(25,769,803,776 bytes). The installed artifact is:

- lmstudio-community/Inkling-2-Mini-GGUF/Inkling-2-Mini-Q4_K_M.gguf
- Model file 17,478,094,048 bytes (about 17.48 GB /16.28 GiB).
- Separate image projector 641,805,888 bytes. These are file sizes, not measured runtime RAM.

No model was loaded or queried. No model files/configuration were changed. Downloaded
weights do not establish that tool calls and the chosen context run reliably.

| Planned candidate | Where/how to run | Role and feasibility judgment |
| --- | --- | --- |
| Qwen/Qwen3.5-4B | Local, supported 4-bit MLX or GGUF build | Small-model starting point; comparatively more memory headroom on this Mac |
| Qwen/Qwen3.5-9B | Local, supported 4-bit MLX or GGUF build | Same-family larger comparison; a practical candidate on 24 GiB, pending measured context use |
| openai/gpt-oss-20b | Local, existing compatible quantized build | Different MoE/reasoning architecture; preserve Harmony and fixed reasoning effort |
| thinkingmachines/Inkling-2-Mini | Local, existing Q4_K_M GGUF | Requested looped-model comparison; conditional on full tool/context memory preflight |
| gpt-6-luna | Hosted client/API; not a local weights download | Lower-cost hosted reference |
| gpt-6.2-sol | Hosted client/API; not a local weights download | A second hosted reference with a different cost/capability role |

The [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) and
[Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) cards document tool use and thinking
controls. A [community 9B MLX conversion](https://huggingface.co/mlx-community/Qwen3.5-9B-MLX-4bit)
is about 5.6 GB on disk; actual RAM includes runtime/cache overhead. Choose a maintained
conversion supported by the installed runtime, then pin its revision/hash. Do not
infer memory use from a misleading quantized-parameter count on a model listing.
The [gpt-oss card](https://huggingface.co/openai/gpt-oss-20b) documents Harmony/native
tool use. Its 21B total/3.6B active parameters are not a dense-model size comparison;
the published 16 GB memory claim does not guarantee large-context operation here.

**Inkling distinction and feasibility:** the requested local candidate is Inkling 2 Mini,
not the original 975B Inkling or 594B Inkling 2 Small shown on the
[official family page](https://thinkingmachines.ai/inkling/). The Mini
[official card](https://thinkingmachines.ai/model-card/inkling-2-mini/) describes a
looped MoE and recommends 32 GB Apple Silicon for the original approximately 20 GB checkpoint.
The [LM Studio listing](https://lmstudio.ai/models/inkling-2-mini) separately lists
an approximately 17.50 GB quantized download and 18 GB minimum RAM. The user's artifact
matches that quantized size. On 24 GiB it is a reasonable candidate to preflight, not a
promise of stable 32K context: the OS, host, runtime and KV cache also need memory.
Run one local model at a time, use text-only tasks, and measure peak memory/swap and
latency. Do not equate its advertised 1M context with practical capacity on this laptop.
If it cannot meet the main context allocation, report that and optionally run a
separately labelled lower-context condition; do not silently shrink all conditions.

**Hosted references:** [Luna](https://developers.openai.com/api/docs/models/gpt-6-luna)
and [Sol](https://developers.openai.com/api/docs/models/gpt-6.2-sol) have documented
function-calling support. Use the Responses API for the controlled API route. Luna's
Chat Completions tool route restricts reasoning to none, so mixing that route with
reasoning-enabled Sol would change the experiment. Access through a supported host
is also possible where the user's account provides it, but record host differences;
UI trials and an API runner are distinct configurations. API access is not confirmed
and no inference budget is spent by this plan.

A local controller can translate the model's function calls into local stdio MCP
calls; no publicly hosted Margin endpoint is needed. Budget model inference separately
from financial-provider usage. The official current model pages list standard per 1M
input/output rates of $0.10/$0.50 for Luna and $2/$10 for Sol; verify at execution time.
A task can make multiple model calls, and reasoning tokens/continued prompts affect
billing. Estimate from calibration usage, not a one-call-per-question assumption.

Match quantization/runtime formats where feasible; freeze them within each pair.
Thinking settings for Qwen3.5 use the documented API/template controls, not a presumed
Qwen3 /think soft switch. Do not treat architecture, quantization or runtime effects
as pure parameter-count effects. The [Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B)
and [Llama-3.1-8B](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) configurations
can remain legacy continuity controls rather than mandatory primary models. R1 distills
are supplementary candidates only after tool-call preflight; ambiguous UI labels must
be resolved to exact checkpoints. [GPT-5 mini](https://developers.openai.com/api/docs/models/gpt-5-mini)
is currently marked deprecated and is not the new hosted reference.

These choices are recommendations, not measured Margin benchmark rankings. Pin exact
available versions; if a hosted service exposes only a mutable alias, record returned
model ID/date and acknowledge drift. Do not replace a weak model after seeing scored
answers. Final cohort and common settings are frozen after calibration.

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
Six models × 40 tasks × two conditions × three repetitions = 1,440 scored responses
if all four local candidates and both hosted references are admitted. Four local models
alone would be 960. Exclude calibration/declared extensions from these counts. This is
a proposed model-run count, not an estimate of paid API requests or provider credits.

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
  enough. This is a study allocation, not any model's advertised maximum. No silent
  truncation or unnoticed RoPE-scaling change. If full 39 cannot fit, report the incompatibility; a focused
  profile is a separately declared study condition, not an unreported rescue.
- Preserve model-specific supported sampling settings rather than imposing an invalid
  universal temperature. For example, follow each Qwen version's thinking-mode guidance
  rather than assuming greedy decoding is appropriate. Keep choices and reasoning
  effort identical across that model's pair;
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

Qwen's emitted thinking blocks, gpt-oss's exposed analysis and Inkling's exposed thinking
can be retained when the runtime provides them. Inkling's looped computation makes
visible token length an especially poor proxy for total reasoning work; the official
[release discussion](https://thinkingmachines.ai/news/inkling-2-mini/) addresses monitorability.
Legacy Llama controls may have no dedicated reasoning channel: mark it unavailable,
not “no reasoning.” For hosted OpenAI models, request supported
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
