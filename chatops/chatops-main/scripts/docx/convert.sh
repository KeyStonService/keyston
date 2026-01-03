#!/usr/bin/env bash
set -euo pipefail

SOURCES="${1:-artifacts/sources}"
MODULES="${2:-artifacts/modules}"
REPORTS="${3:-artifacts/reports}"
FAIL_ON_ERROR="${4:-true}"

mkdir -p "${SOURCES}" "${MODULES}" "${REPORTS}"

# Stub converter: just inventories files to a report.
python3 - <<PY
import json,sys
from pathlib import Path
src=Path("${SOURCES}")
items=[]
for p in src.rglob("*"):
    if p.is_file():
        items.append({"file":str(p),"size":p.stat().st_size})
rep={"tool":"docx-to-artifact","mode":"stub","sources":items}
Path("${REPORTS}").mkdir(parents=True, exist_ok=True)
Path("${REPORTS}") .joinpath("docx-conversion.report.json").write_text(json.dumps(rep,indent=2),encoding="utf-8")
print("docx-convert: wrote", "${REPORTS}/docx-conversion.report.json")
PY
