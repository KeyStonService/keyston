#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path
import sys

# Add scripts directory to path for common utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_utils import now_iso  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--event", required=True)
    ap.add_argument("--actor", default=os.getenv("GITHUB_ACTOR", "local"))
    ap.add_argument("--why", default="")
    ap.add_argument("--how", default="")
    ap.add_argument("--trace-id", default=os.getenv("TRACE_ID", "trace-local"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rec = {
        "ts": now_iso(),
        "trace_id": args.trace_id,
        "actor": args.actor,
        "event": args.event,
        "why": args.why,
        "how": args.how,
        "env": os.getenv("DEPLOY_TARGET", "dev"),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"audit: appended -> {out}")


if __name__ == "__main__":
    main()
