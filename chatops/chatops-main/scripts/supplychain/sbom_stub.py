#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Add scripts directory to path for common utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_utils import now_iso, write_json_report  # noqa: E402


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
    write_json_report(args.out, sbom)
    print(f"sbom: stub out={args.out}")


if __name__ == "__main__":
    main()
