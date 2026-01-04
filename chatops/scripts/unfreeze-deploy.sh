#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import yaml
p="gate-lock-attest.yaml"
d=yaml.safe_load(open(p))
d.setdefault("spec",{})
d["spec"]["frozen"]=False
d["spec"]["reason"]="unfreeze"
open(p,"w",encoding="utf-8").write(yaml.safe_dump(d,sort_keys=False))
print("freeze: disabled")
PY
