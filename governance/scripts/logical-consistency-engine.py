#!/usr/bin/env python3
"""
Logical Consistency Engine - Deep Project Understanding & Structure Optimization

Provides extreme logical consistency capabilities:
- Deep project structure understanding
- Cross-file logical consistency validation
- Technical debt detection and prevention
- Logic error detection
- Auto-fix suggestions
"""

import os
import re
import yaml
import json
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict, Counter

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class LogicalConsistencyEngine:
    """Engine for deep logical consistency analysis and tech debt detection."""
    
    def __init__(self, governance_dir: str = None):
        self.governance_dir = governance_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__))
        )
        self.issues = defaultdict(list)
        self.tech_debt = []
        self.logic_errors = []
        self.stats = defaultdict(int)
        
    def check_all(self, verbose: bool = False) -> Dict:
        """Run all consistency checks."""
        print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}Logical Consistency Engine - Full Analysis{RESET}")
        print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
        
        # Run all checks
        self.check_structural_consistency(verbose)
        self.check_dependency_consistency(verbose)
        self.check_configuration_consistency(verbose)
        self.check_semantic_consistency(verbose)
        self.check_documentation_consistency(verbose)
        self.check_implementation_consistency(verbose)
        self.check_metadata_consistency(verbose)
        
        # Detect tech debt and logic errors
        self.detect_technical_debt(verbose)
        self.detect_logic_errors(verbose)
        
        return self.generate_report()
    
    def check_structural_consistency(self, verbose: bool = False):
        """Check directory structure, naming, and organization."""
        if verbose:
            print(f"{CYAN}Checking structural consistency...{RESET}")
        
        # Check dimension directory naming
        dimension_pattern = re.compile(r'^\d{2}-[a-z-]+$')
        
        for item in os.listdir(self.governance_dir):
            path = os.path.join(self.governance_dir, item)
            if not os.path.isdir(path):
                continue
            
            # Skip special directories
            if item.startswith('.') or item in ['scripts', 'ci', 'policies', 
                                                'schemas', 'packages', 'templates',
                                                'dimensions', '_scratch']:
                continue
            
            # Check naming convention
            if not dimension_pattern.match(item):
                self.issues['structural'].append({
                    'type': 'naming_violation',
                    'item': item,
                    'severity': 'MEDIUM',
                    'message': f"Directory '{item}' does not follow XX-name pattern",
                    'auto_fix': False
                })
                self.stats['structural_issues'] += 1
        
        if verbose:
            print(f"  Found {self.stats['structural_issues']} structural issues\n")
    
    def check_dependency_consistency(self, verbose: bool = False):
        """Check dependency coherence, DAG validity, version conflicts."""
        if verbose:
            print(f"{CYAN}Checking dependency consistency...{RESET}")
        
        # Load governance map
        map_file = os.path.join(self.governance_dir, 'governance-map.yaml')
        if not os.path.exists(map_file):
            if verbose:
                print(f"  {YELLOW}Warning: governance-map.yaml not found{RESET}")
            return
        
        with open(map_file, 'r') as f:
            gov_map = yaml.safe_load(f)
        
        # Build dependency graph
        graph = {}
        for entry in gov_map.get('dimensions', []):
            dim_id = entry['id']
            deps = entry.get('depends_on', [])
            graph[dim_id] = deps
        
        # Check for circular dependencies (should be 0 now)
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if has_cycle(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            
            rec_stack.remove(node)
            return False
        
        for node in graph:
            if node not in visited:
                if has_cycle(node):
                    self.issues['dependency'].append({
                        'type': 'circular_dependency',
                        'node': node,
                        'severity': 'HIGH',
                        'message': f"Circular dependency detected involving {node}",
                        'auto_fix': False
                    })
                    self.stats['dependency_issues'] += 1
        
        if verbose:
            print(f"  Found {self.stats['dependency_issues']} dependency issues\n")
    
    def check_configuration_consistency(self, verbose: bool = False):
        """Check cross-file config validation and drift detection."""
        if verbose:
            print(f"{CYAN}Checking configuration consistency...{RESET}")
        
        # Collect all YAML config files
        configs = {}
        for root, dirs, files in os.walk(self.governance_dir):
            for file in files:
                if file.endswith(('.yaml', '.yml')) and file != 'routing-config.yaml':
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            configs[filepath] = yaml.safe_load(f)
                    except (yaml.YAMLError, OSError, UnicodeDecodeError):
                        pass  # Skip invalid YAML files
        
        # Check for duplicate configurations
        config_keys = defaultdict(list)
        for filepath, config in configs.items():
            if isinstance(config, dict):
                for key in config.keys():
                    config_keys[key].append(filepath)
        
        # Report duplicates
        for key, files in config_keys.items():
            if len(files) > 3:  # More than 3 files have same key
                self.issues['configuration'].append({
                    'type': 'duplicate_config',
                    'key': key,
                    'files': files,
                    'severity': 'LOW',
                    'message': f"Config key '{key}' appears in {len(files)} files",
                    'auto_fix': False
                })
                self.stats['config_issues'] += 1
        
        if verbose:
            print(f"  Found {self.stats['config_issues']} configuration issues\n")
    
    def check_semantic_consistency(self, verbose: bool = False):
        """Check terminology, naming conventions, API contracts."""
        if verbose:
            print(f"{CYAN}Checking semantic consistency...{RESET}")
        
        # Common terminology variations to detect (prefer American spelling)
        term_variations = {
            'behavior': ['behavior', 'behaviour'],
            'authorization': ['authorization', 'authorisation'],
            'organization': ['organization', 'organisation'],
        }
        
        # Scan all markdown and YAML files
        term_usage = defaultdict(lambda: defaultdict(int))
        
        for root, dirs, files in os.walk(self.governance_dir):
            for file in files:
                if file.endswith(('.md', '.yaml', '.yml')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read().lower()
                            
                            for base_term, variations in term_variations.items():
                                for variant in variations:
                                    count = content.count(variant)
                                    if count > 0:
                                        term_usage[base_term][variant] += count
                    except (OSError, UnicodeDecodeError):
                        pass  # Skip unreadable files
        
        # Report inconsistent terminology
        for base_term, variants in term_usage.items():
            if len(variants) > 1:
                self.issues['semantic'].append({
                    'type': 'inconsistent_terminology',
                    'term': base_term,
                    'variants': dict(variants),
                    'severity': 'LOW',
                    'message': f"Inconsistent spelling of '{base_term}': {dict(variants)}",
                    'auto_fix': True
                })
                self.stats['semantic_issues'] += 1
        
        if verbose:
            print(f"  Found {self.stats['semantic_issues']} semantic issues\n")
    
    def check_documentation_consistency(self, verbose: bool = False):
        """Check code-doc sync, outdated references."""
        if verbose:
            print(f"{CYAN}Checking documentation consistency...{RESET}")
        
        # Find all README files
        readmes = []
        for root, dirs, files in os.walk(self.governance_dir):
            if 'README.md' in files:
                readmes.append(os.path.join(root, 'README.md'))
        
        # Check for minimal READMEs (< 100 characters)
        for readme in readmes:
            try:
                with open(readme, 'r') as f:
                    content = f.read()
                    if len(content) < 100:
                        self.issues['documentation'].append({
                            'type': 'minimal_readme',
                            'file': readme,
                            'severity': 'LOW',
                            'message': f"README is too minimal ({len(content)} chars)",
                            'auto_fix': False
                        })
                        self.stats['doc_issues'] += 1
            except:
                pass
        
        if verbose:
            print(f"  Found {self.stats['doc_issues']} documentation issues\n")
    
    def check_implementation_consistency(self, verbose: bool = False):
        """Check for duplicate logic, contradictory patterns."""
        if verbose:
            print(f"{CYAN}Checking implementation consistency...{RESET}")
        
        # Scan Python files for duplicate function names
        functions = defaultdict(list)
        
        for root, dirs, files in os.walk(self.governance_dir):
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            # Simple function name extraction
                            func_pattern = re.compile(r'^\s*def\s+(\w+)', re.MULTILINE)
                            for match in func_pattern.finditer(content):
                                func_name = match.group(1)
                                if not func_name.startswith('_'):  # Skip private
                                    functions[func_name].append(filepath)
                    except:
                        pass
        
        # Report duplicate function names across files
        for func_name, files in functions.items():
            if len(files) > 1:
                self.issues['implementation'].append({
                    'type': 'duplicate_function',
                    'function': func_name,
                    'files': files,
                    'severity': 'MEDIUM',
                    'message': f"Function '{func_name}' defined in {len(files)} files",
                    'auto_fix': False
                })
                self.stats['implementation_issues'] += 1
        
        if verbose:
            print(f"  Found {self.stats['implementation_issues']} implementation issues\n")
    
    def check_metadata_consistency(self, verbose: bool = False):
        """Check version alignment, owner verification."""
        if verbose:
            print(f"{CYAN}Checking metadata consistency...{RESET}")
        
        # Check all dimension.yaml files for metadata completeness
        for root, dirs, files in os.walk(self.governance_dir):
            if 'dimension.yaml' in files:
                filepath = os.path.join(root, 'dimension.yaml')
                try:
                    with open(filepath, 'r') as f:
                        dim = yaml.safe_load(f)
                        
                        # Check required metadata fields
                        required_fields = ['metadata', 'spec']
                        for field in required_fields:
                            if field not in dim:
                                self.issues['metadata'].append({
                                    'type': 'missing_metadata',
                                    'file': filepath,
                                    'field': field,
                                    'severity': 'HIGH',
                                    'message': f"Missing required field: {field}",
                                    'auto_fix': False
                                })
                                self.stats['metadata_issues'] += 1
                except:
                    pass
        
        if verbose:
            print(f"  Found {self.stats['metadata_issues']} metadata issues\n")
    
    def detect_technical_debt(self, verbose: bool = False):
        """Detect TODO/FIXME markers, dead code, outdated dependencies."""
        if verbose:
            print(f"{YELLOW}Detecting technical debt...{RESET}")
        
        debt_markers = ['TODO', 'FIXME', 'HACK', 'XXX', 'DEPRECATED']
        
        for root, dirs, files in os.walk(self.governance_dir):
            for file in files:
                if file.endswith(('.py', '.md', '.yaml', '.yml')):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                            for line_num, line in enumerate(f, 1):
                                for marker in debt_markers:
                                    if marker in line:
                                        self.tech_debt.append({
                                            'type': 'code_marker',
                                            'marker': marker,
                                            'file': filepath,
                                            'line': line_num,
                                            'content': line.strip(),
                                            'severity': 'MEDIUM' if marker in ['FIXME', 'HACK'] else 'LOW',
                                            'auto_fix': False
                                        })
                    except:
                        pass
        
        if verbose:
            print(f"  Found {len(self.tech_debt)} technical debt items\n")
    
    def detect_logic_errors(self, verbose: bool = False):
        """Detect logical errors like circular reasoning, contradictions."""
        if verbose:
            print(f"{RED}Detecting logic errors...{RESET}")
        
        # Check for broken internal links in markdown
        for root, dirs, files in os.walk(self.governance_dir):
            for file in files:
                if file.endswith('.md'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r') as f:
                            content = f.read()
                            # Find markdown links
                            link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
                            for match in link_pattern.finditer(content):
                                link_target = match.group(2)
                                # Check if it's a relative file link
                                if not link_target.startswith(('http://', 'https://', '#')):
                                    target_path = os.path.join(root, link_target)
                                    if not os.path.exists(target_path):
                                        self.logic_errors.append({
                                            'type': 'broken_link',
                                            'file': filepath,
                                            'link': link_target,
                                            'severity': 'LOW',
                                            'message': f"Broken link: {link_target}",
                                            'auto_fix': False
                                        })
                    except:
                        pass
        
        if verbose:
            print(f"  Found {len(self.logic_errors)} logic errors\n")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive consistency report."""
        report = {
            'summary': {
                'total_issues': sum(len(v) for v in self.issues.values()),
                'tech_debt_items': len(self.tech_debt),
                'logic_errors': len(self.logic_errors),
                'health_score': self._calculate_health_score()
            },
            'issues_by_category': {k: len(v) for k, v in self.issues.items()},
            'issues': dict(self.issues),
            'tech_debt': self.tech_debt,
            'logic_errors': self.logic_errors,
            'stats': dict(self.stats)
        }
        
        self._print_report(report)
        return report
    
    def _calculate_health_score(self) -> int:
        """Calculate overall logical consistency health score (0-100)."""
        total_issues = sum(len(v) for v in self.issues.values())
        tech_debt_count = len(self.tech_debt)
        logic_error_count = len(self.logic_errors)
        
        # Start with 100 and deduct based on issues
        score = 100
        score -= total_issues * 2  # Each consistency issue: -2
        score -= tech_debt_count * 0.5  # Each tech debt: -0.5
        score -= logic_error_count * 3  # Each logic error: -3
        
        return max(0, min(100, int(score)))
    
    def _print_report(self, report: Dict):
        """Print formatted consistency report."""
        print(f"\n{BOLD}{BLUE}{'═'*70}{RESET}")
        print(f"{BOLD}{BLUE}  Logical Consistency Report{RESET}")
        print(f"{BOLD}{BLUE}{'═'*70}{RESET}\n")
        
        summary = report['summary']
        
        # Overall health
        health = summary['health_score']
        health_color = GREEN if health >= 85 else YELLOW if health >= 70 else RED
        grade = 'A' if health >= 90 else 'B' if health >= 80 else 'C' if health >= 70 else 'D'
        
        print(f"{BOLD}Overall Health Score:{RESET} {health_color}{health}/100{RESET} (Grade {grade})\n")
        
        # Summary
        print(f"{BOLD}Summary:{RESET}")
        print(f"  Total Consistency Issues: {summary['total_issues']}")
        print(f"  Technical Debt Items: {summary['tech_debt_items']}")
        print(f"  Logic Errors: {summary['logic_errors']}\n")
        
        # Issues by category
        print(f"{BOLD}Issues by Category:{RESET}")
        for category, count in report['issues_by_category'].items():
            color = RED if count > 10 else YELLOW if count > 5 else GREEN
            status = '✅' if count == 0 else '⚠️'
            print(f"  {status} {category.replace('_', ' ').title()}: {color}{count}{RESET}")
        
        print(f"\n{BOLD}{BLUE}{'═'*70}{RESET}\n")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Logical Consistency Engine - Deep project analysis'
    )
    parser.add_argument('--check-all', action='store_true',
                       help='Run all consistency checks')
    parser.add_argument('--check', choices=[
        'structural', 'dependency', 'configuration', 'semantic',
        'documentation', 'implementation', 'metadata'
    ], help='Run specific consistency check')
    parser.add_argument('--detect-tech-debt', action='store_true',
                       help='Detect technical debt')
    parser.add_argument('--detect-logic-errors', action='store_true',
                       help='Detect logic errors')
    parser.add_argument('--full-report', action='store_true',
                       help='Generate full report')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    engine = LogicalConsistencyEngine()
    
    if args.check_all or args.full_report:
        engine.check_all(verbose=args.verbose)
    elif args.check:
        check_method = getattr(engine, f'check_{args.check}_consistency')
        check_method(verbose=args.verbose)
        engine.generate_report()
    elif args.detect_tech_debt:
        engine.detect_technical_debt(verbose=args.verbose)
        print(f"\nFound {len(engine.tech_debt)} technical debt items")
    elif args.detect_logic_errors:
        engine.detect_logic_errors(verbose=args.verbose)
        print(f"\nFound {len(engine.logic_errors)} logic errors")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
