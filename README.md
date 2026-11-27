# Margin MCP

A local [Model Context Protocol](https://modelcontextprotocol.io/) server for Indian
listed-company research. Margin combines BharatStock REST and Drishti MCP data with
deterministic financial calculations, explicit-assumption DCF, and host-assisted
citation and content-sentiment review.

**Python 3.12+ · MIT · Windows, macOS and Linux**

The public distribution is **`margin-mcp`**; the Python import is **`margin`**. Version
**0.10.1**. Earlier local releases used the distribution name `margin-research`.
[Installation from source](#installation-from-source) is also supported.

## Install

Create a virtual environment and install from PyPI:

```sh
python -m venv .venv
# macOS/Linux
.venv/bin/python -m pip install margin-mcp
.venv/bin/margin-mcp --help
# Windows
.venv\Scripts\python.exe -m pip install margin-mcp
.venv\Scripts\margin-mcp.exe --help
```

No Node.js/npm, database or model server is required for Margin. Connect it to an MCP
host that can launch a local stdio server. The default profile exposes 39 tools;
optional `finance`, `review` and `review-simple` profiles expose focused views.

### Connect an MCP host

Merge this entry into your host's MCP server configuration. Replace the executable
path with your installation's absolute path. On Windows use the absolute
`.venv\\Scripts\\margin-mcp.exe` path with JSON-escaped backslashes.

```json
{
  "mcpServers": {
    "margin": {
      "command": "/absolute/path/.venv/bin/margin-mcp",
      "args": ["--mode", "live", "--tool-profile", "all"],
      "env": {
        "MARGIN_BHARATSTOCK_REQUESTS": "0",
        "MARGIN_DRISHTI_REQUESTS": "0",
        "MARGIN_DRISHTI_CREDITS": "0"
      }
    }
  }
}
```

Start with `margin_status` in the host. This configuration allows local discovery,
explicit-input calculations and supplied-text reviews while making no provider
requests. It does not authenticate provider access. Set explicit remaining process
allowances before authorizing live research; these are not account balances.

### Bring your own provider keys

Include only the providers you use in a private file outside the checkout:

```dotenv
BHARATSTOCK_API_KEY=YOUR_BHARATSTOCK_KEY
DRISHTI_API_KEY=YOUR_DRISHTI_KEY
```

Protect the file using your operating system's access controls. Add these two args to
the MCP configuration:

```json
["--credentials-file", "/absolute/private/providers.env"]
```

Keys can alternatively be passed through the MCP process environment. Margin does not
search for `.env` files automatically. Provider subscriptions, entitlements and usage
belong to each user. Keep keys out of prompts and tool arguments.
[Credential setup and precedence](https://github.com/rishitttt/margin-mcp/blob/main/docs/local-credentials.md).

## What you can do

- Retrieve supported financial, price, news, announcement and earnings records.
- Check company-data readiness and calculate margins, profitability, liquidity,
  cash-flow metrics, growth, CAGR and eligible quarterly TTM.
- Calculate FCFF, DCF, sensitivities and scenarios from explicit caller inputs.
- Review supplied passages using host judgments, exact quote/reference checks,
  citation rendering and bounded content-sentiment aggregation.

Results preserve units, periods, reporting basis, scope holds and unknown values.
DCF requires explicit forecasts and assumptions. Citation/sentiment judgments come
from the host; quote matching does not authenticate an original document or establish
market-wide investor sentiment. Provider-filtered records can still be irrelevant.

Margin retains bounded transient state and optional private diagnostic logs. Owner
restart loses transient handles and duplicate protection; it does not renew upstream
quota. Use stable keys to reconcile lost replies.
[Functions and limits](https://github.com/rishitttt/margin-mcp/blob/main/docs/financial-analysis.md),
[review workflows](https://github.com/rishitttt/margin-mcp/blob/main/docs/review-workflows.md).

## Optional local workbench and CLI

```sh
python -m pip install "margin-mcp[workbench]"
margin-workbench --mode synthetic
# In another terminal, using the same environment:
margin-agent --expect-mode synthetic status
```

The workbench serves a local UI/API at `http://127.0.0.1:8765`. Its synthetic mode uses
labelled fictional data. `margin-agent` calls that HTTP API; it needs a running
workbench. Activate the virtual environment or use absolute executable paths for
these commands. The workbench is optional; the base MCP installation does not need
FastAPI. The MCP SDK may install server libraries such as uvicorn transitively.

`margin-backend` is a separate, optional Unix-socket state owner for MCP frontends on
macOS/Linux. Windows uses standalone stdio. Backend/frontend versions must match.
[Standalone/shared setup](https://github.com/rishitttt/margin-mcp/blob/main/docs/mcp.md).

The optional [host skill](https://github.com/rishitttt/margin-mcp/tree/main/skills/margin-research)
is installed separately from the repository; pip does not install or activate skills.
[CLI and skill guide](https://github.com/rishitttt/margin-mcp/blob/main/docs/agent-interface.md).

## Installation from source

```sh
git clone https://github.com/rishitttt/margin-mcp.git
cd margin-mcp
python -m venv .venv
# Use .venv\Scripts\python.exe on Windows.
.venv/bin/python -m pip install .
# Optional UI/API:
.venv/bin/python -m pip install ".[workbench]"
```

To build and validate release artifacts:

```sh
.venv/bin/python -m pip install ".[dev,workbench,release]"
.venv/bin/python -m build
.venv/bin/python -m twine check --strict dist/*
.venv/bin/python scripts/check_distributions.py --version 0.10.1
```

Use a clean build directory. The sdist contains the self-contained product tests;
research/private-bundle tests remain repository-only. Software checks use fictional
fixtures and make no live provider requests.
[Release checks](https://github.com/rishitttt/margin-mcp/blob/main/docs/release-checks.md),
[validation evidence](https://github.com/rishitttt/margin-mcp/blob/main/docs/implementation.md),
[changelog](https://github.com/rishitttt/margin-mcp/blob/main/CHANGELOG.md).

## Authors and license

Rishit Anand, Advait Sharma, Arsalaan Alam, Tanvi Sanghai.

Licensed under [MIT](https://github.com/rishitttt/margin-mcp/blob/main/LICENSE).
Provider data and services remain subject to their own terms.
