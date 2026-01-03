#!/usr/bin/env python3
import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

def now_iso():
    return datetime.now(timezone.utc).isoformat()

WAVES = [10, 25, 50, 100]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = Path(args.plan)
    items = []
    with plan.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        for row in r:
            items.append(row)

    total = len(items)
    waves = []
    for w in WAVES:
        count = (total * w) // 100 if w != 100 else total
        waves.append({"wave_percent": w, "apply_count": count, "status": "simulated"})

    report = {
        "ts": now_iso(),
        "plan": str(plan),
        "total_items": total,
        "waves": waves,
        "notes": "This is a simulation. Integrate with kubectl/kustomize/helm and cluster verification in CI/CD deploy stage.",
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"staged-rename: simulated waves={len(waves)} out={out}")

if __name__ == "__main__":
    main()
