#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))

def compute_score(metrics: dict) -> float:
    pylint = clamp(float(metrics.get("pylint_score_0_100", 0.0)))
    coverage = clamp(float(metrics.get("coverage_0_100", 0.0)))
    security = clamp(float(metrics.get("security_score_0_100", 100.0)))
    naming = clamp(float(metrics.get("naming_compliance_0_100", 100.0)))
    # weights
    return round((pylint*0.25 + coverage*0.35 + security*0.25 + naming*0.15), 1)

def gate_status(score: float, branch: str) -> str:
    if branch == "main":
        thr = 85.0
    elif branch == "develop":
        thr = 75.0
    else:
        thr = 70.0
    return "pass" if score >= thr else "block"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    trace_id = os.getenv("TRACE_ID", "trace-local")
    branch = os.getenv("BRANCH_NAME", os.getenv("GITHUB_REF_NAME", "local"))

    # minimal metrics placeholders (CI workflows may overwrite by injecting env/json)
    metrics = {
        "pylint_score_0_100": float(os.getenv("PYLINT_SCORE_0_100", "0")),
        "coverage_0_100": float(os.getenv("COVERAGE_0_100", "0")),
        "security_score_0_100": float(os.getenv("SECURITY_SCORE_0_100", "100")),
        "naming_compliance_0_100": float(os.getenv("NAMING_COMPLIANCE_0_100", "100")),
    }

    score = compute_score(metrics)
    status = gate_status(score, branch)

    report = {
        "ts": now_iso(),
        "trace_id": trace_id,
        "branch": branch,
        "metrics": metrics,
        "quality_score": score,
        "gate_status": status,
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"quality-gates: {status} score={score} out={out}")

if __name__ == "__main__":
    main()
