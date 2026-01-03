#!/usr/bin/env python3
import argparse
import json
import subprocess
from pathlib import Path

def which(cmd: str) -> bool:
    from shutil import which as w
    return w(cmd) is not None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--policy-dir", required=True)
    ap.add_argument("--target-dir", required=True)
    args = ap.parse_args()

    if not which("conftest"):
        print("conftest not found. Install: https://www.conftest.dev/")
        print("policy: FAIL (missing conftest)")
        raise SystemExit(2)

    policy_dir = Path(args.policy_dir)
    target_dir = Path(args.target_dir)

    if not policy_dir.exists() or not target_dir.exists():
        print("policy: FAIL (missing policy-dir or target-dir)")
        raise SystemExit(2)

    cmd = ["conftest", "test", str(target_dir), "--policy", str(policy_dir)]
    p = subprocess.run(cmd, text=True)
    raise SystemExit(p.returncode)

if __name__ == "__main__":
    main()
