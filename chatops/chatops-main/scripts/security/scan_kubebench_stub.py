#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    report = {
        "ts": now_iso(),
        "tool": "kube-bench",
        "mode": "stub",
        "cis_profile": "generic",
        "summary": {"pass": 0, "fail": 0, "warn": 0},
        "notes": "CI should run kube-bench on cluster nodes; this is a placeholder artifact.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"kube-bench: stub out={out}")

if __name__ == "__main__":
    main()
