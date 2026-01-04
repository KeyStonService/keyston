#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

def run(cmd):
    p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if p.returncode != 0:
        print(p.stdout)
    return p.returncode

def main() -> int:
    py_files = []
    for root in ["scripts", "services"]:
        r = Path(root)
        if r.exists():
            py_files += [str(p) for p in r.rglob("*.py") if "node_modules" not in p.parts and ".venv" not in p.parts]

    if not py_files:
        print("lint-python: SKIP (no python files)")
        return 0

    # basic syntax check
    bad = 0
    for f in py_files:
        rc = run([sys.executable, "-m", "py_compile", f])
        if rc != 0:
            bad += 1
    if bad:
        print(f"lint-python: FAIL (syntax errors={bad})")
        return 2

    print("lint-python: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
