#!/usr/bin/env python3

"""
AI Refactor Review Tool
AI 重構審查工具
-----------------------
Purpose:
  - Read Language Governance Report + Semgrep Report
  - Integrate all violations and risks
  - Call GPT / LLM to generate professional-grade refactoring suggestions
  - Output Markdown report for GitHub Actions PR comments and Issues

使用方法:
  python tools/ai-refactor-review.py \
    --governance-report governance-report.json \
    --semgrep-report semgrep-report.json \
    --codeql-reports codeql-results/ \
    --output ai-refactor-suggestions.md
"""

import argparse
import json
import os
from datetime import datetime
from pathlib import Path

from guardrails_client import chat_completion, client_available, get_api_key

# ---------------------------------------------------------------------
# File Loading Functions
# ---------------------------------------------------------------------

def load_text(path: str) -> str:
    """Load text file"""
    if not os.path.exists(path):
        return ""
    with open(path, encoding="utf-8") as f:
        return f.read()


def load_json(path: str) -> dict:
    """Load JSON file"""
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading {path}: {e}")
            return {}


# ---------------------------------------------------------------------
# AI System Prompt for Refactoring Suggestions
# ---------------------------------------------------------------------

AI_SYSTEM_PROMPT = """
You are an enterprise-grade software architect, language governance expert, and security analyst.

You must read:
1. Language Governance Report (language layer errors, language boundary violations, illegal languages)
2. Semgrep Security Report (security issues, dangerous patterns)
3. CodeQL Analysis Results (security vulnerabilities, code quality issues)

Provide high-quality, precise, actionable refactoring suggestions.

Your output should include:
- **Language Migration Strategy**: How to fix language violations
- **Security Remediation**: How to fix security vulnerabilities
- **Architecture Alignment**: How to align with the 5-layer language stack
- **Code Examples**: Concrete before/after examples when possible
- **Priority**: Order by severity (CRITICAL → ERROR → WARNING)

Format your response in Markdown with clear sections and actionable steps.
Be concise but thorough. Focus on practical solutions.
"""

# ---------------------------------------------------------------------
# Rule-Based Suggestion Generator (Fallback)
# ---------------------------------------------------------------------

