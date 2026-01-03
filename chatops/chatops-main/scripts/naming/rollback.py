#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys

# Add scripts directory to path for common utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_utils import now_iso  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--rto-minutes", type=int, default=20)
    args = ap.parse_args()

    report = {
        "ts": now_iso(),
        "rto_minutes": args.rto_minutes,
        "status": "simulated",
        "steps": [
            "restore previous manifests",
            "restore DNS records",
            "restore traffic routes",
            "verify service health"
        ],
        "verification": {"status": "pending"},
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"rollback: simulated out={out}")


if __name__ == "__main__":
    main()
