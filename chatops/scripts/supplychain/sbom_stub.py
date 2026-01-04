#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--format", default="spdx-json")
    args = ap.parse_args()

    # Stub SBOM output: CI should replace with syft/grype integration.
    sbom = {
        "ts": now_iso(),
        "tool": "sbom-stub",
        "format": args.format,
        "components": [],
        "notes": "Replace with syft: syft dir:. -o spdx-json",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(sbom, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"sbom: stub out={out}")

if __name__ == "__main__":
    main()
