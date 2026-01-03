#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    # Stub report to keep repo runnable without external binary.
    # CI can replace with real Checkov execution.
    root = Path(args.root)
    report = {
        "ts": now_iso(),
        "tool": "checkov",
        "mode": "stub",
        "root": str(root),
        "summary": {"passed": 0, "failed": 0, "skipped": 0},
        "notes": "Install and run real checkov in hardened CI if required.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"checkov: stub out={out}")

if __name__ == "__main__":
    main()
