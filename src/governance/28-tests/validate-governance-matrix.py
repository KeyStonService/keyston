#!/usr/bin/env python3
"""
Validate Architecture Governance Matrix Completeness

This script validates that all 9 dimensions of the Architecture Governance Matrix
are properly defined and cross-referenced.

Usage:
    python tools/governance/validate-governance-matrix.py [--verbose]
"""

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Error: PyYAML is required. Install with: pip install PyYAML")
    sys.exit(1)


class GovernanceValidator:
    def __init__(self, repo_root: Path, verbose: bool = False):
        self.repo_root = repo_root
        self.verbose = verbose
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []
        
    def log_info(self, msg: str):
        """Log informational message"""
        self.info.append(msg)
        if self.verbose:
            print(f"ℹ️  {msg}")
    
    def log_warning(self, msg: str):
        """Log warning message"""
        self.warnings.append(msg)
        print(f"⚠️  {msg}")
    
    def log_error(self, msg: str):
        """Log error message"""
        self.errors.append(msg)
        print(f"❌ {msg}")
    
    def load_yaml(self, path: Path) -> dict:
        """Load and parse YAML file"""
        try:
            with open(path, encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            self.log_error(f"File not found: {path}")
            return {}
        except yaml.YAMLError as e:
            self.log_error(f"YAML parse error in {path}: {e}")
            return {}
    
    def validate_matrix_document(self) -> bool:
        """Validate core governance matrix document exists"""
        matrix_path = self.repo_root / "governance" / "ARCHITECTURE_GOVERNANCE_MATRIX.md"
        
        if not matrix_path.exists():
            self.log_error("Core document missing: governance/ARCHITECTURE_GOVERNANCE_MATRIX.md")
            return False
        
        self.log_info("✅ Core governance matrix document exists")
        
        # Check that it mentions all 9 dimensions
        with open(matrix_path, encoding='utf-8') as f:
            content = f.read()
        
        required_sections = [
            "Namespace",
            "Module Mapping",
            "Dependency Rules",
            "Layers & Domains",
            "Roles & Capabilities",
            "Behavior Contracts",
            "Lifecycle & Ownership",
            "Policies & Constraints",
            "Quality & Metrics"
        ]
        
        for section in required_sections:
            if section not in content:
                self.log_warning(f"Section '{section}' not found in governance matrix")
        
        return True
    
    def validate_layers_domains(self) -> bool:
        """Validate layers and domains definition"""
        layers_path = self.repo_root / "governance" / "architecture" / "layers-domains.yaml"
        
        if not layers_path.exists():
            self.log_error("Missing: governance/architecture/layers-domains.yaml")
            return False
        
        data = self.load_yaml(layers_path)
        if not data:
            return False
        
        # Check for required sections
        if 'layers' not in data:
            self.log_error("layers-domains.yaml missing 'layers' section")
            return False
        
        if 'domains' not in data:
            self.log_error("layers-domains.yaml missing 'domains' section")
            return False
        
        # Validate each layer has required fields
        for layer_name, layer_def in data.get('layers', {}).items():
            required_fields = ['description', 'responsibilities', 'restrictions', 'dependencies']
            for field in required_fields:
                if field not in layer_def:
                    self.log_warning(f"Layer '{layer_name}' missing field: {field}")
        
        self.log_info(f"✅ Layers & domains defined ({len(data.get('layers', {}))} layers, {len(data.get('domains', {}))} domains)")
        return True
    
    def validate_ownership_map(self) -> bool:
        """Validate ownership and lifecycle mapping"""
        ownership_path = self.repo_root / "governance" / "ownership-map.yaml"
        
        if not ownership_path.exists():
            self.log_error("Missing: governance/ownership-map.yaml")
            return False
        
        data = self.load_yaml(ownership_path)
        if not data:
            return False
        
        # Check for required sections
        if 'lifecycle_states' not in data:
            self.log_error("ownership-map.yaml missing 'lifecycle_states' section")
            return False
        
        if 'modules' not in data:
            self.log_error("ownership-map.yaml missing 'modules' section")
            return False
        
        # Validate each module has required fields
        modules = data.get('modules', {})
        for module_name, module_def in modules.items():
            required_fields = ['owner', 'lifecycle']
            for field in required_fields:
                if field not in module_def:
                    self.log_warning(f"Module '{module_name}' missing field: {field}")
        
        self.log_info(f"✅ Ownership map defined ({len(modules)} modules)")
        return True
    
    def validate_behavior_contracts(self) -> bool:
        """Validate behavior contracts directory"""
        contracts_dir = self.repo_root / "governance" / "behavior-contracts"
        
        if not contracts_dir.exists():
            self.log_error("Missing: governance/behavior-contracts/")
            return False
        
        # Count contract files (YAML files only)
        contract_files = list(contracts_dir.glob("*.yaml"))
        
        if len(contract_files) == 0:
            self.log_warning("No behavior contracts found (expected at least 1 example)")
        else:
            self.log_info(f"✅ Behavior contracts directory exists ({len(contract_files)} contracts)")
        
        # Validate structure of first contract as example
        for contract_file in contract_files[:1]:  # Check first one
            data = self.load_yaml(contract_file)
            if data and 'contract' in data:
                contract = data['contract']
                required_fields = ['module', 'version', 'owner']
                for field in required_fields:
                    if field not in contract:
                        self.log_warning(f"Contract {contract_file.name} missing field: contract.{field}")
        
        return True
    
    def validate_architecture_health(self) -> bool:
        """Validate architecture health metrics"""
        health_path = self.repo_root / "governance" / "architecture-health.yaml"
        
        if not health_path.exists():
            self.log_error("Missing: governance/architecture-health.yaml")
            return False
        
        data = self.load_yaml(health_path)
        if not data:
            return False
        
        # Check for required metric categories
        required_categories = ['governance_compliance', 'code_quality', 'architecture_health', 'quality_gates']
        for category in required_categories:
            if category not in data:
                self.log_warning(f"architecture-health.yaml missing category: {category}")
        
        self.log_info("✅ Architecture health metrics defined")
        return True
    
    def validate_architecture_policies(self) -> bool:
        """Validate architecture policy rules"""
        policies_path = self.repo_root / "governance" / "policies" / "architecture-rules.yaml"
        
        if not policies_path.exists():
            self.log_error("Missing: governance/policies/architecture-rules.yaml")
            return False
        
        data = self.load_yaml(policies_path)
        if not data:
            return False
        
        # Check for required policy categories
        required_categories = ['language_policies', 'security_policies', 'dependency_anti_patterns']
        for category in required_categories:
            if category not in data:
                self.log_warning(f"architecture-rules.yaml missing category: {category}")
        
        self.log_info("✅ Architecture policies defined")
        return True
    
    def validate_module_mapping(self) -> bool:
        """Validate module mapping in config"""
        mapping_path = self.repo_root / "config" / "system-module-map.yaml"
        
        if not mapping_path.exists():
            self.log_error("Missing: config/system-module-map.yaml")
            return False
        
        data = self.load_yaml(mapping_path)
        if not data:
            return False
        
        # Check for directory categories
        if 'directory_categories' not in data:
            self.log_error("system-module-map.yaml missing 'directory_categories' section")
            return False
        
        self.log_info("✅ Module mapping exists")
        return True
    
    def validate_cross_references(self) -> bool:
        """Validate cross-references between governance files"""
        self.log_info("Checking cross-references...")
        
        # Load ownership map and check if modules have contracts
        ownership_path = self.repo_root / "governance" / "ownership-map.yaml"
        ownership_data = self.load_yaml(ownership_path)
        
        contracts_dir = self.repo_root / "governance" / "behavior-contracts"
        contract_files = {f.stem for f in contracts_dir.glob("*.yaml")}
        
        modules_without_contracts = []
        for module_name in ownership_data.get('modules', {}).keys():
            if module_name not in contract_files:
                modules_without_contracts.append(module_name)
        
        if modules_without_contracts:
            count = len(modules_without_contracts)
            self.log_info(f"{count} modules without behavior contracts (this is expected during rollout)")
            if self.verbose:
                for module in modules_without_contracts[:5]:  # Show first 5
                    self.log_info(f"  - {module}")
        
        return True
    
    def run(self) -> int:
        """Run all validations and return exit code"""
        print("🔍 Validating Architecture Governance Matrix...")
        print()
        
        validations = [
            ("Core Matrix Document", self.validate_matrix_document),
            ("Layers & Domains", self.validate_layers_domains),
            ("Ownership Map", self.validate_ownership_map),
            ("Behavior Contracts", self.validate_behavior_contracts),
            ("Architecture Health", self.validate_architecture_health),
            ("Architecture Policies", self.validate_architecture_policies),
            ("Module Mapping", self.validate_module_mapping),
            ("Cross-References", self.validate_cross_references),
        ]
        
        results = []
        for name, validator in validations:
            print(f"\n{'='*60}")
            print(f"Validating: {name}")
            print('='*60)
            result = validator()
            results.append((name, result))
        
        # Print summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print(f"\n✅ Passed: {passed}/{total}")
        
        if self.warnings:
            print(f"⚠️  Warnings: {len(self.warnings)}")
        
        if self.errors:
            print(f"❌ Errors: {len(self.errors)}")
            print("\nErrors found:")
            for error in self.errors:
                print(f"  - {error}")
        
        print()
        
        if self.errors:
            return 1
        elif self.warnings:
            print("⚠️  Validation passed with warnings")
            return 0
        else:
            print("✅ All governance matrix validations passed!")
            return 0


def main():
    parser = argparse.ArgumentParser(
        description="Validate Architecture Governance Matrix completeness"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    args = parser.parse_args()
    
    # Find repository root
    current = Path(__file__).resolve()
    repo_root = current.parent.parent.parent
    
    validator = GovernanceValidator(repo_root, verbose=args.verbose)
    sys.exit(validator.run())


if __name__ == "__main__":
    main()
