#!/usr/bin/env python3
"""
SynergyMesh Governance Directory Scanner

Purpose: Comprehensive scan of governance directory structure with detailed reporting.
Provides deep analysis, statistics, and actionable recommendations for governance maintenance.

Features:
- Full directory structure scan (00-80 dimensions)
- File completeness verification (dimension.yaml, framework.yaml, README.md)
- Naming convention validation
- Dependency graph analysis
- Orphaned directory detection
- Statistics generation
- Integration with existing validators

Usage:
    python governance/35-scripts/scan-governance-directory.py
    python governance/35-scripts/scan-governance-directory.py --verbose
    python governance/35-scripts/scan-governance-directory.py --report-format json
    python governance/35-scripts/scan-governance-directory.py --report-output scan-report.yaml
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Optional, Any, Tuple
from collections import defaultdict, Counter

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


class GovernanceScanner:
    """Comprehensive governance directory scanner with deep analysis."""
    
    # Known shared resource directory names (from governance-map.yaml)
    SHARED_RESOURCE_NAMES = [
        'ci', '23-policies', '31-schemas', '35-scripts', 
        'packages', 'dimensions', 'index', '_scratch', 
        '_legacy', 'examples'
    ]
    
    def __init__(
        self,
        governance_root: str = "governance",
        verbose: bool = False,
        report_format: str = "yaml"
    ):
        """
        Initialize the governance scanner.
        
        Args:
            governance_root: Path to governance directory
            verbose: Enable detailed output
            report_format: Report format (yaml, json, or text)
        """
        self.governance_root = Path(governance_root)
        self.verbose = verbose
        self.report_format = report_format
        
        # Scan results
        self.dimensions: List[Dict] = []
        self.shared_resources: List[Dict] = []
        self.orphaned_dirs: List[str] = []
        self.issues: List[Dict] = []
        self.statistics: Dict[str, Any] = {}
        self.recommendations: List[str] = []
        
        # Validation rules
        self.required_files = {
            'dimension': ['dimension.yaml'],
            'recommended': ['README.md', 'framework.yaml']
        }
        
    def log(self, message: str, level: str = "info") -> None:
        """Log message with appropriate color and level."""
        if level == "error":
            print(f"{Colors.FAIL}❌ ERROR: {message}{Colors.ENDC}")
        elif level == "warning":
            print(f"{Colors.WARNING}⚠️  WARNING: {message}{Colors.ENDC}")
        elif level == "info" and self.verbose:
            print(f"{Colors.OKBLUE}ℹ️  INFO: {message}{Colors.ENDC}")
        elif level == "success":
            print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
        elif level == "header":
            print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
            
    def load_governance_map(self) -> Optional[Dict]:
        """Load and parse governance-map.yaml."""
        map_file = self.governance_root / "governance-map.yaml"
        
        if not map_file.exists():
            self.log(f"governance-map.yaml not found at {map_file}", "warning")
            return None
            
        try:
            with open(map_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.log("Loaded governance-map.yaml successfully", "info")
                return data
        except Exception as e:
            self.log(f"Failed to load governance-map.yaml: {e}", "error")
            return None
    
    def scan_directory_structure(self) -> List[Path]:
        """Scan governance directory and return all subdirectories."""
        if not self.governance_root.exists():
            self.log(f"Governance root {self.governance_root} does not exist", "error")
            return []
            
        directories = []
        for item in self.governance_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                directories.append(item)
                
        self.log(f"Found {len(directories)} directories", "info")
        return sorted(directories)
    
    def classify_directory(self, dir_path: Path) -> Tuple[str, Optional[int]]:
        """
        Classify directory type (dimension, shared, or unknown).
        
        Returns:
            Tuple of (type, dimension_number) where type is one of:
            'dimension', 'shared', 'deprecated', 'unknown'
        """
        dir_name = dir_path.name
        
        # Pattern for numbered dimensions: 00-80 range
        numbered_pattern = r'^(\d{2})-([a-z-]+)$'
        match = re.match(numbered_pattern, dir_name)
        
        if match:
            num = int(match.group(1))
            if 0 <= num <= 80:
                return ('dimension', num)
            else:
                return ('unknown', num)
        
        # Check for special directories
        if dir_name.startswith('_'):
            return ('deprecated', None)
        
        # Check against known shared resources
        if dir_name in self.SHARED_RESOURCE_NAMES:
            return ('shared', None)
            
        return ('unknown', None)
    
    def scan_dimension_files(self, dir_path: Path) -> Dict[str, Any]:
        """
        Scan a dimension directory for required and recommended files.
        
        Returns:
            Dictionary with file existence status and metadata
        """
        result = {
            'path': str(dir_path),
            'name': dir_path.name,
            'files': {},
            'missing_required': [],
            'missing_recommended': [],
            'file_count': 0,
            'subdirs': [],
        }
        
        # Check required files
        for req_file in self.required_files['dimension']:
            file_path = dir_path / req_file
            exists = file_path.exists()
            result['files'][req_file] = exists
            
            if not exists:
                result['missing_required'].append(req_file)
        
        # Check recommended files
        for rec_file in self.required_files['recommended']:
            file_path = dir_path / rec_file
            exists = file_path.exists()
            result['files'][rec_file] = exists
            
            if not exists:
                result['missing_recommended'].append(rec_file)
        
        # Count files and subdirectories
        try:
            items = list(dir_path.iterdir())
            result['file_count'] = len([f for f in items if f.is_file()])
            result['subdirs'] = [d.name for d in items if d.is_dir() and not d.name.startswith('.')]
        except Exception as e:
            self.log(f"Error scanning {dir_path}: {e}", "warning")
            
        return result
    
    def parse_dimension_yaml(self, dir_path: Path) -> Optional[Dict]:
        """Parse dimension.yaml file if it exists."""
        dim_file = dir_path / "dimension.yaml"
        
        if not dim_file.exists():
            return None
            
        try:
            with open(dim_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.log(f"Failed to parse {dim_file}: {e}", "warning")
            return None
    
    def validate_naming_convention(self, dir_name: str) -> Dict[str, Any]:
        """
        Validate directory naming convention.
        
        Returns:
            Validation result with status and details
        """
        result = {
            'valid': False,
            'type': 'unknown',
            'issues': []
        }
        
        numbered_pattern = r'^(\d{2})-([a-z-]+)$'
        match = re.match(numbered_pattern, dir_name)
        
        if match:
            num = int(match.group(1))
            name = match.group(2)
            
            if 0 <= num <= 80:
                result['valid'] = True
                result['type'] = 'dimension'
                result['number'] = num
                result['name'] = name
                
                # Check name conventions
                if '_' in name:
                    result['issues'].append('Name contains underscore (should use hyphen)')
                if not name.islower():
                    result['issues'].append('Name is not lowercase')
            else:
                result['issues'].append(f'Number {num} out of range (should be 00-80)')
        else:
            # Unnumbered directory
            if dir_name.startswith('_'):
                result['type'] = 'deprecated'
                result['valid'] = True
            elif dir_name in self.SHARED_RESOURCE_NAMES:
                result['type'] = 'shared'
                result['valid'] = True
            else:
                result['issues'].append('Does not match any known pattern')
                
        return result
    
    def detect_orphaned_directories(
        self,
        actual_dirs: Set[str],
        governance_map: Optional[Dict]
    ) -> List[str]:
        """Detect directories not registered in governance-map.yaml."""
        if not governance_map:
            return []
            
        # Get registered names
        registered = set()
        
        for dim in governance_map.get('dimensions', []):
            registered.add(dim.get('name', ''))
            
        for shared in governance_map.get('shared_resources', []):
            registered.add(shared.get('name', ''))
        
        # Known special directories
        special = {'dimensions', '_scratch', '_legacy', 'index', 'examples'}
        registered |= special
        
        orphaned = actual_dirs - registered
        return sorted(list(orphaned))
    
    def analyze_dimension_coverage(self) -> Dict[str, Any]:
        """Analyze which dimensions (00-80) are present or missing."""
        present_dims = set()
        
        for dim in self.dimensions:
            if dim.get('number') is not None:
                present_dims.add(dim['number'])
        
        expected_range = set(range(81))  # 0-80
        missing_dims = expected_range - present_dims
        
        return {
            'total_expected': 81,
            'total_present': len(present_dims),
            'total_missing': len(missing_dims),
            'coverage_percentage': (len(present_dims) / 81) * 100,
            'present_dimensions': sorted(list(present_dims)),
            'missing_dimensions': sorted(list(missing_dims))
        }
    
    def generate_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive statistics about governance structure."""
        stats = {
            'scan_timestamp': datetime.now().isoformat() + 'Z',
            'governance_root': str(self.governance_root),
            'total_directories': len(self.dimensions) + len(self.shared_resources) + len(self.orphaned_dirs),
            'dimensions': {
                'total': len(self.dimensions),
                'with_dimension_yaml': len([d for d in self.dimensions if d.get('has_dimension_yaml')]),
                'with_readme': len([d for d in self.dimensions if d.get('files', {}).get('README.md')]),
                'with_framework_yaml': len([d for d in self.dimensions if d.get('files', {}).get('framework.yaml')]),
                'missing_required_files': len([d for d in self.dimensions if d.get('missing_required')]),
            },
            'shared_resources': {
                'total': len(self.shared_resources),
            },
            'orphaned_directories': {
                'total': len(self.orphaned_dirs),
                'list': self.orphaned_dirs
            },
            'issues': {
                'total': len(self.issues),
                'by_severity': Counter(i.get('severity') for i in self.issues)
            },
            'file_counts': {
                'total_files': sum(d.get('file_count', 0) for d in self.dimensions),
                'average_per_dimension': sum(d.get('file_count', 0) for d in self.dimensions) / max(len(self.dimensions), 1)
            }
        }
        
        # Add dimension coverage analysis
        coverage = self.analyze_dimension_coverage()
        stats['dimension_coverage'] = coverage
        
        return stats
    
    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on scan results."""
        recommendations = []
        
        # Missing required files
        missing_yaml = [d for d in self.dimensions if 'dimension.yaml' in d.get('missing_required', [])]
        if missing_yaml:
            recommendations.append(
                f"Create dimension.yaml files for {len(missing_yaml)} dimensions: "
                f"{', '.join(d['name'] for d in missing_yaml[:3])}{'...' if len(missing_yaml) > 3 else ''}"
            )
        
        # Missing README files
        missing_readme = [d for d in self.dimensions if 'README.md' in d.get('missing_recommended', [])]
        if missing_readme:
            recommendations.append(
                f"Add README.md documentation for {len(missing_readme)} dimensions"
            )
        
        # Orphaned directories
        if self.orphaned_dirs:
            recommendations.append(
                f"Register {len(self.orphaned_dirs)} orphaned directories in governance-map.yaml "
                f"or move to _legacy: {', '.join(self.orphaned_dirs[:3])}"
            )
        
        # Dimension coverage
        coverage = self.analyze_dimension_coverage()
        if coverage['total_missing'] > 0:
            recommendations.append(
                f"Consider implementing {coverage['total_missing']} missing governance dimensions "
                f"(current coverage: {coverage['coverage_percentage']:.1f}%)"
            )
        
        # Naming convention issues
        naming_issues = [i for i in self.issues if i.get('type') == 'naming_convention']
        if naming_issues:
            recommendations.append(
                f"Fix naming convention issues in {len(naming_issues)} directories"
            )
        
        return recommendations
    
    def scan(self) -> bool:
        """
        Execute comprehensive governance directory scan.
        
        Returns:
            True if scan completed successfully, False otherwise
        """
        self.log("=" * 80, "header")
        self.log("SynergyMesh Governance Directory Scanner", "header")
        self.log("=" * 80, "header")
        print()
        
        # Load governance map
        self.log("[1/6] Loading governance-map.yaml...", "header")
        governance_map = self.load_governance_map()
        
        # Scan directory structure
        self.log("\n[2/6] Scanning directory structure...", "header")
        directories = self.scan_directory_structure()
        
        if not directories:
            self.log("No directories found to scan", "error")
            return False
        
        # Classify and analyze directories
        self.log("\n[3/6] Classifying and analyzing directories...", "header")
        actual_dir_names = set()
        
        for dir_path in directories:
            dir_name = dir_path.name
            actual_dir_names.add(dir_name)
            
            dir_type, dim_num = self.classify_directory(dir_path)
            
            self.log(f"Analyzing {dir_name} (type: {dir_type})", "info")
            
            if dir_type == 'dimension':
                # Scan dimension files
                file_scan = self.scan_dimension_files(dir_path)
                file_scan['type'] = 'dimension'
                file_scan['number'] = dim_num
                
                # Parse dimension.yaml
                dim_yaml = self.parse_dimension_yaml(dir_path)
                file_scan['dimension_yaml_content'] = dim_yaml
                file_scan['has_dimension_yaml'] = dim_yaml is not None
                
                # Validate naming
                naming = self.validate_naming_convention(dir_name)
                file_scan['naming_validation'] = naming
                
                self.dimensions.append(file_scan)
                
                # Record issues
                if file_scan['missing_required']:
                    self.issues.append({
                        'type': 'missing_required_files',
                        'severity': 'error',
                        'directory': dir_name,
                        'details': file_scan['missing_required']
                    })
                
                if naming.get('issues'):
                    self.issues.append({
                        'type': 'naming_convention',
                        'severity': 'warning',
                        'directory': dir_name,
                        'details': naming['issues']
                    })
                    
            elif dir_type == 'shared':
                file_scan = self.scan_dimension_files(dir_path)
                file_scan['type'] = 'shared'
                self.shared_resources.append(file_scan)
                
            elif dir_type == 'deprecated':
                self.log(f"Skipping deprecated directory: {dir_name}", "info")
                
            else:
                self.log(f"Unknown directory type: {dir_name}", "warning")
        
        # Detect orphaned directories
        self.log("\n[4/6] Detecting orphaned directories...", "header")
        self.orphaned_dirs = self.detect_orphaned_directories(actual_dir_names, governance_map)
        
        if self.orphaned_dirs:
            self.log(f"Found {len(self.orphaned_dirs)} orphaned directories", "warning")
            for orphan in self.orphaned_dirs:
                self.log(f"  - {orphan}", "warning")
        else:
            self.log("No orphaned directories found", "success")
        
        # Generate statistics
        self.log("\n[5/6] Generating statistics...", "header")
        self.statistics = self.generate_statistics()
        
        # Generate recommendations
        self.log("\n[6/6] Generating recommendations...", "header")
        self.recommendations = self.generate_recommendations()
        
        self.log("\n✅ Scan completed successfully", "success")
        return True
    
    def print_summary(self) -> None:
        """Print scan summary to console."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}")
        print("Governance Directory Scan Summary")
        print(f"{'=' * 80}{Colors.ENDC}\n")
        
        stats = self.statistics
        
        # Directory counts
        print(f"{Colors.BOLD}Directory Structure:{Colors.ENDC}")
        print(f"  Total directories: {stats['total_directories']}")
        print(f"  Dimensions (00-80): {stats['dimensions']['total']}")
        print(f"  Shared resources: {stats['shared_resources']['total']}")
        print(f"  Orphaned directories: {stats['orphaned_directories']['total']}")
        
        # Dimension coverage
        coverage = stats.get('dimension_coverage', {})
        print(f"\n{Colors.BOLD}Dimension Coverage:{Colors.ENDC}")
        print(f"  Expected dimensions: {coverage.get('total_expected', 0)}")
        print(f"  Present: {coverage.get('total_present', 0)}")
        print(f"  Missing: {coverage.get('total_missing', 0)}")
        print(f"  Coverage: {coverage.get('coverage_percentage', 0):.1f}%")
        
        # File completeness
        print(f"\n{Colors.BOLD}File Completeness:{Colors.ENDC}")
        dims = stats['dimensions']
        print(f"  With dimension.yaml: {dims['with_dimension_yaml']}/{dims['total']}")
        print(f"  With README.md: {dims['with_readme']}/{dims['total']}")
        print(f"  With framework.yaml: {dims['with_framework_yaml']}/{dims['total']}")
        print(f"  Missing required files: {dims['missing_required_files']}")
        
        # Issues
        print(f"\n{Colors.BOLD}Issues Found:{Colors.ENDC}")
        print(f"  Total issues: {stats['issues']['total']}")
        
        if self.issues:
            by_severity = stats['issues']['by_severity']
            for severity, count in by_severity.items():
                color = Colors.FAIL if severity == 'error' else Colors.WARNING
                print(f"  {color}{severity.upper()}: {count}{Colors.ENDC}")
        
        # Recommendations
        if self.recommendations:
            print(f"\n{Colors.BOLD}Recommendations:{Colors.ENDC}")
            for i, rec in enumerate(self.recommendations, 1):
                print(f"  {i}. {rec}")
        
        print(f"\n{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")
    
    def generate_report(self, output_path: Optional[str] = None) -> str:
        """
        Generate detailed scan report in specified format.
        
        Args:
            output_path: Optional file path to write report
            
        Returns:
            Report content as string
        """
        report = {
            'metadata': {
                'scan_timestamp': self.statistics.get('scan_timestamp'),
                'governance_root': self.statistics.get('governance_root'),
                'scanner_version': '1.0.0'
            },
            'statistics': self.statistics,
            'dimensions': self.dimensions,
            'shared_resources': self.shared_resources,
            'orphaned_directories': self.orphaned_dirs,
            'issues': self.issues,
            'recommendations': self.recommendations
        }
        
        # Format report
        if self.report_format == 'json':
            content = json.dumps(report, indent=2, ensure_ascii=False)
        elif self.report_format == 'yaml':
            content = yaml.dump(report, default_flow_style=False, allow_unicode=True, sort_keys=False)
        else:  # text
            content = self._format_text_report(report)
        
        # Write to file if specified
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"Report written to {output_path}", "success")
            except Exception as e:
                self.log(f"Failed to write report: {e}", "error")
        
        return content
    
    def _format_text_report(self, report: Dict) -> str:
        """Format report as human-readable text."""
        lines = [
            "=" * 80,
            "SynergyMesh Governance Directory Scan Report",
            "=" * 80,
            "",
            f"Scan Timestamp: {report['metadata']['scan_timestamp']}",
            f"Governance Root: {report['metadata']['governance_root']}",
            "",
            "STATISTICS",
            "-" * 80,
        ]
        
        stats = report['statistics']
        lines.extend([
            f"Total Directories: {stats['total_directories']}",
            f"Dimensions: {stats['dimensions']['total']}",
            f"Shared Resources: {stats['shared_resources']['total']}",
            f"Orphaned: {stats['orphaned_directories']['total']}",
            f"Total Issues: {stats['issues']['total']}",
            "",
            "DIMENSION COVERAGE",
            "-" * 80,
        ])
        
        coverage = stats.get('dimension_coverage', {})
        lines.extend([
            f"Coverage: {coverage.get('coverage_percentage', 0):.1f}% ({coverage.get('total_present', 0)}/81)",
            f"Missing Dimensions: {', '.join(map(str, coverage.get('missing_dimensions', [])[:20]))}",
            "",
            "RECOMMENDATIONS",
            "-" * 80,
        ])
        
        for i, rec in enumerate(report.get('recommendations', []), 1):
            lines.append(f"{i}. {rec}")
        
        lines.extend(["", "=" * 80])
        
        return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Comprehensive governance directory scanner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python governance/35-scripts/scan-governance-directory.py
  python governance/35-scripts/scan-governance-directory.py --verbose
  python governance/35-scripts/scan-governance-directory.py --report-output scan-report.yaml
  python governance/35-scripts/scan-governance-directory.py --report-format json --report-output report.json
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
    
    parser.add_argument(
        '--report-format',
        choices=['yaml', 'json', 'text'],
        default='yaml',
        help='Report output format (default: yaml)'
    )
    
    parser.add_argument(
        '--report-output',
        help='Write report to specified file'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress console output (only write report file)'
    )
    
    args = parser.parse_args()
    
    # Create scanner
    scanner = GovernanceScanner(
        governance_root=args.governance_root,
        verbose=args.verbose,
        report_format=args.report_format
    )
    
    # Run scan
    success = scanner.scan()
    
    if not success:
        return 1
    
    # Print summary unless quiet
    if not args.quiet:
        scanner.print_summary()
    
    # Generate report
    if args.report_output or args.quiet:
        scanner.generate_report(args.report_output)
    
    # Exit with appropriate code
    return 0 if len(scanner.issues) == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
