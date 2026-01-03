#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Add scripts directory to path for common utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_utils import now_iso, write_json_report  # noqa: E402


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
    write_json_report(args.out, report)
    print(f"kube-bench: stub out={args.out}")


if __name__ == "__main__":
    main()
