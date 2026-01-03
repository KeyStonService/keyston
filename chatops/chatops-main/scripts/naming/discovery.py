#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path
from datetime import datetime, timezone

NAME_PATTERN = re.compile(r"^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\d+\.\d+\.\d+(-[A-Za-z0-9]+)?$")

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def scan_k8s_yaml(root: Path):
    items = []
    for p in root.rglob("*.y*ml"):
        try:
            text = p.read_text(encoding="utf-8")
        except Exception:
            continue
        # super-light parser: find lines "kind:" and "name:"
        kind = None
        name = None
        for line in text.splitlines():
            s = line.strip()
            if s.startswith("kind:"):
                kind = s.split(":", 1)[1].strip()
            if s.startswith("name:") and name is None:
                name = s.split(":", 1)[1].strip().strip('"').strip("'")
        if kind and name:
            ok = bool(NAME_PATTERN.match(name))
            items.append({
                "file": str(p),
                "kind": kind,
                "name": name,
                "compliant": ok,
                "pattern": NAME_PATTERN.pattern,
            })
    return items

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    report = {
        "ts": now_iso(),
        "root": str(root),
        "resources": scan_k8s_yaml(root),
    }
    total = len(report["resources"])
    compliant = len([r for r in report["resources"] if r["compliant"]])
    report["summary"] = {
        "total": total,
        "compliant": compliant,
        "noncompliant": total - compliant,
        "compliance_rate": round((compliant / total) * 100, 2) if total else 100.0
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"naming-discovery: out={out} compliance={report['summary']['compliance_rate']}%")

if __name__ == "__main__":
    main()
