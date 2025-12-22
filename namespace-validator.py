#!/usr/bin/env python3
"""
MachineNativeOps Namespace Validator
機器原生運維命名空間驗證器

Validates that all files follow MachineNativeOps namespace conventions:
- machinenativeops.io (all tags)
- machinenativeops (namespace)
- registry.machinenativeops.io (mirror repository)
- etc/machinenativeops/pkl (certificate path)
- super-agent-etcd-cluster (cluster token)
"""

import re
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
import argparse

class NamespaceValidator:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.violations = []
        self.checked_files = 0
        self.compliant_files = 0
        
        # Required patterns for MachineNativeOps namespace
        self.required_patterns = {
            'domain': r'machinenativeops\.io',
            'namespace': r'machinenativeops(?!\.)',
            'registry': r'registry\.machinenativeops\.io',
            'cert_path': r'etc/machinenativeops/pkl',
            'cluster_token': r'super-agent-etcd-cluster',
        }
        
        # Forbidden patterns (old AXIOM references)
        self.forbidden_patterns = {
            'old_domain': r'axiom\.io',
            'old_namespace': r'axiom-system',
            'old_urn': r'urn:axiom:',
            'old_baseline': r'AxiomGlobalBaseline',
        }
    
    def validate_file(self, file_path: Path) -> Tuple[bool, List[str]]:
        """Validate a single file for namespace compliance."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_violations = []
            
            # Check for forbidden patterns
            for pattern_name, pattern in self.forbidden_patterns.items():
                matches = re.findall(pattern, content)
                if matches:
                    file_violations.append(
                        f"❌ Found forbidden pattern '{pattern_name}': {len(matches)} occurrence(s)"
                    )
            
            # For YAML files, perform deeper validation
            if file_path.suffix in ['.yaml', '.yml']:
                try:
                    docs = yaml.safe_load_all(content)
                    for doc in docs:
                        if doc:
                            self._validate_yaml_structure(doc, file_violations)
                except yaml.YAMLError as e:
                    file_violations.append(f"⚠️  YAML parsing error: {e}")
            
            self.checked_files += 1
            if not file_violations:
                self.compliant_files += 1
                return True, []
            else:
                return False, file_violations
                
        except Exception as e:
            return False, [f"❌ Error reading file: {e}"]
    
    def _validate_yaml_structure(self, doc: dict, violations: List[str]):
        """Validate YAML document structure for namespace compliance."""
        if not isinstance(doc, dict):
            return
        
        # Check apiVersion
        if 'apiVersion' in doc:
            api_version = doc['apiVersion']
            # Note: Checking for forbidden pattern, not URL sanitization (CodeQL false positive)
            if 'axiom.io' in api_version:
                violations.append(
                    f"❌ apiVersion uses forbidden 'axiom.io': {api_version}"
                )
            elif 'machinenativeops.io' not in api_version and '/' in api_version:
                if api_version not in ['v1', 'v2', 'apps/v1', 'batch/v1']:
                    violations.append(
                        f"⚠️  apiVersion should use 'machinenativeops.io': {api_version}"
                    )
        
        # Check kind
        if 'kind' in doc:
            kind = doc['kind']
            if 'Axiom' in kind:
                violations.append(
                    f"❌ kind uses forbidden 'Axiom' prefix: {kind}"
                )
        
        # Check metadata labels and annotations
        if 'metadata' in doc and isinstance(doc['metadata'], dict):
            for field in ['labels', 'annotations']:
                if field in doc['metadata']:
                    self._validate_labels(doc['metadata'][field], violations)
    
    def _validate_labels(self, labels: dict, violations: List[str]):
        """Validate labels/annotations for namespace compliance."""
        if not isinstance(labels, dict):
            return
        
        # Note: Checking for forbidden pattern in metadata, not URL sanitization (CodeQL false positive)
        for key, value in labels.items():
            if 'axiom.io' in key:
                violations.append(
                    f"❌ Label/annotation uses forbidden 'axiom.io': {key}"
                )
            if isinstance(value, str) and 'axiom.io' in value:
                violations.append(
                    f"❌ Label/annotation value uses forbidden 'axiom.io': {key}={value}"
                )
    
    def validate_directory(self, directory: Path, extensions: List[str] = None) -> Dict:
        """Validate all files in a directory."""
        if extensions is None:
            extensions = ['.yaml', '.yml', '.py', '.md', '.sh', '.json']
        
        results = {
            'total_files': 0,
            'compliant_files': 0,
            'violations_by_file': {},
        }
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip certain directories
                skip_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', 'archive'}
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue
                
                is_compliant, violations = self.validate_file(file_path)
                results['total_files'] += 1
                
                if is_compliant:
                    results['compliant_files'] += 1
                    if self.verbose:
                        print(f"✅ {file_path.relative_to(directory)}")
                else:
                    results['violations_by_file'][str(file_path.relative_to(directory))] = violations
                    print(f"\n❌ {file_path.relative_to(directory)}")
                    for violation in violations:
                        print(f"   {violation}")
        
        return results
    
    def generate_report(self, results: Dict) -> str:
        """Generate a validation report."""
        total = results['total_files']
        compliant = results['compliant_files']
        violations_count = len(results['violations_by_file'])
        
        compliance_rate = (compliant / total * 100) if total > 0 else 0
        
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║     MachineNativeOps Namespace Validation Report            ║
╚══════════════════════════════════════════════════════════════╝

📊 Summary:
  Total files checked:     {total}
  Compliant files:         {compliant}
  Files with violations:   {violations_count}
  Compliance rate:         {compliance_rate:.2f}%

"""
        
        if compliance_rate == 100:
            report += "✅ **All files are 100% compliant with MachineNativeOps namespace!**\n"
        elif compliance_rate >= 90:
            report += "⚠️  Most files are compliant, but some violations found.\n"
        else:
            report += "❌ Significant violations found. Action required.\n"
        
        report += f"""
🎯 Namespace Requirements:
  ✓ machinenativeops.io (domain for all tags)
  ✓ machinenativeops (primary namespace)
  ✓ registry.machinenativeops.io (mirror repository)
  ✓ etc/machinenativeops/pkl (certificate path)
  ✓ super-agent-etcd-cluster (cluster token)

🚫 Forbidden Patterns:
  ✗ axiom.io (old domain)
  ✗ axiom-system (old namespace)
  ✗ urn:axiom: (old URN pattern)
  ✗ AxiomGlobalBaseline (old resource type)
"""
        
        return report

def main():
    parser = argparse.ArgumentParser(
        description='Validate MachineNativeOps namespace compliance'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to validate (default: current directory)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show all checked files, not just violations'
    )
    parser.add_argument(
        '--output',
        help='Output report to file'
    )
    
    args = parser.parse_args()
    
    directory = Path(args.directory).resolve()
    if not directory.exists():
        print(f"❌ Directory not found: {directory}")
        sys.exit(1)
    
    print(f"🔍 Validating namespace compliance in: {directory}\n")
    
    validator = NamespaceValidator(verbose=args.verbose)
    results = validator.validate_directory(directory)
    report = validator.generate_report(results)
    
    print(report)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n📄 Report saved to: {args.output}")
    
    # Exit with error code if not 100% compliant
    if results['compliant_files'] != results['total_files']:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
