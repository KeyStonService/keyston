#!/usr/bin/env python3
"""
SynergyMesh Governance Structure Validator

Purpose: Validate governance directory structure against governance-map.yaml
Ensures consistency, prevents orphaned directories, and enforces conventions.

Usage:
    python governance/scripts/validate-governance-structure.py
    python governance/scripts/validate-governance-structure.py --verbose
    python governance/scripts/validate-governance-structure.py --fix-permissions
"""

import os
import sys
import yaml
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set, Tuple

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class GovernanceValidator:
    def __init__(self, governance_root: str = "governance", verbose: bool = False):
        self.governance_root = Path(governance_root)
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.info: List[str] = []
        
    def log(self, message: str, level: str = "info"):
        """Log message with appropriate color and level"""
        if level == "error":
            self.errors.append(message)
            print(f"{Colors.FAIL}❌ ERROR: {message}{Colors.ENDC}")
        elif level == "warning":
            self.warnings.append(message)
            print(f"{Colors.WARNING}⚠️  WARNING: {message}{Colors.ENDC}")
        elif level == "info":
            self.info.append(message)
            if self.verbose:
                print(f"{Colors.OKBLUE}ℹ️  INFO: {message}{Colors.ENDC}")
        elif level == "success":
            print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
                
    def load_governance_map(self) -> Dict:
        """Load and parse governance-map.yaml"""
        map_file = self.governance_root / "governance-map.yaml"
        
        if not map_file.exists():
            self.log(f"Missing governance-map.yaml at {map_file}", "error")
            return {}
            
        try:
            with open(map_file, 'r', encoding='utf-8') as f:
                governance_map = yaml.safe_load(f)
                self.log(f"Loaded governance-map.yaml successfully", "info")
                return governance_map
        except yaml.YAMLError as e:
            self.log(f"Failed to parse governance-map.yaml: {e}", "error")
            return {}
        except Exception as e:
            self.log(f"Error reading governance-map.yaml: {e}", "error")
            return {}
    
    def get_actual_directories(self) -> Set[str]:
        """Get all actual directories in governance/"""
        if not self.governance_root.exists():
            self.log(f"Governance root {self.governance_root} does not exist", "error")
            return set()
            
        actual_dirs = set()
        for item in self.governance_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                actual_dirs.add(item.name)
                
        self.log(f"Found {len(actual_dirs)} directories in {self.governance_root}", "info")
        return actual_dirs
    
    def validate_dimension_structure(self, dimension: Dict) -> bool:
        """Validate a single dimension directory structure"""
        name = dimension.get('name', 'unknown')
        path = Path(dimension.get('path', ''))
        
        if not path.exists():
            self.log(f"Dimension '{name}' path does not exist: {path}", "error")
            return False
            
        # Check for required dimension.yaml file
        dimension_file = path / "dimension.yaml"
        if not dimension_file.exists():
            self.log(f"Dimension '{name}' missing required dimension.yaml file", "warning")
            
        return True
    
    def validate_shared_resources(self, shared: Dict) -> bool:
        """Validate a shared resource directory"""
        name = shared.get('name', 'unknown')
        path = Path(shared.get('path', ''))
        
        if not path.exists():
            self.log(f"Shared resource '{name}' path does not exist: {path}", "error")
            return False
            
        return True
    
    def check_naming_conventions(self, directory: str) -> Tuple[bool, str]:
        """Check if directory follows naming conventions"""
        # Pattern for numbered dimensions: 00-80 range
        numbered_pattern = r'^\d{2}-[a-z-]+$'
        
        if re.match(numbered_pattern, directory):
            # Extract number
            num = int(directory[:2])
            if 0 <= num <= 80:
                return True, "dimension"
            else:
                return False, f"number out of range (should be 00-80): {directory}"
        else:
            # Unnumbered directory - should be shared resource
            return True, "shared"
    
    def check_orphaned_directories(self, governance_map: Dict, actual_dirs: Set[str]) -> List[str]:
        """Find directories not registered in governance-map.yaml"""
        registered_dims = {d['name'] for d in governance_map.get('dimensions', [])}
        registered_shared = {s['name'] for s in governance_map.get('shared_resources', [])}
        registered_all = registered_dims | registered_shared
        
        # Add known special directories
        special_dirs = {'dimensions', '_scratch'}
        registered_all |= special_dirs
        
        orphaned = actual_dirs - registered_all
        return list(orphaned)
    
    def check_dependencies(self, governance_map: Dict) -> bool:
        """Validate dimension dependencies are valid"""
        all_dimensions = {d['name'] for d in governance_map.get('dimensions', [])}
        
        valid = True
        for dimension in governance_map.get('dimensions', []):
            name = dimension.get('name')
            depends_on = dimension.get('depends_on', [])
            
            for dep in depends_on:
                if dep not in all_dimensions:
                    self.log(f"Dimension '{name}' depends on non-existent dimension '{dep}'", "error")
                    valid = False
                    
        return valid
    
    def check_migration_deadlines(self, governance_map: Dict) -> None:
        """Check for overdue migrations"""
        migrations = governance_map.get('migrations', {}).get('pending', [])
        
        for migration in migrations:
            asset = migration.get('asset')
            deadline_str = migration.get('deadline')
            
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
                    if deadline < datetime.now():
                        self.log(f"Migration overdue: {asset} (deadline: {deadline_str})", "warning")
                    else:
                        days_left = (deadline - datetime.now()).days
                        self.log(f"Migration pending: {asset} ({days_left} days until {deadline_str})", "info")
                except ValueError:
                    self.log(f"Invalid deadline format for {asset}: {deadline_str}", "warning")
    
    def validate(self) -> bool:
        """Run all validation checks"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
        print(f"SynergyMesh Governance Structure Validator")
        print(f"{'='*70}{Colors.ENDC}\n")
        
        # Load governance map
        governance_map = self.load_governance_map()
        if not governance_map:
            return False
        
        # Get actual directories
        actual_dirs = self.get_actual_directories()
        if not actual_dirs:
            return False
        
        # Check 1: Validate dimension structures
        print(f"\n{Colors.BOLD}[1/6] Validating dimension structures...{Colors.ENDC}")
        for dimension in governance_map.get('dimensions', []):
            self.validate_dimension_structure(dimension)
        
        # Check 2: Validate shared resources
        print(f"\n{Colors.BOLD}[2/6] Validating shared resources...{Colors.ENDC}")
        for shared in governance_map.get('shared_resources', []):
            self.validate_shared_resources(shared)
        
        # Check 3: Check naming conventions
        print(f"\n{Colors.BOLD}[3/6] Checking naming conventions...{Colors.ENDC}")
        for directory in actual_dirs:
            valid, category = self.check_naming_conventions(directory)
            if not valid:
                self.log(f"Invalid naming convention: {category}", "warning")
            else:
                self.log(f"Directory '{directory}' identified as {category}", "info")
        
        # Check 4: Check for orphaned directories
        print(f"\n{Colors.BOLD}[4/6] Checking for orphaned directories...{Colors.ENDC}")
        orphaned = self.check_orphaned_directories(governance_map, actual_dirs)
        if orphaned:
            for orphan in orphaned:
                self.log(f"Orphaned directory not in governance-map.yaml: {orphan}", "warning")
        else:
            self.log("No orphaned directories found", "success")
        
        # Check 5: Validate dependencies
        print(f"\n{Colors.BOLD}[5/6] Validating dimension dependencies...{Colors.ENDC}")
        if self.check_dependencies(governance_map):
            self.log("All dimension dependencies are valid", "success")
        
        # Check 6: Check migration deadlines
        print(f"\n{Colors.BOLD}[6/6] Checking migration deadlines...{Colors.ENDC}")
        self.check_migration_deadlines(governance_map)
        
        # Summary
        self.print_summary()
        
        # Return success if no errors
        return len(self.errors) == 0
    
    def print_summary(self):
        """Print validation summary"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
        print(f"Validation Summary")
        print(f"{'='*70}{Colors.ENDC}\n")
        
        if self.errors:
            print(f"{Colors.FAIL}Errors: {len(self.errors)}{Colors.ENDC}")
            for error in self.errors:
                print(f"  - {error}")
                
        if self.warnings:
            print(f"\n{Colors.WARNING}Warnings: {len(self.warnings)}{Colors.ENDC}")
            for warning in self.warnings:
                print(f"  - {warning}")
                
        if self.verbose and self.info:
            print(f"\n{Colors.OKBLUE}Info: {len(self.info)}{Colors.ENDC}")
            for info in self.info:
                print(f"  - {info}")
        
        print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
        
        if len(self.errors) == 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✅ VALIDATION PASSED{Colors.ENDC}\n")
        else:
            print(f"{Colors.FAIL}{Colors.BOLD}❌ VALIDATION FAILED{Colors.ENDC}\n")

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Validate SynergyMesh governance directory structure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python governance/scripts/validate-governance-structure.py
  python governance/scripts/validate-governance-structure.py --verbose
  python governance/scripts/validate-governance-structure.py --governance-root ./governance
        """
    )
    
    parser.add_argument(
        '--governance-root',
        default='governance',
        help='Path to governance root directory (default: governance)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Run validation
    validator = GovernanceValidator(
        governance_root=args.governance_root,
        verbose=args.verbose
    )
    
    success = validator.validate()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
