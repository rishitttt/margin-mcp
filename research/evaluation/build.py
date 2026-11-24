"""Build private, separate live-task and evaluator archives; performs no provider calls."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime, timedelta
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from margin.core.config import Settings
from margin.core.registry import Registry
from research.evaluation.spec import (
    AS_OF,
    BENCHMARK_ID,
    TASKS,
    answer_schema,
    task_document,
    template,
)

R_URL = "https://www.ril.com/ar2025-26/pdf/07_RIL_IAR_2025-26_Consolidated_22-05-26.pdf"
T_URL = "https://www.tcs.com/content/dam/tcs/investor-relations/financial-statements/2025-26/q4/IND%20AS/Consolidated.pdf"


def gold_key(path=None):
    """Load operator-supplied private gold; never embed benchmark answers in public source."""
    path = (
        Path(path)
        if path
        else Path(__file__).resolve().parents[2]
        / "reports/private/evaluation/gold-inputs-2026-11-16.json"
    )
    try:
        gold = json.loads(path.read_text())
    except (OSError, ValueError):
        raise ValueError(
            "Provide the separately retained evaluator key with --gold-file; no public numerical key is bundled."
        ) from None
    if (
        not isinstance(gold, dict)
        or gold.get("benchmark_id") != BENCHMARK_ID
        or gold.get("as_of") != AS_OF
        or gold.get("task_ids") != [task[0] for task in TASKS]
        or not isinstance(gold.get("expected"), dict)
        or not gold["expected"]
    ):
        raise ValueError("Private evaluator key does not match this historical task contract.")
    return gold


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def archive_folder(folder, output):
    descriptor = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream, ZipFile(stream, "w", ZIP_DEFLATED) as archive:
            for path in sorted(folder.rglob("*")):
                if path.is_file():
                    archive.write(path, str(Path(folder.name) / path.relative_to(folder)))
    except BaseException:
        output.unlink(missing_ok=True)
        raise


def build(root, output_dir, wheel, gold_file=None):
    gold = gold_key(gold_file)
    output_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    runner_zip = output_dir / "margin-live-test-runner-v1.zip"
    evaluator_zip = output_dir / "margin-live-test-evaluator-v1.zip"
    if runner_zip.exists() or evaluator_zip.exists():
        raise ValueError("Use a fresh output directory; packages are not overwritten")
    spec = importlib.util.spec_from_file_location(
        "margin_bundle_builder", root / "scripts/package_agent_bundle.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    until = (datetime.now(UTC) + timedelta(days=14)).date().isoformat()
    enabled = ",".join(x["operation"] for x in Registry(Settings()).capabilities())
    with tempfile.TemporaryDirectory(prefix="eval-package-", dir=output_dir) as temporary:
        temp = Path(temporary)
        base_zip = temp / "base.zip"
        module.build_bundle(root, base_zip, wheel, include_keys=True)
        with ZipFile(base_zip) as archive:
            archive.extractall(temp)
        runner = temp / "margin-agent-local"
        (runner / "TASK.md").write_text(task_document())
        write_json(runner / "answer-schema.json", answer_schema())
        (runner / "workspace").mkdir()
        write_json(runner / "workspace/answers.json", template())
        (runner / "workspace/report.md").write_text(
            "# Run report\n\nReplace with concise findings and limitations.\n"
        )
        shutil.copy2(root / "research/evaluation/submit.py", runner / "runtime/submit.py")
        prompt = """Read ../TASK.md and .agents/skills/margin-research/SKILL.md. Carry out the two-ticker LIVE evaluation using that local skill and the already-running backend. Exclude DCF/FCFF, use --why for one-line tool-choice explanations, preserve the configured session and budgets. Write answers.json and report.md in this workspace, finish using the exact answers.json, then export with ../margin_local.py submit. Do not access evaluator files or any other Margin checkout, use replay/synthetic data, change allowances or restart the backend. If a provider branch is blocked or uncertain, report it rather than retrying/bypassing it. Return submission.zip to me. You are authorized to make fresh provider calls within the configured task budget."""
        (runner / "AGENT_PROMPT.txt").write_text(prompt + "\n")
        (runner / "START_HERE.md").write_text(f"""# Run the live skill test

