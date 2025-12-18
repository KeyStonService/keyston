"""
Governance Utility Functions
Version: 1.0.0
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any

def load_yaml(file_path: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def save_yaml(data: Dict[str, Any], file_path: str) -> None:
    """Save data to YAML file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

def find_governance_files(base_path: str, pattern: str = "*.yaml") -> List[Path]:
    """Find all governance configuration files"""
    base = Path(base_path)
    return list(base.rglob(pattern))

def validate_yaml_syntax(file_path: str) -> bool:
    """Validate YAML syntax"""
    try:
        load_yaml(file_path)
        return True
    except yaml.YAMLError:
        return False

def get_dimension_status(dimension_path: str) -> Dict[str, Any]:
    """Get status of a governance dimension"""
    readme_path = Path(dimension_path) / "README.md"
    if not readme_path.exists():
        return {'status': 'unknown', 'completion': 0}
    
    # Parse README for status information
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
        if 'Status: Active' in content or 'Status**: Active' in content:
            return {'status': 'active', 'completion': 100}
        elif 'Status: Planning' in content or 'Status**: Planning' in content:
            return {'status': 'planning', 'completion': 0}
        else:
            return {'status': 'unknown', 'completion': 0}
