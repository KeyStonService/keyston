#!/usr/bin/env python3
"""
Language Governance Analyzer
語言治理分析器

Enhanced analyzer for CI/CD integration with multiple output formats
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml


class LanguageGovernanceAnalyzer:
    """Enhanced language governance analyzer for CI/CD"""
    
    # Language file extension mapping
    LANGUAGE_EXTENSIONS = {
        'TypeScript': ['.ts', '.tsx'],
        'JavaScript': ['.js', '.jsx'],
        'Python': ['.py', '.pyi'],
        'C++': ['.cpp', '.cc', '.cxx', '.hpp', '.h', '.hxx'],
        'C': ['.c', '.h'],
        'Go': ['.go'],
        'Rust': ['.rs'],
        'Rego': ['.rego'],
        'Bash': ['.sh', '.bash'],
        'PHP': ['.php'],
        'Ruby': ['.rb'],
        'Lua': ['.lua'],
        'Perl': ['.pl', '.pm'],
        'Swift': ['.swift'],
        'Kotlin': ['.kt', '.kts'],
        'Java': ['.java'],
        'HCL': ['.tf', '.hcl'],
    }
    
    def __init__(self, repo_root: str, policy_file: str):
        self.repo_root = Path(repo_root)
        self.policy_file = Path(policy_file)
        self.policy = self._load_policy()
        self.violations = []
        self.stats = defaultdict(lambda: defaultdict(int))
        self.total_files = 0
    
    def _load_policy(self) -> dict:
        """Load language policy configuration"""
        try:
            with open(self.policy_file, encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"❌ Error loading policy file {self.policy_file}: {e}", file=sys.stderr)
            sys.exit(1)
    
    def _get_language_from_extension(self, ext: str) -> str:
        """Determine language from file extension"""
        for language, extensions in self.LANGUAGE_EXTENSIONS.items():
            if ext.lower() in extensions:
                return language
        return 'Unknown'
    
    def _is_allowed_language(self, language: str, allowed_list: list[str]) -> bool:
        """Check if language is in allowed list"""
        return language in allowed_list
    
    def _check_directory_rules(self):
        """Check directory-level language rules"""
        directory_rules = self.policy.get('directory_rules', {})
        
        for dir_pattern, rules in directory_rules.items():
            dir_path = dir_pattern.rstrip('/')
            full_path = self.repo_root / dir_path
            
            if not full_path.exists():
                continue
            
            allowed_languages = rules.get('allowed_languages', [])
            forbidden_patterns = rules.get('forbidden_patterns', [])
            
            for file_path in full_path.rglob('*'):
                if not file_path.is_file():
                    continue
                
                if '.git' in file_path.parts or 'node_modules' in file_path.parts:
                    continue
                
                ext = file_path.suffix
                if not ext:
                    continue
                
                self.total_files += 1
                language = self._get_language_from_extension(ext)
                
                # Update statistics
                self.stats[dir_pattern][language] += 1
                
                if language == 'Unknown':
                    continue
                
                # Check if language is allowed
                if not self._is_allowed_language(language, allowed_languages):
                    # Check if it's a data format
                    data_formats = self.policy.get('global_policy', {}).get('data_formats', [])
                    if language not in data_formats:
                        self.violations.append({
                            'type': 'LANGUAGE_NOT_ALLOWED',
                            'severity': 'ERROR',
                            'file': str(file_path.relative_to(self.repo_root)),
                            'directory': dir_pattern,
                            'language': language,
                            'allowed': allowed_languages,
                            'message': f'{language} is not allowed in {dir_pattern}'
                        })
                
                # Check forbidden patterns
                for pattern in forbidden_patterns:
                    if file_path.match(pattern):
                        self.violations.append({
                            'type': 'FORBIDDEN_PATTERN',
                            'severity': 'ERROR',
                            'file': str(file_path.relative_to(self.repo_root)),
                            'directory': dir_pattern,
                            'pattern': pattern,
                            'message': f'File matches forbidden pattern {pattern}'
                        })
    
    def _check_forbidden_languages(self):
        """Check globally forbidden languages"""
        forbidden = self.policy.get('global_policy', {}).get('forbidden_languages', [])
        
        for file_path in self.repo_root.rglob('*'):
            if not file_path.is_file():
                continue
            
            if '.git' in file_path.parts or 'node_modules' in file_path.parts:
                continue
            
            ext = file_path.suffix
            if not ext:
                continue
            
            language = self._get_language_from_extension(ext)
            
            if language in forbidden:
                self.violations.append({
                    'type': 'GLOBALLY_FORBIDDEN',
                    'severity': 'CRITICAL',
                    'file': str(file_path.relative_to(self.repo_root)),
                    'language': language,
                    'message': f'{language} is globally forbidden'
                })
    
    def analyze(self) -> bool:
        """Run all checks"""
        print("🔍 Analyzing language governance...")
        print(f"Repository: {self.repo_root}")
        print(f"Policy: {self.policy_file}\n")
        
        self._check_directory_rules()
        self._check_forbidden_languages()
        
        return len(self.violations) == 0
    
    def generate_json_report(self) -> dict:
        """Generate JSON report"""
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'repository': str(self.repo_root),
            'policy_file': str(self.policy_file),
            'total_files': self.total_files,
            'violations': self.violations,
            'stats': dict(self.stats),
            'summary': {
                'total_violations': len(self.violations),
                'by_severity': self._count_by_severity(),
                'by_type': self._count_by_type()
            }
        }
    
    def generate_markdown_report(self) -> str:
        """Generate Markdown report for PR comments"""
        lines = []
        
        if not self.violations:
            lines.append("### ✅ No Language Governance Violations\n")
            lines.append("All files comply with the language policy.\n")
        else:
            lines.append(f"### ⚠️ Language Governance Violations ({len(self.violations)})\n")
            
            by_severity = defaultdict(list)
            for v in self.violations:
                by_severity[v['severity']].append(v)
            
            for severity in ['CRITICAL', 'ERROR', 'WARNING']:
                violations = by_severity.get(severity, [])
                if violations:
                    icon = '🔴' if severity == 'CRITICAL' else ('⚠️' if severity == 'ERROR' else '💡')
                    lines.append(f"\n#### {icon} {severity} ({len(violations)})\n")
                    
                    for v in violations[:10]:  # Limit to first 10
                        lines.append(f"- **{v['message']}**")
                        lines.append(f"  - File: `{v['file']}`")
                        if 'language' in v:
                            lines.append(f"  - Language: {v['language']}")
                        if 'directory' in v:
                            lines.append(f"  - Directory: {v['directory']}")
                        lines.append("")
                    
                    if len(violations) > 10:
                        lines.append(f"_... and {len(violations) - 10} more_\n")
        
        # Add statistics
        if self.stats:
            lines.append("\n### 📊 Language Distribution\n")
            for directory, languages in sorted(self.stats.items()):
                if languages:
                    lines.append(f"**{directory}**")
                    for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]:
                        lines.append(f"- {lang}: {count} files")
                    lines.append("")
        
        # Add references
        lines.append("\n### 📚 References\n")
        lines.append("- [Language Stack Documentation](../blob/main/docs/architecture/language-stack.md)")
        lines.append("- [Language Governance](../blob/main/docs/architecture/language-governance.md)")
        lines.append("- [Language Policy](../blob/main/config/language-policy.yaml)")
        
        return '\n'.join(lines)
    
    def _count_by_severity(self) -> dict[str, int]:
        """Count violations by severity"""
        counts = defaultdict(int)
        for v in self.violations:
            counts[v['severity']] += 1
        return dict(counts)
    
    def _count_by_type(self) -> dict[str, int]:
        """Count violations by type"""
        counts = defaultdict(int)
        for v in self.violations:
            counts[v['type']] += 1
        return dict(counts)
    
    def print_console_report(self):
        """Print report to console"""
        print("\n" + "=" * 70)
        print("📊 Language Governance Analysis Report")
        print("=" * 70 + "\n")
        
        print(f"Total Files Scanned: {self.total_files}")
        print(f"Violations Found: {len(self.violations)}\n")
        
        if self.violations:
            by_severity = self._count_by_severity()
            print("By Severity:")
            for severity in ['CRITICAL', 'ERROR', 'WARNING']:
                if severity in by_severity:
                    icon = '🔴' if severity == 'CRITICAL' else ('⚠️' if severity == 'ERROR' else '💡')
                    print(f"  {icon} {severity}: {by_severity[severity]}")
            
            print("\nViolations:")
            print("-" * 70)
            
            for v in self.violations[:20]:  # Show first 20
                print(f"\n• {v['message']}")
                print(f"  File: {v['file']}")
                if 'language' in v:
                    print(f"  Language: {v['language']}")
                if 'directory' in v:
                    print(f"  Directory: {v['directory']}")
            
            if len(self.violations) > 20:
                print(f"\n... and {len(self.violations) - 20} more violations")
        else:
            print("✅ No violations detected!")
        
        print("\n" + "=" * 70)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Language Governance Analyzer for CI/CD'
    )
    parser.add_argument(
        '--config',
        required=True,
        help='Path to language-policy.yaml'
    )
    parser.add_argument(
        '--repo-root',
        default='.',
        help='Repository root directory'
    )
    parser.add_argument(
        '--output-format',
        choices=['console', 'json', 'markdown'],
        default='console',
        help='Output format'
    )
    parser.add_argument(
        '--output-file',
        help='Output file path (for json/markdown)'
    )
    
    args = parser.parse_args()
    
    # Check if policy file exists
    if not os.path.exists(args.config):
        print(f"❌ Error: Policy file not found: {args.config}", file=sys.stderr)
        sys.exit(1)
    
    # Create analyzer
    analyzer = LanguageGovernanceAnalyzer(args.repo_root, args.config)
    
    # Run analysis
    analyzer.analyze()
    
    # Generate output
    if args.output_format == 'json':
        report = analyzer.generate_json_report()
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            print(f"✅ JSON report saved to {args.output_file}")
        else:
            print(json.dumps(report, indent=2, ensure_ascii=False))
    
    elif args.output_format == 'markdown':
        report = analyzer.generate_markdown_report()
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Markdown report saved to {args.output_file}")
        else:
            print(report)
    
    else:  # console
        analyzer.print_console_report()
    
    # Exit with error if violations found
    sys.exit(0 if len(analyzer.violations) == 0 else 1)

if __name__ == '__main__':
    main()
