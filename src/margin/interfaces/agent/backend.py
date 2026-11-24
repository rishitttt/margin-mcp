"""Explicit backend launcher for a private portable test bundle."""

import argparse
import json
from dataclasses import replace

from margin.core.config import Settings
from margin.core.contracts import DomainError
from margin.interfaces.agent.client import BridgeError
from margin.interfaces.agent.local_config import read_provider_env


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--credentials-file")
    parser.add_argument("--mode", choices=["live", "synthetic"], default="live")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--bharatstock-requests", type=int, default=1)
    parser.add_argument("--drishti-requests", type=int, default=0)
    parser.add_argument("--drishti-credits", type=int, default=0)
    parser.add_argument("--enable-operations", default="")
    args = parser.parse_args(argv)
    try:
        if not 1 <= args.port <= 65535:
            raise BridgeError("invalid_config", "Use a valid local TCP port.")
        credentials = read_provider_env(args.credentials_file) if args.credentials_file else {}
        base = Settings.from_env()
        settings = replace(
            base,
            mode=args.mode,
            bharatstock_key=credentials.get("BHARATSTOCK_API_KEY", base.bharatstock_key),
            drishti_key=credentials.get("DRISHTI_API_KEY", base.drishti_key),
            bharatstock_requests=args.bharatstock_requests,
            drishti_requests=args.drishti_requests,
            drishti_credits=args.drishti_credits,
            enabled_unverified=frozenset(filter(None, args.enable_operations.split(","))),
            synthetic_fault="none",
        )
        import uvicorn

        from margin.interfaces.workbench.app import create_app

        print(
            f"Margin backend: http://127.0.0.1:{args.port} — {settings.mode.upper()}; process counters are not account quota."
        )
        uvicorn.run(
            create_app(settings),
            host="127.0.0.1",
            port=args.port,
            workers=1,
            reload=False,
            access_log=False,
            log_level="warning",
        )
        return 0
    except (BridgeError, DomainError) as error:
        print(json.dumps({"error": {"code": error.code, "message": error.message}}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
