#!/usr/bin/env python3
import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

def now_iso():
    return datetime.now(timezone.utc).isoformat()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    prov = {
        "ts": now_iso(),
        "slsa_level": "L3-target",
        "repo": os.getenv("GITHUB_REPOSITORY", "local"),
        "sha": os.getenv("GITHUB_SHA", "local"),
        "builder": "github-actions",
        "notes": "Replace with SLSA provenance generator + cosign attest.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(prov, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"provenance: stub out={out}")

if __name__ == "__main__":
    main()
