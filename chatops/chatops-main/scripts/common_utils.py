#!/usr/bin/env python3
"""
Common utility functions shared across chatops scripts.
Reduces code duplication and improves maintainability.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat()


def write_json_report(output_path: str, data: Dict[str, Any]) -> None:
    """
    Write a JSON report to the specified path.

    Args:
        output_path: Path to write the JSON file
        data: Dictionary to serialize as JSON
    """
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