This is the RUNNER only. Keep the evaluator ZIP away from the tested agent. Trial keys
are already in private/providers.env; do not paste them into chat. Both APIs require
internet; initial setup also downloads pinned Python dependencies. Python >=3.12 required.
No live calls happen during setup. Tested locally on macOS, other host setups unverified.

1. Extract into a NEW folder outside the development repository. Keep that location.
2. In Terminal, cd into the extracted margin-agent-local folder and run:

```sh
python3.12 margin_local.py setup --task-file TASK.md --retention-until {until} --agent-label codex-run-01
python3.12 margin_local.py serve --bharatstock-requests 10 --drishti-requests 40 --drishti-credits 10 --enable-operations {enabled}
```

Leave this terminal running. The second command starts LIVE mode. Enable flags admit
reviewed operations only; changed contracts remain held. Do not restart to reset counters.
Use setup --port 8766 in a fresh extracted copy if 8765 is already occupied.

3. Open the extracted **workspace** folder in a fresh agent chat with shell access.
Paste AGENT_PROMPT.txt. Explicitly point at this copy's local SKILL.md if another global
Margin skill exists. The agent fills answers.json and report.md, records its final JSON,
and exports submission.zip. The output contains answers plus sanitized tool logs and
visible one-line explanations. It contains neither provider keys nor hidden reasoning.
If the host has no automatic skill discovery, have it read the local SKILL.md explicitly.

4. Send **submission.zip** back in our original chat for evaluation. If export was missed,
from the bundle root run `python3.12 margin_local.py submit` after finish was successful.
Stop the backend with Ctrl-C after export. Never upload the original runner ZIP publicly.

Each agent needs a fresh extracted copy/session. Run sequentially: all copies share the
same real account quotas (BharatStock Free historically 25/day), while process limits do
not coordinate across copies. This run permits at most 10 B attempts, 40 D HTTP attempts
including metadata, and 10 estimated D credits. Current remaining account quotas are
not guaranteed; report quota failures without retries. No new paid key is required just
to attempt one bounded run with available trial allowance.

The task date/windows are fixed at {AS_OF}; use the same task for comparisons. Retention
is a manual review/delete date, not automatic deletion. Separate ZIPs prevent accidental
answer-key inclusion; they are not a filesystem security boundary. For stronger isolation,
mount only the runner/workspace into the tested host. This is a private pilot, not a full
model runner or final scientific benchmark. No agent has completed this evaluation yet.
""")
        manifest = json.loads((runner / "manifest.json").read_text())
        manifest.update(
            benchmark_id=BENCHMARK_ID,
            instrumentation="visible-tool-choice-v2",
            task_sha256=hashlib.sha256((runner / "TASK.md").read_bytes()).hexdigest(),
        )
        write_json(runner / "manifest.json", manifest)
        evaluator = temp / "margin-live-evaluator"
        evaluator.mkdir()
        write_json(evaluator / "gold.json", gold)
        write_json(evaluator / "answer-schema.json", answer_schema())
        shutil.copy2(root / "research/evaluation/grade.py", evaluator / "grade.py")
        primary = evaluator / "primary-sources"
        primary.mkdir()
        source_pdf = root / "reports/private/eval-sources/reliance-fy2026-consolidated.pdf"
        if source_pdf.exists():
            shutil.copy2(source_pdf, primary / source_pdf.name)
        write_json(primary / "sources.json", gold["sources"])
        (evaluator / "README.md").write_text("""# Private evaluator — never give to tested agent

Contains independent issuer financial targets, independently calculated formulas,
primary source locators/pages, an archived RIL PDF and an offline receipt checker.
TCS primary source was read through the web parser; local fetch returned 403. Financial
review status is explicit in gold.json: independent human approval is still pending.

Run with Python >=3.12, no API keys or network required:

