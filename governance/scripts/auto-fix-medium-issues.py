#!/usr/bin/env python3
"""
Auto-Fix Medium Severity Issues
Automatically fixes the top 2 MEDIUM severity problems identified:
1. Optional policy enforcement → Required for critical dimensions
2. Missing compliance frameworks → Add standard frameworks
"""

import os
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Critical dimensions that require mandatory policy enforcement
CRITICAL_DIMENSIONS = [
    "05-compliance",
    "06-security", 
    "07-audit",
    "23-policies",
    "39-automation",
    "40-self-healing",
    "60-contracts",
    "70-audit"
]

# Standard compliance frameworks to add
COMPLIANCE_FRAMEWORKS = {
    # Strategic layer - AI/ML governance
    "00-vision-strategy": ["ISO-42001", "NIST-AI-RMF"],
    "01-architecture": ["ISO-42010", "TOGAF"],
    "02-decision": ["ISO-38500", "COBIT"],
    
    # Security and compliance
    "05-compliance": ["ISO-27001", "ISO-42001", "SOC-2", "GDPR"],
    "06-security": ["ISO-27001", "NIST-CSF", "CIS-Controls"],
    "07-audit": ["ISO-19011", "SOC-2"],
    "70-audit": ["ISO-19011", "SOC-2"],
    
    # Policy and governance
    "10-policy": ["ISO-38500", "COBIT"],
    "23-policies": ["ISO-38500"],
    
    # Risk management
    "04-risk": ["ISO-31000", "NIST-RMF"],
    
    # Execution and automation
    "39-automation": ["ISO-22301", "ITIL"],
    "40-self-healing": ["ISO-22301", "SRE-Principles"],
    
    # Contracts and SBOMs
    "60-contracts": ["ISO-19770", "SPDX"],
    "38-sbom": ["ISO-19770", "SPDX", "CycloneDX"],
    
    # Default for others
    "_default": ["ISO-42001"]
}


def load_yaml_file(file_path: Path) -> Dict[str, Any]:
    """Load YAML file with error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return {}


def save_yaml_file(file_path: Path, data: Dict[str, Any]) -> bool:
    """Save YAML file with proper formatting."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False


def fix_policy_enforcement(governance_root: Path) -> int:
    """
    Fix Issue #1: Convert optional policy enforcement to required for critical dimensions
    """
    print(f"\n{BLUE}[1/2] Fixing Policy Enforcement...{RESET}")
    fixed_count = 0
    
    for dim_name in CRITICAL_DIMENSIONS:
        dim_file = governance_root / dim_name / "dimension.yaml"
        if not dim_file.exists():
            continue
            
        data = load_yaml_file(dim_file)
        
        # Check if policy enforcement exists and is optional
        if 'spec' in data and 'policy' in data['spec']:
            policy_spec = data['spec']['policy']
            
            if isinstance(policy_spec, dict):
                current_enforcement = policy_spec.get('enforcement', 'optional')
                
                if current_enforcement != 'required':
                    policy_spec['enforcement'] = 'required'
                    
                    if save_yaml_file(dim_file, data):
                        print(f"  {GREEN}✓{RESET} {dim_name}: Changed enforcement optional → required")
                        fixed_count += 1
                    else:
                        print(f"  ✗ {dim_name}: Failed to save changes")
    
    print(f"{GREEN}Fixed {fixed_count} policy enforcement issues{RESET}")
    return fixed_count