class RuleBasedSuggestionGenerator:
    """Generate suggestions using rules when AI is not available"""
    
    def __init__(self):
        self.suggestions = []
    
    def generate_language_suggestions(self, violations: list[dict]) -> list[str]:
        """Generate language governance suggestions"""
        suggestions = []
        
        # Group by violation type
        by_type = {}
        for v in violations:
            vtype = v.get('type', 'UNKNOWN')
            if vtype not in by_type:
                by_type[vtype] = []
            by_type[vtype].append(v)
        
        # Language not allowed violations
        if 'LANGUAGE_NOT_ALLOWED' in by_type:
            violations_list = by_type['LANGUAGE_NOT_ALLOWED']
            suggestions.append({
                'title': 'Language Policy Violations',
                'severity': 'ERROR',
                'count': len(violations_list),
                'suggestion': self._generate_language_migration_advice(violations_list)
            })
        
        # Globally forbidden languages
        if 'GLOBALLY_FORBIDDEN' in by_type:
            violations_list = by_type['GLOBALLY_FORBIDDEN']
            suggestions.append({
                'title': 'Forbidden Languages Detected',
                'severity': 'CRITICAL',
                'count': len(violations_list),
                'suggestion': self._generate_removal_advice(violations_list)
            })
        
        return suggestions
    
    def _generate_language_migration_advice(self, violations: list[dict]) -> str:
        """Generate migration advice for language violations"""
        advice = []
        
        # Group by language
        by_lang = {}
        for v in violations:
            lang = v.get('language', 'Unknown')
            if lang not in by_lang:
                by_lang[lang] = []
            by_lang[lang].append(v)
        
        for lang, vlist in by_lang.items():
            directories = set(v.get('directory', '') for v in vlist)
            advice.append(f"**{lang} Files ({len(vlist)})**:")
            advice.append(f"- Found in: {', '.join(sorted(directories))}")
            advice.append("- **Action**: Migrate to allowed language or move to appropriate directory")
            
            # Specific suggestions based on language
            if lang == 'JavaScript':
                advice.append("- **Recommendation**: Convert to TypeScript for type safety")
                advice.append("- **Tool**: Use `tsc` compiler or automated migration tools")
            elif lang == 'Python':
                advice.append("- **Recommendation**: Ensure Python is allowed in this directory")
                advice.append("- **Check**: Review `config/language-policy.yaml` for directory rules")
            
            advice.append("")
        
        return '\n'.join(advice)
    
    def _generate_removal_advice(self, violations: list[dict]) -> str:
        """Generate advice for removing forbidden languages"""
        advice = []
        
        by_lang = {}
        for v in violations:
            lang = v.get('language', 'Unknown')
            if lang not in by_lang:
                by_lang[lang] = []
            by_lang[lang].append(v)
        
        for lang, vlist in by_lang.items():
            advice.append(f"**{lang} is Globally Forbidden ({len(vlist)} files)**:")
            advice.append(f"- **Critical Action**: Remove all {lang} files immediately")
            advice.append(f"- **Files**: {', '.join([v.get('file', '') for v in vlist[:5]])}")
            if len(vlist) > 5:
                advice.append(f"- ... and {len(vlist) - 5} more files")
            advice.append("")
        
        return '\n'.join(advice)
    
    def generate_security_suggestions(self, semgrep_data: dict, codeql_data: list[dict]) -> list[str]:
        """Generate security suggestions"""
        suggestions = []
        
        # Semgrep findings
        if semgrep_data:
            runs = semgrep_data.get('runs', [])
            if runs and runs[0].get('results'):
                results = runs[0]['results']
                suggestions.append({
                    'title': 'Semgrep Security Findings',
                    'severity': 'WARNING',
                    'count': len(results),
                    'suggestion': f"Review {len(results)} security findings from Semgrep. Focus on OWASP Top 10 vulnerabilities."
                })
        
        # CodeQL findings
        for codeql in codeql_data:
            lang = codeql.get('language', 'unknown')
            data = codeql.get('data', {})
            runs = data.get('runs', [])
            if runs and runs[0].get('results'):
                results = runs[0]['results']
                suggestions.append({
                    'title': f'CodeQL {lang.title()} Analysis',
                    'severity': 'WARNING',
                    'count': len(results),
                    'suggestion': f"Address {len(results)} findings from CodeQL analysis. These are high-confidence security issues."
                })
        
        return suggestions


# ---------------------------------------------------------------------
# AI-Powered Suggestion Generator
# ---------------------------------------------------------------------

