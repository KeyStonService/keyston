"""
Tests for governance framework
"""
import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


def load_structure_module(governance_root: Path) -> ModuleType:
    """Load structure_baseline without mutating sys.path."""
    module_path = governance_root / "structure_baseline.py"
    spec = importlib.util.spec_from_file_location("structure_baseline", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[call-arg]
    return module


@pytest.fixture
def baseline(governance_root: Path) -> ModuleType:
    return load_structure_module(governance_root)

def test_governance_structure_exists(governance_root):
    """Test that governance structure exists"""
    assert governance_root.exists()
    assert (governance_root / "README.md").exists()

def test_dimensions_exist(governance_root, baseline):
    """Test that all dimension directories exist"""
    # Note: 10-stakeholder moved to _legacy/10-stakeholder (2025-12-12)
    # Now using 10-policy for layered governance framework

    missing = baseline.missing_items(governance_root, baseline.REQUIRED_DIMENSIONS)
    assert not missing, f"Missing dimensions: {missing}"

def test_root_files_exist(governance_root, baseline):
    """Test that root files exist"""
    missing = baseline.missing_items(governance_root, baseline.REQUIRED_ROOT_FILES)
    assert not missing, f"Missing root files: {missing}"
