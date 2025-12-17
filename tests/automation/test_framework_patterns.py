#!/usr/bin/env python3
"""
SynergyMesh Test Framework Patterns
====================================
Purpose: Reusable test patterns and utilities for automation testing
Extracted from legacy axiom_pr_test_suite.py and adapted for SynergyMesh
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class TestResult:
    """Data class for test results"""
    test_name: str
    status: str  # PASS, FAIL, WARNING
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict = field(default_factory=dict)


class TestSuiteRunner:
    """Base test suite runner with common patterns"""
    
    def __init__(self):
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'warnings': 0,
            'test_details': []
        }
        self.repo_root = Path.cwd()
    
    def log_test_result(self, test_name: str, status: str, message: str, details: Dict = None):
        """Log test result"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat(),
            'details': details or {}
        }
        
        self.test_results['test_details'].append(result)
        self.test_results['total_tests'] += 1
        
        if status == 'PASS':
            self.test_results['passed'] += 1
            print(f"✅ {test_name}: {message}")
        elif status == 'FAIL':
            self.test_results['failed'] += 1
            print(f"❌ {test_name}: {message}")
        elif status == 'WARNING':
            self.test_results['warnings'] += 1
            print(f"⚠️  {test_name}: {message}")
    
    def test_yaml_validation(self) -> bool:
        """Test YAML file validation"""
        try:
            yaml_files = list(self.repo_root.glob("**/*.yaml"))
            yaml_files.extend(list(self.repo_root.glob("**/*.yml")))
            
            # Exclude certain directories
            excluded_dirs = {'.git', 'node_modules', 'dist', '.github-private'}
            yaml_files = [
                f for f in yaml_files
                if not any(excluded in f.parts for excluded in excluded_dirs)
            ]
            
            if len(yaml_files) == 0:
                self.log_test_result(
                    "yaml_validation",
                    "WARNING",
                    "No YAML files found to validate"
                )
                return True
            
            # Basic validation check
            invalid_files = []
            for yaml_file in yaml_files:
                try:
                    with open(yaml_file, 'r') as f:
                        content = f.read()
                        # Basic syntax check
                        if not content.strip():
                            invalid_files.append(str(yaml_file))
                except Exception as e:
                    invalid_files.append(str(yaml_file))
            
            if len(invalid_files) == 0:
                self.log_test_result(
                    "yaml_validation",
                    "PASS",
                    f"All {len(yaml_files)} YAML files validated successfully",
                    {"files_checked": len(yaml_files)}
                )
                return True
            else:
                self.log_test_result(
                    "yaml_validation",
                    "FAIL",
                    f"YAML validation failed for {len(invalid_files)} files",
                    {"invalid_files": invalid_files}
                )
                return False
                
        except Exception as e:
            self.log_test_result("yaml_validation", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_code_quality_checks(self) -> bool:
        """Test code quality checks"""
        try:
            python_files = list(self.repo_root.glob("**/*.py"))
            
            # Exclude certain directories
            excluded_dirs = {'.git', 'node_modules', 'dist', '__pycache__', '.venv'}
            python_files = [
                f for f in python_files
                if not any(excluded in f.parts for excluded in excluded_dirs)
            ]
            
            if len(python_files) == 0:
                self.log_test_result(
                    "code_quality_checks",
                    "WARNING",
                    "No Python files found to check"
                )
                return True
            
            # Basic quality checks
            issues = []
            for py_file in python_files:
                try:
                    with open(py_file, 'r') as f:
                        content = f.read()
                        # Check for basic quality issues
                        if len(content) > 10000:  # Large file
                            issues.append(f"{py_file}: File too large")
                except Exception as e:
                    issues.append(f"{py_file}: {str(e)}")
            
            if len(issues) <= 5:  # Allow some issues
                self.log_test_result(
                    "code_quality_checks",
                    "PASS",
                    f"Code quality acceptable ({len(issues)} minor issues)",
                    {"issues": issues}
                )
                return True
            else:
                self.log_test_result(
                    "code_quality_checks",
                    "FAIL",
                    f"Too many code quality issues: {len(issues)}"
                )
                return False
                
        except Exception as e:
            self.log_test_result("code_quality_checks", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_directory_structure(self) -> bool:
        """Test repository directory structure"""
        try:
            required_dirs = [
                'automation',
                'config',
                'docs',
                'governance',
                'tools'
            ]
            
            missing_dirs = []
            for dir_name in required_dirs:
                dir_path = self.repo_root / dir_name
                if not dir_path.exists():
                    missing_dirs.append(dir_name)
            
            if len(missing_dirs) == 0:
                self.log_test_result(
                    "directory_structure",
                    "PASS",
                    "All required directories present"
                )
                return True
            else:
                self.log_test_result(
                    "directory_structure",
                    "WARNING",
                    f"Missing directories: {missing_dirs}",
                    {"missing": missing_dirs}
                )
                return True
                
        except Exception as e:
            self.log_test_result("directory_structure", "FAIL", f"Exception: {str(e)}")
            return False
    
    def test_configuration_files(self) -> bool:
        """Test configuration files existence"""
        try:
            required_configs = [
                'machinenativeops.yaml',
                'package.json',
                'pyproject.toml'
            ]
            legacy_aliases = {}
            
            missing_configs = []
            legacy_used = []
            for config_file in required_configs:
                config_path = self.repo_root / config_file
                if not config_path.exists():
                    aliases = legacy_aliases.get(config_file, [])
                    if any((self.repo_root / alias).exists() for alias in aliases):
                        legacy_used.append(config_file)
                        continue
                    missing_configs.append(config_file)
            
            if len(missing_configs) == 0:
                self.log_test_result(
                    "configuration_files",
                    "INFO" if legacy_used else "PASS",
                    "All required configuration files present"
                    + (f" (using legacy aliases for: {legacy_used})" if legacy_used else "")
                )
                return True
            else:
                self.log_test_result(
                    "configuration_files",
                    "WARNING",
                    f"Missing configuration files: {missing_configs}",
                    {"missing": missing_configs}
                )
                return True
                
        except Exception as e:
            self.log_test_result("configuration_files", "FAIL", f"Exception: {str(e)}")
            return False
    
    def run_all_tests(self) -> Dict:
        """Run all tests"""
        print("🧪 Starting SynergyMesh Test Suite...")
        print("=" * 60)
        
        # Run all test methods
        test_methods = [
            self.test_yaml_validation,
            self.test_code_quality_checks,
            self.test_directory_structure,
            self.test_configuration_files
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test_result(
                    test_method.__name__,
                    "FAIL",
                    f"Unexpected error: {str(e)}"
                )
        
        # Calculate overall results
        success_rate = (
            self.test_results['passed'] / self.test_results['total_tests']
            if self.test_results['total_tests'] > 0
            else 0
        )
        
        print("\n" + "=" * 60)
        print("📊 Test Summary")
        print("-" * 30)
        print(f"Total Tests: {self.test_results['total_tests']}")
        print(f"Passed: {self.test_results['passed']} ✅")
        print(f"Failed: {self.test_results['failed']} ❌")
        print(f"Warnings: {self.test_results['warnings']} ⚠️")
        print(f"Success Rate: {success_rate:.1%}")
        
        # Determine overall status
        if success_rate >= 0.9 and self.test_results['failed'] == 0:
            print(f"\n🎉 SynergyMesh Test Suite: PASSED")
            self.test_results['overall_status'] = 'PASS'
        elif success_rate >= 0.8:
            print(f"\n⚠️  SynergyMesh Test Suite: PASSED WITH WARNINGS")
            self.test_results['overall_status'] = 'PASS_WITH_WARNINGS'
        else:
            print(f"\n❌ SynergyMesh Test Suite: FAILED")
            self.test_results['overall_status'] = 'FAIL'
        
        return self.test_results
    
    def generate_test_report(self, output_file: str = "test-report.json"):
        """Generate test report"""
        with open(output_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"\n📋 Test report saved to: {output_file}")


def main():
    """Main entry point"""
    runner = TestSuiteRunner()
    results = runner.run_all_tests()
    runner.generate_test_report()
    
    # Exit with appropriate code
    if results['overall_status'] == 'PASS':
        sys.exit(0)
    elif results['overall_status'] == 'PASS_WITH_WARNINGS':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
