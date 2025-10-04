#!/usr/bin/env python3
"""Environment validation script (Story S4).
Validates presence (and basic shape) of required environment variables.
Extend with type/format validation as project evolves.
"""
from __future__ import annotations
import os
import sys
import json

REQUIRED_VARS = [
    "APP_ENV",
    "API_PORT",
    "LOG_LEVEL",
]

OPTIONAL_VARS = [
    "OTEL_EXPORTER_OTLP_ENDPOINT",
]

def main() -> int:
    missing = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing.append(var)
    result = {
        "required_total": len(REQUIRED_VARS),
        "missing": missing,
        "ok": not missing,
    }
    print(json.dumps(result))
    return 0 if not missing else 1

if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
