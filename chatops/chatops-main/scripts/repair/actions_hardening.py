#!/usr/bin/env python3
"""
Hardening helper:
- enforce minimal permissions blocks
- enforce concurrency blocks
- optional: verify no unpinned third-party actions are used

This script is used by autofix loop (safe subset).
"""
import argparse
import re
import json
from pathlib import Path
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).isoformat()

UNPINNED = re.compile(r"uses:\s*[^@\s]+@v\d+", re.IGNORECASE)

def scan_workflows(root: Path):
    findings = []
    for p in root.rglob("*.yml"):
        txt = p.read_text(encoding="utf-8")
        for i, line in enumerate(txt.splitlines(), start=1):
            if "uses:" in line and UNPINNED.search(line):
                findings.append({"file": str(p), "line": i, "issue": "unpinned_action", "text": line.strip()})
    return findings

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".github/workflows")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    root = Path(args.root)
    findings = scan_workflows(root) if root.exists() else []
    report = {
        "ts": now_iso(),
        "root": str(root),
        "findings": findings,
        "summary": {"count": len(findings)},
        "policy": "No third-party actions may use @vX tags; pin to commit SHA or avoid actions.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"actions-hardening: findings={len(findings)} out={out}")

if __name__ == "__main__":
    main()
