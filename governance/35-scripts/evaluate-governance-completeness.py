#!/usr/bin/env python3
"""
SynergyMesh Governance Completeness Evaluator

Purpose: Evaluate the completeness percentage of each governance dimension.

Scoring Criteria:
- dimension.yaml exists: 30%
- README.md exists: 20%
- framework.yaml exists: 15%
- Has subdirectories (organized structure): 10%
- Has policy files (*.rego): 10%
- Has schema files (*.json): 10%
- Has additional documentation (*.md > 1): 5%

Total: 100%

Usage:
    python governance/35-scripts/evaluate-governance-completeness.py
    python governance/35-scripts/evaluate-governance-completeness.py --verbose
    python governance/35-scripts/evaluate-governance-completeness.py --output completeness-report.yaml
    python governance/35-scripts/evaluate-governance-completeness.py --threshold 80
"""

import os
import sys
import yaml
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class CompletenessEvaluator:
    """Evaluate completeness of governance dimensions."""
    
    # Scoring weights
    WEIGHTS = {
        'dimension_yaml': 30,
        'readme': 20,
        'framework_yaml': 15,
        'has_subdirectories': 10,
        'has_policies': 10,
        'has_schemas': 10,
        'has_extra_docs': 5,
    }
    
    def __init__(self, governance_root: str = "governance", verbose: bool = False):
        """Initialize evaluator."""
        self.governance_root = Path(governance_root)
        self.verbose = verbose
        self.results: List[Dict] = []
        
    def log(self, message: str, level: str = "info") -> None:
        """Log message with color."""
        if level == "error":
            print(f"{Colors.FAIL}❌ {message}{Colors.ENDC}")
        elif level == "warning":
            print(f"{Colors.WARNING}⚠️  {message}{Colors.ENDC}")
        elif level == "info" and self.verbose:
            print(f"{Colors.OKBLUE}ℹ️  {message}{Colors.ENDC}")
        elif level == "success":
            print(f"{Colors.OKGREEN}✅ {message}{Colors.ENDC}")
            
    def is_dimension_directory(self, dir_name: str) -> bool:
        """Check if directory is a numbered dimension (00-80)."""
        pattern = r'^(\d{2})-([a-z-]+)$'
        match = re.match(pattern, dir_name)
        if match:
            num = int(match.group(1))
            return 0 <= num <= 80
        return False
        
    def evaluate_dimension(self, dim_path: Path) -> Dict[str, Any]:
        """
        Evaluate a single dimension directory.
        
        Returns:
            Dictionary with evaluation results and score
        """
        result = {
            'name': dim_path.name,
            'path': str(dim_path),
            'scores': {},
            'total_score': 0,
            'percentage': 0.0,
            'grade': '',
            'missing': [],
            'recommendations': []
        }
        
        # Check dimension.yaml
        if (dim_path / 'dimension.yaml').exists():
            result['scores']['dimension_yaml'] = self.WEIGHTS['dimension_yaml']
        else:
            result['missing'].append('dimension.yaml')
            result['recommendations'].append(f"Create dimension.yaml")
            
        # Check README.md
        if (dim_path / 'README.md').exists():
            result['scores']['readme'] = self.WEIGHTS['readme']
        else:
            result['missing'].append('README.md')
            result['recommendations'].append(f"Add README.md documentation")
            
        # Check framework.yaml
        if (dim_path / 'framework.yaml').exists():
            result['scores']['framework_yaml'] = self.WEIGHTS['framework_yaml']
        else:
            result['missing'].append('framework.yaml')
            result['recommendations'].append(f"Add framework.yaml configuration")
            
        # Check for subdirectories (organized structure)
        subdirs = [d for d in dim_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
        if len(subdirs) > 0:
            result['scores']['has_subdirectories'] = self.WEIGHTS['has_subdirectories']
            result['subdirectory_count'] = len(subdirs)
        else:
            result['recommendations'].append(f"Consider organizing with subdirectories")
            
        # Check for policy files (*.rego)
        policy_files = list(dim_path.glob('**/*.rego'))
        if len(policy_files) > 0:
            result['scores']['has_policies'] = self.WEIGHTS['has_policies']
            result['policy_count'] = len(policy_files)
        else:
            result['recommendations'].append(f"Consider adding OPA/Rego policies")
            
        # Check for schema files (*.schema.json or schema.json)
        schema_files = [f for f in dim_path.glob('**/*.json') if f.name.endswith('.schema.json') or f.name == 'schema.json']
        if len(schema_files) > 0:
            result['scores']['has_schemas'] = self.WEIGHTS['has_schemas']
            result['schema_count'] = len(schema_files)
        else:
            result['recommendations'].append(f"Consider adding JSON schemas")
            
        # Check for additional documentation
        md_files = list(dim_path.glob('**/*.md'))
        if len(md_files) > 1:  # More than just README.md
            result['scores']['has_extra_docs'] = self.WEIGHTS['has_extra_docs']
            result['doc_count'] = len(md_files)
        else:
            result['recommendations'].append(f"Consider adding more documentation")
            
        # Calculate total
        result['total_score'] = sum(result['scores'].values())
        result['percentage'] = round(result['total_score'], 1)
        result['grade'] = self.get_grade(result['percentage'])
        
        return result
        
    def get_grade(self, percentage: float) -> str:
        """Get letter grade based on percentage."""
        if percentage >= 90:
            return 'A'
        elif percentage >= 80:
            return 'B'
        elif percentage >= 70:
            return 'C'
        elif percentage >= 60:
            return 'D'
        else:
            return 'F'
            
    def get_grade_color(self, grade: str) -> str:
        """Get color for grade."""
        if grade == 'A':
            return Colors.OKGREEN
        elif grade == 'B':
            return Colors.OKCYAN
        elif grade == 'C':
            return Colors.WARNING
        else:
            return Colors.FAIL
            
    def scan_all_dimensions(self) -> List[Dict]:
        """Scan all dimension directories."""
        if not self.governance_root.exists():
            self.log(f"Governance root {self.governance_root} does not exist", "error")
            return []
            
        results = []
        
        for item in sorted(self.governance_root.iterdir()):
            if item.is_dir() and self.is_dimension_directory(item.name):
                self.log(f"Evaluating {item.name}...", "info")
                result = self.evaluate_dimension(item)
                results.append(result)
                
        self.results = results
        return results
        
    def generate_statistics(self) -> Dict[str, Any]:
        """Generate overall statistics."""
        if not self.results:
            return {}
            
        total_dims = len(self.results)
        avg_percentage = sum(r['percentage'] for r in self.results) / total_dims
        
        grade_counts = defaultdict(int)
        for r in self.results:
            grade_counts[r['grade']] += 1
            
        # Find dimensions below threshold
        below_60 = [r for r in self.results if r['percentage'] < 60]
        below_80 = [r for r in self.results if 60 <= r['percentage'] < 80]
        excellent = [r for r in self.results if r['percentage'] >= 90]
        
        stats = {
            'total_dimensions': total_dims,
            'average_completeness': round(avg_percentage, 1),
            'grade_distribution': dict(grade_counts),
            'excellent_count': len(excellent),
            'needs_improvement_count': len(below_80) + len(below_60),
            'critical_count': len(below_60),
            'excellent_dimensions': [r['name'] for r in excellent],
            'needs_improvement': [r['name'] for r in below_80],
            'critical_dimensions': [r['name'] for r in below_60],
        }
        
        return stats
        
    def print_report(self) -> None:
        """Print completeness report to console."""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
        print(f"Governance Completeness Evaluation Report")
        print(f"{'='*80}{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}Evaluation Criteria:{Colors.ENDC}")
        print(f"  dimension.yaml exists:     {self.WEIGHTS['dimension_yaml']}%")
        print(f"  README.md exists:          {self.WEIGHTS['readme']}%")
        print(f"  framework.yaml exists:     {self.WEIGHTS['framework_yaml']}%")
        print(f"  Has subdirectories:        {self.WEIGHTS['has_subdirectories']}%")
        print(f"  Has policy files (*.rego): {self.WEIGHTS['has_policies']}%")
        print(f"  Has schema files (*.json): {self.WEIGHTS['has_schemas']}%")
        print(f"  Has extra documentation:   {self.WEIGHTS['has_extra_docs']}%")
        print()
        
        # Summary statistics
        stats = self.generate_statistics()
        print(f"{Colors.BOLD}Overall Statistics:{Colors.ENDC}")
        print(f"  Total Dimensions:          {stats['total_dimensions']}")
        print(f"  Average Completeness:      {stats['average_completeness']}%")
        print(f"  Grade Distribution:")
        for grade in ['A', 'B', 'C', 'D', 'F']:
            count = stats['grade_distribution'].get(grade, 0)
            color = self.get_grade_color(grade)
            print(f"    {color}{grade}{Colors.ENDC}: {count}")
        print()
        
        # Excellent dimensions
        if stats['excellent_count'] > 0:
            print(f"{Colors.OKGREEN}{Colors.BOLD}✨ Excellent (≥90%):{Colors.ENDC} {stats['excellent_count']} dimensions")
            for name in stats['excellent_dimensions'][:5]:  # Show top 5
                result = next(r for r in self.results if r['name'] == name)
                print(f"  {Colors.OKGREEN}• {name}: {result['percentage']}%{Colors.ENDC}")
            if len(stats['excellent_dimensions']) > 5:
                print(f"  ... and {len(stats['excellent_dimensions']) - 5} more")
            print()
            
        # Critical dimensions
        if stats['critical_count'] > 0:
            print(f"{Colors.FAIL}{Colors.BOLD}⚠️  Critical (<60%):{Colors.ENDC} {stats['critical_count']} dimensions")
            for name in stats['critical_dimensions']:
                result = next(r for r in self.results if r['name'] == name)
                print(f"  {Colors.FAIL}• {name}: {result['percentage']}%{Colors.ENDC}")
                for rec in result['recommendations'][:2]:  # Show top 2 recommendations
                    print(f"    → {rec}")
            print()
            
        # Detailed results table
        print(f"{Colors.BOLD}Detailed Completeness by Dimension:{Colors.ENDC}\n")
        print(f"{'Dimension':<30} {'Score':<8} {'Grade':<7} {'Status':<20}")
        print(f"{'-'*30} {'-'*8} {'-'*7} {'-'*20}")
        
        for result in sorted(self.results, key=lambda x: x['percentage'], reverse=True):
            color = self.get_grade_color(result['grade'])
            status = "Excellent" if result['percentage'] >= 90 else \
                     "Good" if result['percentage'] >= 80 else \
                     "Needs Work" if result['percentage'] >= 60 else \
                     "Critical"
            print(f"{result['name']:<30} {color}{result['percentage']:<7}%{Colors.ENDC} {color}{result['grade']:<7}{Colors.ENDC} {status:<20}")
            
        print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
        
    def save_report(self, output_path: str, format: str = "yaml") -> None:
        """Save report to file."""
        report = {
            'metadata': {
                'scan_timestamp': datetime.utcnow().isoformat() + 'Z',
                'governance_root': str(self.governance_root),
                'evaluator_version': '1.0.0'
            },
            'statistics': self.generate_statistics(),
            'dimensions': self.results
        }
        
        output_file = Path(output_path)
        
        if format == 'yaml':
            with open(output_file, 'w', encoding='utf-8') as f:
                yaml.dump(report, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        elif format == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        else:
            self.log(f"Unknown format: {format}", "error")
            return
            
        self.log(f"Report saved to {output_file}", "success")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Evaluate completeness of SynergyMesh governance dimensions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python governance/35-scripts/evaluate-governance-completeness.py
  python governance/35-scripts/evaluate-governance-completeness.py --verbose
  python governance/35-scripts/evaluate-governance-completeness.py --output completeness-report.yaml
  python governance/35-scripts/evaluate-governance-completeness.py --threshold 80
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
        '--output', '-o',
        help='Output file path for report'
    )
    
    parser.add_argument(
        '--format', '-f',
        choices=['yaml', 'json'],
        default='yaml',
        help='Output format (default: yaml)'
    )
    
    parser.add_argument(
        '--threshold', '-t',
        type=float,
        default=60.0,
        help='Completeness threshold for warnings (default: 60)'
    )
    
    args = parser.parse_args()
    
    # Run evaluation
    evaluator = CompletenessEvaluator(
        governance_root=args.governance_root,
        verbose=args.verbose
    )
    
    evaluator.scan_all_dimensions()
    evaluator.print_report()
    
    # Save report if requested
    if args.output:
        evaluator.save_report(args.output, args.format)
    
    # Check threshold
    stats = evaluator.generate_statistics()
    if stats['average_completeness'] < args.threshold:
        print(f"{Colors.WARNING}⚠️  Warning: Average completeness ({stats['average_completeness']}%) is below threshold ({args.threshold}%){Colors.ENDC}")
        sys.exit(1)
    
    print(f"{Colors.OKGREEN}✅ Evaluation completed successfully{Colors.ENDC}\n")
    sys.exit(0)


if __name__ == '__main__':
    main()