```sh
python3.12 grade.py /absolute/path/submission.zip --output evaluation.json
```

This checks fixed annual financial values, derived arithmetic and selected live-receipt
fidelity. It reports tool coverage and missing/blocked conditions separately. Review all
manual_review entries in gold.json: news relevance, definitions, citation support, periods,
identity resolution, limits, null explanations and safety decisions need human review.
The automatic percentage is not an overall scientific score. A correct number with any
trace reference still needs a reviewer to confirm the reference supports that number.

Important preparation findings (not universal expectations): quarterly start dates and
CFO were missing; TTM should not invent boundaries/zeros. Drishti announcements were held
for schema change. RELIANCE earnings listing for the specified historical window returned
empty, so no detail was requested. Empty is not evidence that no release occurred.
TCS FY26 primary cash PPE 3670 + intangible 367 = 4037 crore. API-labelled capex was 4078;
primary CFO 52094 gives 48057 versus API-input CFO-minus-capex 48016. Report this definition
gap separately from whether the function correctly subtracts its supplied inputs.

Ground truth scope: annual amounts/EPS are source-backed. Cash-capex arithmetic and live
prices are checked against THIS submitted run, not treated as independently verified
exchange truth. Latest news/prices can change. All numeric checks have explicit units,
periods/basis and tolerances. The source-selected annual numbers and manual checks must
be reviewed before a publication-quality study. No completed model evaluation is claimed.

Logs contain observable tool results and agent-authored one-line decision summaries.
They do not capture hidden reasoning or prove explanations faithful. Export hashes detect
post-export accidental changes, not authenticity/tamper resistance. Inspect the submitted
report plus logs when attributing model/tool/provider errors. There is no full host transcript.

Preparation budget, 16 November: four BharatStock financial calls succeeded. Drishti used
23 SDK HTTP requests across three metadata sessions, plus eight direct diagnostic requests
(two used the frontend origin by mistake). Five successful/empty data operations and one
pre-dispatch announcement block were observed. Estimated credits 5; observed actual trial
balance 961 to 958 (3 charged). These are preparation costs, not an account-quota promise.
Runner contains no preparation responses or answer key. DCF/FCFF/sensitivity/scenarios
are excluded. Existing direct-quote retrieval may remain unexercised; coverage is reported,
not inflated by forcing unnecessary calls. Never include evaluator files in agent submissions.
""")
        write_json(
            evaluator / "pair-manifest.json",
            {
                "benchmark_id": BENCHMARK_ID,
                "runner_task_sha256": manifest["task_sha256"],
                "runtime_wheel_sha256": manifest["wheel_sha256"],
                "source_pdf_sha256": hashlib.sha256(source_pdf.read_bytes()).hexdigest()
                if source_pdf.exists()
                else None,
            },
        )
        # The final runner must contain secrets only in the explicitly authorized env file.
        from margin.interfaces.agent.local_config import read_provider_env

        secrets = read_provider_env(root / ".env").values()
        for folder in (runner, evaluator):
            for path in folder.rglob("*"):
                if path.is_file() and path != runner / "private/providers.env":
                    if any(value.encode() in path.read_bytes() for value in secrets):
                        raise ValueError("Credential spill outside designated runner env file")
        archive_folder(runner, runner_zip)
        try:
            archive_folder(evaluator, evaluator_zip)
        except BaseException:
            runner_zip.unlink(missing_ok=True)
            raise
    return {
        "runner": str(runner_zip),
        "evaluator": str(evaluator_zip),
        "provider_calls_during_build": 0,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument(
        "--gold-file", type=Path, help="Private evaluator key; excluded from runner and Git"
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--no-isolation"],
        cwd=root,
        stdout=subprocess.DEVNULL,
        check=True,
    )
    wheel = max((root / "dist").glob("margin_research-*.whl"), key=lambda p: p.stat().st_mtime)
    print(json.dumps(build(root, args.output_dir.resolve(), wheel, args.gold_file)))


if __name__ == "__main__":
    main()
