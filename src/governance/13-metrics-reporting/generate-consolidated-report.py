#!/usr/bin/env python3
"""
Consolidated Security Report Generator
綜合安全報告生成器

Combines results from Language Governance, CodeQL, and Semgrep
"""

import argparse
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


class ConsolidatedReportGenerator:
    """Generate consolidated security and governance report"""
    
    def __init__(self, results_dir: str, output_file: str):
        self.results_dir = Path(results_dir)
        self.output_file = Path(output_file)
        self.governance_data = None
        self.codeql_data = []
        self.semgrep_data = None
    
    def load_governance_report(self):
        """Load language governance report"""
        report_path = self.results_dir / 'language-governance-report' / 'governance-report.json'
        if report_path.exists():
            with open(report_path, encoding='utf-8') as f:
                self.governance_data = json.load(f)
                print(f"✓ Loaded governance report: {len(self.governance_data.get('violations', []))} violations")
        else:
            print("⚠ Governance report not found")
    
    def load_codeql_results(self):
        """Load CodeQL SARIF results"""
        codeql_dirs = [d for d in self.results_dir.glob('codeql-results-*')]
        for codeql_dir in codeql_dirs:
            sarif_files = list(codeql_dir.glob('*.sarif'))
            for sarif_file in sarif_files:
                try:
                    with open(sarif_file, encoding='utf-8') as f:
                        data = json.load(f)
                        self.codeql_data.append({
                            'language': codeql_dir.name.replace('codeql-results-', ''),
                            'data': data
                        })
                        print(f"✓ Loaded CodeQL results for {codeql_dir.name}")
                except Exception as e:
                    print(f"⚠ Error loading {sarif_file}: {e}")
    
    def load_semgrep_results(self):
        """Load Semgrep SARIF results"""
        semgrep_path = self.results_dir / 'semgrep-results' / 'semgrep.sarif'
        if semgrep_path.exists():
            with open(semgrep_path, encoding='utf-8') as f:
                self.semgrep_data = json.load(f)
                print("✓ Loaded Semgrep results")
        else:
            print("⚠ Semgrep results not found")
    
    def generate_report(self):
        """Generate consolidated markdown report"""
        lines = []
        
        # Header
        lines.append("# 🏝️ Unmanned Island Consolidated Security Report")
        lines.append("")
        lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        
        total_issues = 0
        critical_issues = 0
        
        if self.governance_data:
            gov_violations = len(self.governance_data.get('violations', []))
            gov_critical = sum(1 for v in self.governance_data.get('violations', [])
                             if v.get('severity') == 'CRITICAL')
            total_issues += gov_violations
            critical_issues += gov_critical
            lines.append(f"- **Language Governance:** {gov_violations} violations ({gov_critical} critical)")
        
        if self.codeql_data:
            lines.append(f"- **CodeQL:** {len(self.codeql_data)} language(s) analyzed")
        
        if self.semgrep_data:
            lines.append("- **Semgrep:** Analysis completed")
        
        lines.append("")
        lines.append(f"**Total Issues:** {total_issues}")
        lines.append(f"**Critical Issues:** {critical_issues}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Language Governance Details
        if self.governance_data:
            lines.append("## 1. Language Stack Governance")
            lines.append("")
            lines.append(f"**Files Scanned:** {self.governance_data.get('total_files', 0)}")
            lines.append(f"**Violations:** {len(self.governance_data.get('violations', []))}")
            lines.append("")
            
            violations = self.governance_data.get('violations', [])
            if violations:
                by_severity = defaultdict(list)
                for v in violations:
                    by_severity[v.get('severity', 'UNKNOWN')].append(v)
                
                for severity in ['CRITICAL', 'ERROR', 'WARNING']:
                    if severity in by_severity:
                        lines.append(f"### {severity} Issues ({len(by_severity[severity])})")
                        lines.append("")
                        for v in by_severity[severity][:10]:  # Top 10
                            lines.append(f"- **{v['message']}**")
                            lines.append(f"  - File: `{v['file']}`")
                            if 'language' in v:
                                lines.append(f"  - Language: {v['language']}")
                            if 'directory' in v:
                                lines.append(f"  - Directory: {v['directory']}")
                            lines.append("")
                        
                        if len(by_severity[severity]) > 10:
                            lines.append(f"*... and {len(by_severity[severity]) - 10} more*")
                            lines.append("")
            
            lines.append("---")
            lines.append("")
        
        # CodeQL Details
        if self.codeql_data:
            lines.append("## 2. CodeQL Analysis")
            lines.append("")
            lines.append("Multi-language security analysis using GitHub's CodeQL engine.")
            lines.append("")
            
            for codeql in self.codeql_data:
                lang = codeql['language']
                lines.append(f"### {lang.title()}")
                lines.append("")
                
                # Extract results from SARIF
                try:
                    runs = codeql['data'].get('runs', [])
                    if runs:
                        results = runs[0].get('results', [])
                        lines.append(f"- **Findings:** {len(results)}")
                        
                        if results:
                            lines.append("- **Sample Issues:**")
                            for result in results[:5]:  # Top 5
                                rule_id = result.get('ruleId', 'Unknown')
                                message = result.get('message', {}).get('text', 'No description')
                                lines.append(f"  - `{rule_id}`: {message}")
                            lines.append("")
                except Exception as e:
                    lines.append(f"- Error processing results: {e}")
                    lines.append("")
            
            lines.append("📊 View detailed results in the Security tab")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Semgrep Details
        if self.semgrep_data:
            lines.append("## 3. Semgrep Analysis")
            lines.append("")
            lines.append("Fast syntax and security pattern matching.")
            lines.append("")
            
            try:
                runs = self.semgrep_data.get('runs', [])
                if runs:
                    results = runs[0].get('results', [])
                    lines.append(f"**Findings:** {len(results)}")
                    lines.append("")
                    
                    if results:
                        lines.append("**Sample Issues:**")
                        for result in results[:10]:  # Top 10
                            rule_id = result.get('ruleId', 'Unknown')
                            message = result.get('message', {}).get('text', 'No description')
                            lines.append(f"- `{rule_id}`: {message}")
                        lines.append("")
            except Exception as e:
                lines.append(f"Error processing results: {e}")
                lines.append("")
            
            lines.append("📊 View detailed results in the Security tab")
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        
        if critical_issues > 0:
            lines.append("### 🔴 Critical Priority")
            lines.append("")
            lines.append("1. Address all CRITICAL violations immediately")
            lines.append("2. Review security findings from CodeQL and Semgrep")
            lines.append("3. Consult the [Language Stack Policy](docs/architecture/language-stack.md)")
            lines.append("")
        
        if total_issues > 0:
            lines.append("### ⚠️ High Priority")
            lines.append("")
            lines.append("1. Fix ERROR-level language governance violations")
            lines.append("2. Review and remediate security vulnerabilities")
            lines.append("3. Request exceptions if necessary through the [governance process](docs/architecture/language-governance.md)")
            lines.append("")
        else:
            lines.append("### ✅ All Clear")
            lines.append("")
            lines.append("No issues detected. System is compliant with all policies.")
            lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append("## Resources")
        lines.append("")
        lines.append("- [Language Stack Documentation](docs/architecture/language-stack.md)")
        lines.append("- [Language Governance Policy](docs/architecture/language-governance.md)")
        lines.append("- [Language Policy Configuration](config/language-policy.yaml)")
        lines.append("")
        lines.append("*Report generated by Unmanned Island CI/CD System*")
        
        return '\n'.join(lines)
    
    def save_report(self, content: str):
        """Save report to file"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ Consolidated report saved to {self.output_file}")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='Generate consolidated security and governance report'
    )
    parser.add_argument(
        '--results-dir',
        required=True,
        help='Directory containing analysis results'
    )
    parser.add_argument(
        '--output',
        default='consolidated-security-report.md',
        help='Output file path'
    )
    
    args = parser.parse_args()
    
    print("🔍 Generating Consolidated Security Report...\n")
    
    # Create generator
    generator = ConsolidatedReportGenerator(args.results_dir, args.output)
    
    # Load all results
    generator.load_governance_report()
    generator.load_codeql_results()
    generator.load_semgrep_results()
    
    # Generate report
    content = generator.generate_report()
    
    # Save report
    generator.save_report(content)
    
    print("\n✅ Report generation complete!")

if __name__ == '__main__':
    main()
