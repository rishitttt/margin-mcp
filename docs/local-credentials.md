# Local users: bring your own provider keys

Margin 0.10.1 supports each user supplying their own BharatStock and/or Drishti
key. The package contains no provider credentials. Provider access/limits belong to the
user's account; installing Margin does not include a provider subscription.

## Standalone MCP: private file

Create a private file outside the project, for example /absolute/private/providers.env:

```dotenv
BHARATSTOCK_API_KEY=YOUR_BHARATSTOCK_KEY
DRISHTI_API_KEY=YOUR_DRISHTI_KEY
```

Include only providers you use. On macOS/Linux, use `chmod 600 /absolute/private/providers.env` and keep its parent
directory private. On Windows use a private user directory and appropriate file access.
Use an absolute path in the host config; do not assume tilde or shell expansion.

Configure the host to start the absolute installed margin-mcp executable, with args:

```json
["--mode", "live", "--credentials-file", "/absolute/private/providers.env", "--tool-profile", "all"]
```

Set these separately in the MCP process environment, initially zero for local checks:

```json
{
  "MARGIN_BHARATSTOCK_REQUESTS": "0",
  "MARGIN_DRISHTI_REQUESTS": "0",
  "MARGIN_DRISHTI_CREDITS": "0"
}
```

Allocate confirmed remaining provider usage before live execution. These are local
process ceilings, not provider account balances/daily quotas. Startup/status/catalog
alone do not authenticate keys or fetch company data. Explicit live execution uses
that user's account; Drishti connection/cleanup also consumes HTTP allowance.

## Environment alternative

The process can instead receive BHARATSTOCK_API_KEY and DRISHTI_API_KEY through the
host's environment/secrets configuration. Omit --credentials-file in that case. The
host must actually pass the values to the child process; exporting a variable in an
unrelated terminal may not reach a desktop app. Do not paste keys into tool arguments
or model prompts. A credential file avoids putting the key values in MCP JSON itself.

## File behavior and precedence

- Keys in an explicitly supplied credentials file override environment values per key.
- Missing file entries fall back to that process's environment.
- Only the two provider key names are read from this file. MARGIN_* limits belong in
  the process environment, not this credentials file.
- No automatic .env search/loading occurs. A file named .env must still be passed
  explicitly using --credentials-file, or its values supplied through the environment.
- Changing the file does not hot-reload a running owner. An intentional owner restart
  loads new configuration and loses transient state; it does not replenish account quota.
- A configured key is not proof of live authentication/entitlement. Status reports the
  distinction; no balance probe is implied.

## Optional shared backend

For shared macOS/Linux mode, provide --credentials-file (or key environment variables)
and allowance variables to margin-backend, the actual state owner. The margin-mcp
frontend connects with --backend-socket and does not load/change the owner's keys or
budgets. Do not put --credentials-file on the proxy frontend. Standalone is the Windows
route. See [connection instructions](mcp.md).

All provider calls are made from the user's machine to the upstream providers. Margin
runs no hosted credential service. Optional logs are local/private and sanitized; never
bundle credentials or private test captures in a public wheel, sdist or skill package.
The old explicitly private agent bundles are not public distribution artifacts.
