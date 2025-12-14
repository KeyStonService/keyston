"""
Tests for governance framework
"""
import pytest
from pathlib import Path

def test_governance_structure_exists(governance_root):
    """Test that governance structure exists"""
    assert governance_root.exists()
    assert (governance_root / "README.md").exists()

def test_dimensions_exist(governance_root):
    """Test that all dimension directories exist"""
    expected_dims = [
        "00-vision-strategy", "01-architecture", "02-decision",
        "03-change", "04-risk", "05-compliance", "06-security",
        "07-audit", "08-process", "09-performance", "10-stakeholder",
        "11-tools-systems", "12-culture-capability", 
        "13-metrics-reporting", "14-improvement"
    ]
    
    for dim in expected_dims:
        dim_path = governance_root / dim
        assert dim_path.exists(), f"Dimension {dim} does not exist"

def test_root_files_exist(governance_root):
    """Test that root files exist"""
    root_files = [
        "README.md", "QUICKSTART.md", "IMPLEMENTATION-ROADMAP.md",
        "requirements.txt", "docker-compose.yml", "Makefile"
    ]
    
    for file in root_files:
        assert (governance_root / file).exists(), f"Root file {file} missing"
