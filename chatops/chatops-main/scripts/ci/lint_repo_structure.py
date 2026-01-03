#!/usr/bin/env python3
from pathlib import Path
import sys

REQUIRED_DIRS = [
    Path(".github/workflows"),
    Path("scripts"),
    Path("policies"),
    Path("deployments"),
]

REQUIRED_FILES = [
    Path("scripts/requirements.txt"),
    Path("policies/opa/naming.rego"),
    Path("policies/opa/naming_test.rego"),
    Path("policies/conftest.toml"),
]

def main() -> int:
    missing = []
    for d in REQUIRED_DIRS:
        if not d.exists():
            missing.append(str(d))
    for f in REQUIRED_FILES:
        if not f.exists():
            missing.append(str(f))

    if missing:
        print("repo-structure: FAIL")
        for m in missing:
            print(f"- missing: {m}")
        return 2

    print("repo-structure: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
