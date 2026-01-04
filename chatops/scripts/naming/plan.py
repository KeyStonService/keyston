#!/usr/bin/env python3
import argparse
import csv
import json
import re
from pathlib import Path

NAME_PATTERN = re.compile(r"^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\d+\.\d+\.\d+(-[A-Za-z0-9]+)?$")

def suggest_name(kind: str, raw_name: str, env: str = "prod", app: str = "chatops") -> str:
    kind_map = {
        "Deployment": "deploy",
        "Service": "svc",
        "Ingress": "ing",
        "ConfigMap": "cm",
        "Secret": "secret",
    }
    suffix = kind_map.get(kind, "cm")
    # minimal deterministic suggestion
    return f"{env}-{app}-{suffix}-v1.0.0"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discovery", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    discovery = json.loads(Path(args.discovery).read_text(encoding="utf-8"))
    rows = []
    for r in discovery.get("resources", []):
        if r.get("compliant"):
            continue
        rows.append({
            "file": r["file"],
            "kind": r["kind"],
            "current_name": r["name"],
            "suggested_name": suggest_name(r["kind"], r["name"]),
            "action": "rename",
            "dry_run": "true",
        })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["file","kind","current_name","suggested_name","action","dry_run"])
        w.writeheader()
        for row in rows:
            w.writerow(row)

    print(f"naming-plan: out={out} rows={len(rows)}")

if __name__ == "__main__":
    main()
