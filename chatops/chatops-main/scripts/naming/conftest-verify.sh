#!/usr/bin/env bash
set -euo pipefail
# Blocks on deny in real conftest usage. Here we enforce via python quick-check too.
python3 - <<'PY'
import json,sys
p="artifacts/reports/naming/compliance_report.json"
d=json.load(open(p))
v=int(d["summary"]["noncompliant"])
if v>0:
    print("naming-verify: FAIL violations=",v)
    sys.exit(2)
print("naming-verify: OK")
PY
