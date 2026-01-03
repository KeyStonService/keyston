#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

def now_iso():
    return datetime.now(timezone.utc).isoformat()

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
