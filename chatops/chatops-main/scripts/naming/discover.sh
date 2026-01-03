#!/usr/bin/env bash
set -euo pipefail
mkdir -p artifacts/reports/naming
python3 - <<'PY'
import json, re
from pathlib import Path
pattern=re.compile(r"^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\d+\.\d+\.\d+(-[A-Za-z0-9]+)?$")
items=[]
for p in Path("deploy").rglob("*.y*ml"):
    try: txt=p.read_text(encoding="utf-8")
    except Exception: continue
    kind=name=None
    for line in txt.splitlines():
        s=line.strip()
        if s.startswith("kind:") and not kind: kind=s.split(":",1)[1].strip()
        if s.startswith("name:") and not name: name=s.split(":",1)[1].strip().strip('"').strip("'")
    if kind and name:
        items.append({"file":str(p),"kind":kind,"name":name,"compliant":bool(pattern.match(name)),"pattern":pattern.pattern})
total=len(items); comp=sum(1 for x in items if x["compliant"])
rep={"version":"1.0","generatedAt":"1970-01-01T00:00:00Z","pattern":pattern.pattern,
     "summary":{"total":total,"compliant":comp,"noncompliant":total-comp,"compliance_rate": (comp/total) if total else 1.0},
     "violations":[x for x in items if not x["compliant"]]}
Path("artifacts/reports/naming/compliance_report.json").write_text(json.dumps(rep,ensure_ascii=False,indent=2),encoding="utf-8")
print("naming-discovery: total",total,"violations",total-comp)
PY
