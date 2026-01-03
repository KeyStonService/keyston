#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = Path(args.plan)
    changes = []
    with plan.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            changes.append({
                "file": row["file"],
                "kind": row["kind"],
                "from": row["current_name"],
                "to": row["suggested_name"],
                "dry_run": True,
                "status": "simulated",
            })

    report = {
        "ts": now_iso(),
        "plan": str(plan),
        "changes": changes,
        "summary": {
            "total": len(changes),
            "simulated": len(changes),
        }
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"naming-dryrun: out={out} changes={len(changes)}")

if __name__ == "__main__":
    main()
