#!/usr/bin/env bash
set -euo pipefail

MODE="${1:-}"
if [[ "${MODE}" == "--check-only" ]]; then
  python3 - <<'PY'
import yaml,sys
d=yaml.safe_load(open("gate-lock-attest.yaml"))
if d.get("spec",{}).get("frozen",False):
    print("freeze gate active")
    sys.exit(2)
print("freeze gate not active")
PY
  exit 0
fi

python3 - <<'PY'
import yaml
p="gate-lock-attest.yaml"
d=yaml.safe_load(open(p))
d.setdefault("spec",{})
d["spec"]["frozen"]=True
d["spec"]["reason"]="manual freeze via scripts/freeze-deploy.sh"
open(p,"w",encoding="utf-8").write(yaml.safe_dump(d,sort_keys=False))
print("freeze: enabled")
PY
