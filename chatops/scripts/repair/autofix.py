#!/usr/bin/env python3
import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

def now_iso():
    return datetime.now(timezone.utc).isoformat()

WHITELIST_ROOTS = ["scripts", "policies", "deployments", ".github", "artifacts", "var", "tests", "services", "proto"]

def ensure_file(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True

def is_allowed(path: Path) -> bool:
    parts = path.parts
    return len(parts) > 0 and parts[0] in WHITELIST_ROOTS

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    repo = Path(args.repo_root)
    trace_id = os.getenv("TRACE_ID", f"trace-autofix-{int(datetime.now().timestamp())}")

    changes = []

    # Safe: add missing placeholders
    for fp in [repo / "artifacts/.gitkeep", repo / "var/.gitkeep", repo / "policies/opa/.gitkeep"]:
        if is_allowed(fp) and ensure_file(fp, ""):
            changes.append({"type": "create", "path": str(fp.relative_to(repo)), "reason": "ensure directory placeholder exists"})

    # Safe: generate actions hardening report (does not modify workflows)
    report_path = repo / "artifacts/auto-fix/actions-hardening.report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)

    # Inline scanning to keep dependencies minimal
    unpinned = re.compile(r"uses:\s*[^@\s]+@v\d+", re.IGNORECASE)
    findings = []
    wf_root = repo / ".github/workflows"
    if wf_root.exists():
        for p in wf_root.rglob("*.yml"):
            txt = p.read_text(encoding="utf-8")
            for i, line in enumerate(txt.splitlines(), start=1):
                if "uses:" in line and unpinned.search(line):
                    findings.append({"file": str(p.relative_to(repo)), "line": i, "issue": "unpinned_action", "text": line.strip()})

    hardening = {"ts": now_iso(), "trace_id": trace_id, "summary": {"count": len(findings)}, "findings": findings}
    report_path.write_text(json.dumps(hardening, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = f"AutoFix applied {len(changes)} change(s). Findings={len(findings)} (workflows unpinned action scan)."
    report = {
        "ts": now_iso(),
        "trace_id": trace_id,
        "changes": changes,
        "summary": summary,
        "limits": {"whitelist_roots": WHITELIST_ROOTS},
        "reports": {"actions_hardening": str(report_path.relative_to(repo))}
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(summary)

if __name__ == "__main__":
    main()
