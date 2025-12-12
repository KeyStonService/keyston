"""
Baseline references for governance directory validation.
"""
from pathlib import Path
from typing import Iterable

REQUIRED_DIMENSIONS: tuple[str, ...] = (
    "00-vision-strategy",
    "01-architecture",
    "02-decision",
    "03-change",
    "04-risk",
    "05-compliance",
    "06-security",
    "07-audit",
    "08-process",
    "09-performance",
    "10-policy",
    "11-tools-systems",
    "12-culture-capability",
    "13-metrics-reporting",
    "14-improvement",
)

REQUIRED_ROOT_FILES: tuple[str, ...] = (
    "README.md",
    "QUICKSTART.md",
    "IMPLEMENTATION-ROADMAP.md",
    "requirements.txt",
    "docker-compose.yml",
    "Makefile",
)


def missing_items(root: Path, names: Iterable[str]) -> list[str]:
    """Return any names that do not exist under the given root."""
    return [name for name in names if not (root / name).exists()]