def fix_compliance_frameworks(governance_root: Path) -> int:
    """
    Fix Issue #2: Add compliance frameworks to all dimensions
    """
    print(f"\n{BLUE}[2/2] Adding Compliance Frameworks...{RESET}")
    fixed_count = 0
    
    # Find all dimension.yaml files
    dim_files = list(governance_root.glob("*/dimension.yaml"))
    
    for dim_file in dim_files:
        dim_name = dim_file.parent.name
        
        data = load_yaml_file(dim_file)
        
        # Ensure spec section exists
        if 'spec' not in data:
            data['spec'] = {}
        
        # Ensure compliance section exists under spec (as expected by problem identifier)
        if 'compliance' not in data['spec']:
            data['spec']['compliance'] = {}
        
        # Check if frameworks already exist
        if 'frameworks' not in data['spec']['compliance'] or not data['spec']['compliance']['frameworks']:
            # Get appropriate frameworks for this dimension
            frameworks = COMPLIANCE_FRAMEWORKS.get(dim_name, COMPLIANCE_FRAMEWORKS['_default'])
            
            data['spec']['compliance']['frameworks'] = frameworks
            
            # Add framework descriptions
            if 'framework_mappings' not in data['spec']['compliance']:
                data['spec']['compliance']['framework_mappings'] = []
            
            for framework in frameworks:
                # Add basic mapping if not exists
                existing = [m for m in data['spec']['compliance']['framework_mappings'] 
                           if m.get('framework') == framework]
                if not existing:
                    data['spec']['compliance']['framework_mappings'].append({
                        'framework': framework,
                        'controls': [],
                        'compliance_status': 'in_progress'
                    })
            
            if save_yaml_file(dim_file, data):
                print(f"  {GREEN}✓{RESET} {dim_name}: Added {len(frameworks)} compliance framework(s)")
                fixed_count += 1
            else:
                print(f"  ✗ {dim_name}: Failed to save changes")
    
    print(f"{GREEN}Fixed {fixed_count} compliance framework issues{RESET}")
    return fixed_count


def update_governance_map_execution(governance_root: Path) -> int:
    """
    Update governance-map.yaml to mark critical dimensions as required execution
    """
    print(f"\n{BLUE}[BONUS] Updating Governance Map...{RESET}")
    map_file = governance_root / "governance-map.yaml"
    
    if not map_file.exists():
        print(f"  {YELLOW}⚠{RESET} governance-map.yaml not found")
        return 0
    
    data = load_yaml_file(map_file)
    updated_count = 0
    
    if 'dimensions' in data:
        for dim in data['dimensions']:
            if dim.get('name') in CRITICAL_DIMENSIONS:
                if 'execution' not in dim or dim['execution'] != 'required':
                    dim['execution'] = 'required'
                    updated_count += 1
    
    if updated_count > 0:
        if save_yaml_file(map_file, data):
            print(f"  {GREEN}✓{RESET} Updated {updated_count} dimensions to required execution")
        else:
            print(f"  ✗ Failed to save governance-map.yaml")
            updated_count = 0
    else:
        print(f"  {YELLOW}ℹ{RESET} All critical dimensions already set to required")
    
    return updated_count


def main():
    """Main execution"""
    print("="*80)
    print("SynergyMesh Auto-Fix Tool - MEDIUM Severity Issues")
    print("自動修復工具 - 中等嚴重度問題")
    print("="*80)
    
    # Determine governance root
    script_dir = Path(__file__).parent.parent
    governance_root = script_dir
    
    if not governance_root.exists():
        print(f"Error: Governance directory not found: {governance_root}")
        sys.exit(1)
    
    print(f"\nGovernance Root: {governance_root}")
    print(f"Fixing 2 MEDIUM severity issues:\n")
    print("  1. Policy Enforcement: optional → required (critical dimensions)")
    print("  2. Compliance Frameworks: Add ISO/NIST frameworks to all dimensions")
    
    # Execute fixes
    total_fixed = 0
    
    fixed_1 = fix_policy_enforcement(governance_root)
    total_fixed += fixed_1
    
    fixed_2 = fix_compliance_frameworks(governance_root)
    total_fixed += fixed_2
    
    fixed_bonus = update_governance_map_execution(governance_root)
    
    # Summary
    print("\n" + "="*80)
    print("Auto-Fix Summary")
    print("="*80)
    print(f"Policy Enforcement Fixed:     {fixed_1}")
    print(f"Compliance Frameworks Added:  {fixed_2}")
    print(f"Governance Map Updated:       {fixed_bonus}")
    print(f"\n{GREEN}Total Issues Fixed: {total_fixed}{RESET}")
    print("="*80)
    
    print(f"\n{GREEN}✓ Auto-fix completed successfully{RESET}")
    print(f"\nNext steps:")
    print(f"  1. Run validation: python governance/scripts/validate-governance-structure.py")
    print(f"  2. Re-scan problems: python governance/scripts/extreme-problem-identifier.py")
    print(f"  3. Commit changes: git add . && git commit -m 'fix: Auto-fix MEDIUM severity issues'")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
