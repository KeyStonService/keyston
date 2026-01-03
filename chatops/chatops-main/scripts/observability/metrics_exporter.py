#!/usr/bin/env python3
"""
A tiny Prometheus textfile exporter for naming governance metrics (local/dev).
In prod, export via service endpoint or pushgateway.
"""
import argparse
import json
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--discovery", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--env", default="prod")
    args = ap.parse_args()

    discovery = json.loads(Path(args.discovery).read_text(encoding="utf-8"))
    rate = float(discovery["summary"]["compliance_rate"]) / 100.0
    violations = int(discovery["summary"]["noncompliant"])

    lines = []
    lines.append(f'chatops_naming_compliance_rate{{env="{args.env}"}} {rate}')
    lines.append(f'chatops_naming_violations_total{{env="{args.env}"}} {violations}')
    # Placeholder rates (populated by CI in future)
    lines.append(f'chatops_naming_autofix_success_rate{{env="{args.env}"}} 0')
    lines.append(f'chatops_naming_autofix_failure_rate{{env="{args.env}"}} 0')

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"metrics: wrote {out}")

if __name__ == "__main__":
    main()
