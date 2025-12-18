"""
Pytest configuration for governance tests
"""
import pytest
from pathlib import Path

@pytest.fixture
def governance_root():
    """Return path to governance root directory"""
    return Path(__file__).parent.parent

@pytest.fixture
def test_yaml_file(tmp_path):
    """Create a temporary YAML file for testing"""
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text("key: value\n")
    return yaml_file
