#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path

# Add scripts directory to path for common utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_utils import now_iso, write_json_report  # noqa: E402


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
    write_json_report(args.out, prov)
    print(f"provenance: stub out={args.out}")


if __name__ == "__main__":
    main()