class AISuggestionGenerator:
    """Generate suggestions using OpenAI GPT"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4"):
        self.api_key = api_key or get_api_key()
        self.model = model
        
        self.available = client_available(self.api_key)
        if not self.available:
            print("⚠️  AI suggestions not available. Set AI_INTEGRATIONS_OPENAI_API_KEY or OPENAI_API_KEY.")
    
    def generate_suggestions(self, context: str) -> str:
        """Generate AI-powered suggestions"""
        if not self.available:
            return "AI suggestions not available. Using rule-based fallback."
        
        try:
            response = chat_completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": AI_SYSTEM_PROMPT},
                    {"role": "user", "content": context}
                ],
                temperature=0.7,
                max_tokens=2000,
                api_key=self.api_key,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            print(f"⚠️  Error calling OpenAI API: {e}")
            return "AI suggestions failed. See rule-based suggestions below."


# ---------------------------------------------------------------------
# Main Report Generator
# ---------------------------------------------------------------------

class AIRefactorReviewer:
    """Main class for generating AI-powered refactor suggestions"""
    
    def __init__(self, args):
        self.args = args
        self.governance_data = None
        self.semgrep_data = None
        self.codeql_data = []
        
        # Initialize generators
        self.rule_generator = RuleBasedSuggestionGenerator()
        self.ai_generator = AISuggestionGenerator()
    
    def load_all_reports(self):
        """Load all input reports"""
        print("📥 Loading reports...")
        
        # Load governance report
        if self.args.governance_report and os.path.exists(self.args.governance_report):
            self.governance_data = load_json(self.args.governance_report)
            print(f"✓ Loaded governance report: {len(self.governance_data.get('violations', []))} violations")
        
        # Load Semgrep report
        if self.args.semgrep_report and os.path.exists(self.args.semgrep_report):
            self.semgrep_data = load_json(self.args.semgrep_report)
            print("✓ Loaded Semgrep report")
        
        # Load CodeQL reports
        if self.args.codeql_reports and os.path.exists(self.args.codeql_reports):
            codeql_path = Path(self.args.codeql_reports)
            for sarif_file in codeql_path.rglob('*.sarif'):
                data = load_json(str(sarif_file))
                if data:
                    self.codeql_data.append({
                        'language': sarif_file.stem,
                        'data': data
                    })
            print(f"✓ Loaded {len(self.codeql_data)} CodeQL report(s)")
    
    def generate_context_summary(self) -> str:
        """Generate summary of all findings for AI"""
        parts = []
        
        # Governance violations
        if self.governance_data:
            violations = self.governance_data.get('violations', [])
            if violations:
                parts.append(f"## Language Governance Violations ({len(violations)})\n")
                for v in violations[:20]:  # Top 20
                    parts.append(f"- {v.get('severity', 'UNKNOWN')}: {v.get('message', '')}")
                    parts.append(f"  File: {v.get('file', '')}")
                if len(violations) > 20:
                    parts.append(f"... and {len(violations) - 20} more violations")
                parts.append("")
        
        # Semgrep findings
        if self.semgrep_data:
            runs = self.semgrep_data.get('runs', [])
            if runs and runs[0].get('results'):
                results = runs[0]['results']
                parts.append(f"## Semgrep Security Findings ({len(results)})\n")
                for r in results[:10]:  # Top 10
                    rule_id = r.get('ruleId', 'Unknown')
                    message = r.get('message', {}).get('text', 'No description')
                    parts.append(f"- {rule_id}: {message}")
                if len(results) > 10:
                    parts.append(f"... and {len(results) - 10} more findings")
                parts.append("")
        
        # CodeQL findings
        for codeql in self.codeql_data:
            lang = codeql.get('language', 'unknown')
            data = codeql.get('data', {})
            runs = data.get('runs', [])
            if runs and runs[0].get('results'):
                results = runs[0]['results']
                parts.append(f"## CodeQL {lang.title()} ({len(results)})\n")
                for r in results[:5]:  # Top 5
                    rule_id = r.get('ruleId', 'Unknown')
                    message = r.get('message', {}).get('text', 'No description')
                    parts.append(f"- {rule_id}: {message}")
                parts.append("")
        
        return '\n'.join(parts)
    
    def generate_report(self) -> str:
        """Generate complete refactoring report"""
        lines = []
        
        # Header
        lines.append("# 🤖 AI-Powered Refactoring Suggestions")
        lines.append("")
        lines.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")
        
        total_issues = 0
        if self.governance_data:
            total_issues += len(self.governance_data.get('violations', []))
        if self.semgrep_data:
            runs = self.semgrep_data.get('runs', [])
            if runs:
                total_issues += len(runs[0].get('results', []))
        for codeql in self.codeql_data:
            runs = codeql.get('data', {}).get('runs', [])
            if runs:
                total_issues += len(runs[0].get('results', []))
        
        lines.append(f"**Total Issues Detected:** {total_issues}")
        lines.append("")
        lines.append("This report provides AI-powered and rule-based suggestions for addressing:")
        lines.append("- Language governance violations")
        lines.append("- Security vulnerabilities")
        lines.append("- Code quality issues")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Rule-based suggestions
        lines.append("## 📋 Rule-Based Suggestions")
        lines.append("")
        
        if self.governance_data:
            violations = self.governance_data.get('violations', [])
            if violations:
                suggestions = self.rule_generator.generate_language_suggestions(violations)
                for sugg in suggestions:
                    emoji = '🔴' if sugg['severity'] == 'CRITICAL' else '⚠️'
                    lines.append(f"### {emoji} {sugg['title']} ({sugg['count']} issues)")
                    lines.append("")
                    lines.append(sugg['suggestion'])
                    lines.append("")
                    lines.append("---")
                    lines.append("")
        
        # Security suggestions
        if self.semgrep_data or self.codeql_data:
            sec_suggestions = self.rule_generator.generate_security_suggestions(
                self.semgrep_data, self.codeql_data
            )
            for sugg in sec_suggestions:
                lines.append(f"### 🔒 {sugg['title']} ({sugg['count']} issues)")
                lines.append("")
                lines.append(sugg['suggestion'])
                lines.append("")
                lines.append("---")
                lines.append("")
        
        # AI-powered suggestions (if available)
        if self.ai_generator and self.ai_generator.available:
            lines.append("## 🤖 AI-Powered Suggestions")
            lines.append("")
            lines.append("*Generated using GPT-4 based on all detected issues*")
            lines.append("")
            
            context = self.generate_context_summary()
            ai_suggestions = self.ai_generator.generate_suggestions(context)
            lines.append(ai_suggestions)
            lines.append("")
            lines.append("---")
            lines.append("")
        
        # Action Plan
        lines.append("## 📝 Recommended Action Plan")
        lines.append("")
        lines.append("### Immediate Actions (Critical)")
        lines.append("")
        lines.append("1. Remove all globally forbidden languages")
        lines.append("2. Address CRITICAL security vulnerabilities")
        lines.append("3. Fix language boundary violations")
        lines.append("")
        lines.append("### Short-term (This Sprint)")
        lines.append("")
        lines.append("1. Migrate files to correct directories")
        lines.append("2. Convert JavaScript to TypeScript where needed")
        lines.append("3. Address ERROR-level governance violations")
        lines.append("4. Fix HIGH severity security issues")
        lines.append("")
        lines.append("### Long-term (Next Quarter)")
        lines.append("")
        lines.append("1. Establish comprehensive testing for all changes")
        lines.append("2. Implement automated language migration tools")
        lines.append("3. Review and update language policy as needed")
        lines.append("4. Conduct security training for team")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Resources
        lines.append("## 📚 Resources")
        lines.append("")
        lines.append("- [Language Stack Policy](docs/architecture/language-stack.md)")
        lines.append("- [Language Governance Guide](docs/architecture/language-governance.md)")
        lines.append("- [Exception Request Process](docs/architecture/language-governance.md#例外申請)")
        lines.append("- [Language Policy Configuration](config/language-policy.yaml)")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*Generated by Unmanned Island AI Refactor Review Tool*")
        
        return '\n'.join(lines)
    
    def save_report(self, content: str):
        """Save report to file"""
        with open(self.args.output, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"\n✅ AI refactor suggestions saved to {self.args.output}")


# ---------------------------------------------------------------------
# Main Function
# ---------------------------------------------------------------------

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='AI-Powered Refactor Review Tool'
    )
    parser.add_argument(
        '--governance-report',
        help='Path to governance report JSON'
    )
    parser.add_argument(
        '--semgrep-report',
        help='Path to Semgrep SARIF report'
    )
    parser.add_argument(
        '--codeql-reports',
        help='Directory containing CodeQL SARIF reports'
    )
    parser.add_argument(
        '--output',
        default='ai-refactor-suggestions.md',
        help='Output file path'
    )
    parser.add_argument(
        '--ai-model',
        default='gpt-4',
        help='OpenAI model to use (default: gpt-4)'
    )
    
    args = parser.parse_args()
    
    print("🤖 AI Refactor Review Tool")
    print("=" * 60)
    print("")
    
    # Create reviewer
    reviewer = AIRefactorReviewer(args)
    
    # Load all reports
    reviewer.load_all_reports()
    
    # Generate report
    print("\n📝 Generating refactoring suggestions...")
    report_content = reviewer.generate_report()
    
    # Save report
    reviewer.save_report(report_content)
    
    print("\n✅ Report generation complete!")
    print(f"📄 Output: {args.output}")


if __name__ == '__main__':
    main()
