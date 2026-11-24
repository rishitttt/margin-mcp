# Portable local skill bundle

Updated **16 November 2026**. A private ZIP now includes the complete skill, runtime wheel, constrained dependencies, setup/server helpers, optional evaluation recorder, complete function reference and a generated offline schema catalog. At the user's explicit request, the local test ZIP also includes the existing BharatStock and Drishti trial keys in **`private/providers.env`**. They are not embedded in SKILL.md, source, prompts or logs. The ZIP is ignored/private and is not committed or pushed.

## Share and run

The produced archive is `reports/private/packages/margin-agent-local-2026-11-16.zip`. Share it privately with the local testers. It contains no previous financial responses, datasets, experiment logs, answer keys or workstation-specific `connection.json`.

```text
margin-agent-local/
  GETTING_STARTED.md
  margin_local.py
  margin-research/
    SKILL.md
    scripts/margin.py
    references/functions.md
    references/catalog.json
  runtime/
    margin_research-0.1.0-py3-none-any.whl
    requirements.lock
    pilot.py
  private/providers.env       # supplied trial keys; local/private only
  manifest.json
```

Extract before setup. Each tester needs Python 3.12+, shell execution and loopback/network access. From the extracted directory, write the actual evaluation question into `question.md`, then:

```sh
python3.12 margin_local.py setup --task-file question.md \
  --retention-until YYYY-MM-DD --agent-label HOST-MODEL-RUN
python3.12 margin_local.py serve --bharatstock-requests 1 \
  --drishti-requests 0 --drishti-credits 0
```

Replace the retention date and host/model label. Setup with a task explicitly enables private local recording, creates a virtual environment, installs the included wheel with the `workbench` extra, initializes one session and copies the skill into `workspace/.agents/skills/margin-research`. It does not query providers. Initial dependency installation needs internet; this is not an offline wheelhouse. The tested dependency snapshot is macOS/Python 3.12; clean dependency resolution on other platforms remains unverified.

The backend terminal stays running. Open a fresh chat in `workspace` and invoke `$margin-research` in Codex, giving the question and allowed call budget. Another host may use a different skill directory: setup `--target /absolute/path/to/that/host/skills/margin-research` installs there. A shell-capable host can also read the provided SKILL.md explicitly and execute `python3.12 margin_local.py agent ...`. Native skill discovery/support varies; packaging does not make a text-only chat execute Python. Actual host compatibility and model quality require host-specific pilots. If multiple skills share this name, select the full workspace skill path so it uses the intended recorder.

Setup regenerates local interpreter/backend/session paths. Move the bundle **before** setup. Use a fresh extracted copy for another agent/run; existing configured destinations are not overwritten. `--no-recording` explicitly selects ordinary unrecorded use. `--mode synthetic` is for fictional software tests; the default portable mode is live and the helper pins that expectation. No browser or Margin MCP server is required.

Selected Drishti testing requires appropriate process allowances and explicit operation opt-ins; see the archive's guide. Its connect/metadata/lifecycle traffic counts toward HTTP allowance. Default portable startup permits one BharatStock attempt and zero Drishti calls. All agents/copies with the same keys share actual account quotas; local counters do not coordinate across machines. The historical 25/day BharatStock and 1,000 one-off Drishti trial limits are not remaining-balance measurements. Restarting is not a quota reset. Rotate/update `private/providers.env` locally when needed; rebuild a new private ZIP to distribute new keys.

## Functionality described to agents

The [skill's function reference](../skills/margin-research/references/functions.md) names all 37 current retrieval/finance functions: six BharatStock retrieval operations, seven Drishti nested operations, fifteen explicit-input calculations and nine company workflows (plus ten review functions separately). Previously generated 16 November ZIPs retain their original inventory; this describes the current source/future builds. It also documents retained fact preparation, schemas, preview/run/idempotency, source reuse, shared budgets, connection, cancellation, status/history, logs and limitations. A test checks the inventory against the actual runtime registries. Exact schemas come from the running catalog; the generated offline catalog is a build-time reference, not evidence of live entitlement.

Citation verification, sentiment protocols, automatic source-backed company forecasting/DCF, the full professor evaluation harness and Margin's downstream MCP server remain unimplemented. A listed API operation may still be held or lack enough data for a particular calculation.

## What the evaluation log captures

Tool-helper calls automatically record sanitized responses, timestamps, backend identity, validated preview arguments and execution receipts. The skill additionally requests brief **visible decision summaries**, observations and limitations, submitted with:

```sh
python3.12 margin_local.py agent note --kind decision --file workspace/decision.md
python3.12 margin_local.py agent note --kind observation --file workspace/observation.md \
  --run-id RUN_ID --operation-id OPERATION_ID
python3.12 margin_local.py agent finish --answer-file workspace/final.md
```

The summary covers the goal/tool choice, a material result or a limitation. It is labelled `origin: agent_self_report`, `is_hidden_reasoning: false`, with instrumentation version `visible-summaries-v1`. It is not hidden chain of thought, proof of faithful internal reasoning or an independent evaluation. The skill cannot force an agent to submit a note; finish reports actual summary/tool counts and flags missing summaries. Asking for summaries is itself an experiment condition: hold it constant or compare it separately across agents.

Sessions under `private/sessions/<id>/` contain task/host labels, backend pin, chronological `events.jsonl` and final `answer.json`. A configured provider credential file redacts notes, task text, results and answers. Directories/files are restricted; logs remain bounded and expire for new actions at the review date. Expiration does not delete files. Do not place answer keys in the skill/workspace. Review/delete private logs manually.

Complete host conversations, omitted notes or tool calls outside this helper are not captured. A future host adapter can collect exposed messages/reasoning summaries where supported; raw internal reasoning is not accessible through this skill. Full replay, fixed task/gold records and independent grading remain separate work. Official references: [skill format/discovery](https://learn.chatgpt.com/docs/build-skills), [OpenAI reasoning summaries](https://developers.openai.com/api/docs/guides/reasoning).

## Rebuild and verify

```sh
.venv/bin/python scripts/package_agent_bundle.py --include-keys \
  --output reports/private/packages/NEW-PRIVATE-NAME.zip
.venv/bin/python scripts/smoke_agent_bundle.py \
  reports/private/packages/NEW-PRIVATE-NAME.zip --port 8796
```

Omit `--include-keys` for a keyless bundle. Packaging refuses existing outputs and checks that credentials occur only in the designated private file, including checking compressed wheel contents. The ZIP is created with permissions 0600. Keep credential-bearing output outside Git or in an ignored location; the builder enforces that inside this repository. It makes no provider calls.

The process acceptance test relocates the extracted bundle into a path with spaces, uses an explicitly preinstalled runtime (`--skip-install`), starts a fictional backend, exercises tools/idempotency and summary/final logging, checks redaction, then removes the private test copy and stops the server. It does **not** validate a fresh internet dependency install or a model deciding which tools to use. Dated checks belong in [implementation status](implementation.md).
