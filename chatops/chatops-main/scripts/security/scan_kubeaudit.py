#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys

# Add scripts directory to path for common utilities
sys.path.insert(0, str(Path(__file__).parent.parent))
from common_utils import now_iso  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    report = {
        "ts": now_iso(),
        "tool": "kubeaudit",
        "mode": "stub",
        "root": str(Path(args.root)),
        "summary": {"findings": 0},
        "notes": "CI should run kubeaudit/kubescape against cluster or rendered manifests.",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"kubeaudit: stub out={out}")


if __name__ == "__main__":
    main()
