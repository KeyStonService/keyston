#!/usr/bin/env python3

"""
AI Auto-Fix Tool
AI 自動修復工具
-----------------------
Purpose:
  - Analyze Language Governance, CodeQL, and Semgrep reports
  - Use AI (GPT-4) to generate code fixes
  - Create git patches and file changes
  - Generate PR description with explanations

使用方法:
  python tools/ai-auto-fix.py \
    --artifacts-dir analysis-artifacts/ \
    --repo-root . \
    --branch-name ai-auto-fix-20250106 \
    --output-dir auto-fix-patches/
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

from guardrails_client import chat_completion, client_available, get_api_key

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------

AI_FIX_SYSTEM_PROMPT = """
You are an expert software engineer specializing in automated code remediation.

Your task is to generate precise code fixes for:
1. Language policy violations (e.g., wrong language in wrong directory)
2. Security vulnerabilities (from CodeQL and Semgrep)
3. Code quality issues

For each violation, provide:
- Exact file path
- Current problematic code
- Fixed code
- Explanation of the fix

Output format should be structured JSON with clear before/after code blocks.
Focus on minimal, surgical changes that fix the issue without breaking functionality.
"""

# ---------------------------------------------------------------------
# Artifact Loaders
# ---------------------------------------------------------------------

class ArtifactLoader:
    """Load and parse all analysis artifacts"""
    
    def __init__(self, artifacts_dir: str):
        self.artifacts_dir = Path(artifacts_dir)
        self.governance_data = None
        self.semgrep_data = None
        self.codeql_data = []
        self.ai_suggestions = None
    
    def load_all(self):
        """Load all available artifacts"""
        print("📥 Loading analysis artifacts...")
        
        # Load governance report
        gov_report = self.artifacts_dir / 'language-governance-report' / 'governance-report.json'
        if gov_report.exists():
            with open(gov_report, encoding='utf-8') as f:
                self.governance_data = json.load(f)
            print(f"✓ Loaded governance report: {len(self.governance_data.get('violations', []))} violations")
        
        # Load Semgrep report
        semgrep_report = self.artifacts_dir / 'semgrep-results' / 'semgrep.sarif'
        if semgrep_report.exists():
            with open(semgrep_report, encoding='utf-8') as f:
                self.semgrep_data = json.load(f)
            print("✓ Loaded Semgrep report")
        
        # Load CodeQL reports
        for codeql_dir in self.artifacts_dir.glob('codeql-results-*'):
            for sarif_file in codeql_dir.glob('*.sarif'):
                with open(sarif_file, encoding='utf-8') as f:
                    data = json.load(f)
                    self.codeql_data.append({
                        'language': codeql_dir.name.replace('codeql-results-', ''),
                        'data': data
                    })
        if self.codeql_data:
            print(f"✓ Loaded {len(self.codeql_data)} CodeQL report(s)")
        
        # Load AI suggestions
        ai_suggestions_file = self.artifacts_dir / 'consolidated-security-report' / 'ai-refactor-suggestions.md'
        if ai_suggestions_file.exists():
            with open(ai_suggestions_file, encoding='utf-8') as f:
                self.ai_suggestions = f.read()
            print("✓ Loaded AI suggestions")
    
    def get_fixable_issues(self) -> list[dict]:
        """Extract fixable issues from all reports"""
        issues = []
        
        # Governance violations
        if self.governance_data:
            for violation in self.governance_data.get('violations', []):
                if violation.get('severity') in ['CRITICAL', 'ERROR']:
                    issues.append({
                        'type': 'governance',
                        'severity': violation.get('severity'),
                        'file': violation.get('file'),
                        'language': violation.get('language'),
                        'message': violation.get('message'),
                        'directory': violation.get('directory')
                    })
        
        # Semgrep findings
        if self.semgrep_data:
            runs = self.semgrep_data.get('runs', [])
            if runs:
                for result in runs[0].get('results', []):
                    location = result.get('locations', [{}])[0]
                    physical_location = location.get('physicalLocation', {})
                    artifact_location = physical_location.get('artifactLocation', {})
                    
                    issues.append({
                        'type': 'semgrep',
                        'severity': 'ERROR',
                        'file': artifact_location.get('uri', ''),
                        'rule_id': result.get('ruleId', ''),
                        'message': result.get('message', {}).get('text', ''),
                        'region': physical_location.get('region', {})
                    })
        
        # CodeQL findings
        for codeql in self.codeql_data:
            runs = codeql.get('data', {}).get('runs', [])
            if runs:
                for result in runs[0].get('results', []):
                    location = result.get('locations', [{}])[0]
                    physical_location = location.get('physicalLocation', {})
                    artifact_location = physical_location.get('artifactLocation', {})
                    
                    issues.append({
                        'type': 'codeql',
                        'severity': 'ERROR',
                        'language': codeql.get('language'),
                        'file': artifact_location.get('uri', ''),
                        'rule_id': result.get('ruleId', ''),
                        'message': result.get('message', {}).get('text', ''),
                        'region': physical_location.get('region', {})
                    })
        
        return issues


# ---------------------------------------------------------------------
# AI Fix Generator
# ---------------------------------------------------------------------

class AIFixGenerator:
    """Generate code fixes using AI"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or get_api_key()
        self.available = client_available(self.api_key)
        if self.available:
            print("✓ Guardrails/OpenAI client configured")
        else:
            print("⚠️  AI client not available. Fixes will be limited to rule-based suggestions.")
    
    def generate_fixes(self, issues: list[dict], repo_root: str) -> list[dict]:
        """Generate fixes for the given issues"""
        fixes = []
        
        # Group issues by type for better AI context
        by_type = {}
        for issue in issues:
            itype = issue.get('type', 'unknown')
            if itype not in by_type:
                by_type[itype] = []
            by_type[itype].append(issue)
        
        # Generate fixes for governance issues (these are often file movements)
        if 'governance' in by_type:
            fixes.extend(self._generate_governance_fixes(by_type['governance'], repo_root))
        
        # Generate fixes for security issues (code changes)
        if 'semgrep' in by_type or 'codeql' in by_type:
            security_issues = by_type.get('semgrep', []) + by_type.get('codeql', [])
            if self.available:
                fixes.extend(self._generate_ai_fixes(security_issues, repo_root))
            else:
                fixes.extend(self._generate_rule_based_fixes(security_issues, repo_root))
        
        return fixes
    
    def _generate_governance_fixes(self, issues: list[dict], repo_root: str) -> list[dict]:
        """Generate fixes for governance violations"""
        fixes = []
        
        for issue in issues[:10]:  # Limit to first 10
            file_path = issue.get('file', '')
            if not file_path:
                continue
            
            # For now, suggest file removal or documentation of exception
            fixes.append({
                'type': 'governance',
                'file': file_path,
                'action': 'document',
                'suggestion': f"Add exception request or remove {file_path}",
                'severity': issue.get('severity'),
                'automated': False
            })
        
        return fixes
    
    def _generate_ai_fixes(self, issues: list[dict], repo_root: str) -> list[dict]:
        """Generate AI-powered fixes for security issues"""
        fixes = []
        
        # Take top 5 issues to avoid token limits
        for issue in issues[:5]:
            file_path = issue.get('file', '')
            if not file_path:
                continue
            
            full_path = Path(repo_root) / file_path
            if not full_path.exists():
                continue
            
            try:
                with open(full_path, encoding='utf-8') as f:
                    file_content = f.read()
                
                # Prepare context for AI
                context = f"""
File: {file_path}
Issue Type: {issue.get('type')}
Rule: {issue.get('rule_id', 'N/A')}
Message: {issue.get('message', '')}

Current File Content:
```
{file_content[:2000]}  # Limit to first 2000 chars
```

Please provide a fix for this issue. Output as JSON with:
- explanation: Brief explanation of the fix
- fixed_code: The corrected code (full file or relevant section)
"""
                
                # Call AI client via guardrails_client wrapper
                response = chat_completion(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": AI_FIX_SYSTEM_PROMPT},
                        {"role": "user", "content": context}
                    ],
                    temperature=0.3,
                    max_tokens=1500,
                    api_key=self.api_key,
                )
                
                ai_response = response.choices[0].message.content
                
                # Parse AI response
                fixes.append({
                    'type': 'security',
                    'file': file_path,
                    'action': 'modify',
                    'ai_suggestion': ai_response,
                    'severity': issue.get('severity'),
                    'automated': True
                })
                
            except Exception as e:
                print(f"⚠️  Error generating fix for {file_path}: {e}")
        
        return fixes
    
    def _generate_rule_based_fixes(self, issues: list[dict], repo_root: str) -> list[dict]:
        """Generate rule-based fixes when AI is not available"""
        fixes = []
        
        for issue in issues[:10]:  # Limit to first 10
            file_path = issue.get('file', '')
            if not file_path:
                continue
            
            fixes.append({
                'type': 'security',
                'file': file_path,
                'action': 'review',
                'suggestion': f"Manual review required: {issue.get('message', '')}",
                'severity': issue.get('severity'),
                'automated': False
            })
        
        return fixes


# ---------------------------------------------------------------------
# Patch Generator
# ---------------------------------------------------------------------

class PatchGenerator:
    """Generate git patches and file changes"""
    
    def __init__(self, output_dir: str):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_patches(self, fixes: list[dict]) -> bool:
        """Generate patch files from fixes"""
        if not fixes:
            print("⚠️  No fixes to generate")
            return False
        
        print(f"\n🔧 Generating patches for {len(fixes)} fix(es)...")
        
        # Generate PR description
        self._generate_pr_description(fixes)
        
        # Generate individual patches
        patch_count = 0
        for i, fix in enumerate(fixes):
            if fix.get('automated') and fix.get('ai_suggestion'):
                self._create_patch_file(i, fix)
                patch_count += 1
        
        print(f"✅ Generated {patch_count} patch file(s)")
        return patch_count > 0
    
    def _generate_pr_description(self, fixes: list[dict]):
        """Generate PR description"""
        lines = []
        
        lines.append("# 🤖 AI Auto-Fix: Address Governance and Security Violations")
        lines.append("")
        lines.append("## Overview")
        lines.append("")
        lines.append("This PR was automatically generated by the AI Auto-Fix Bot to address violations")
        lines.append("detected by the Language Governance, CodeQL, and Semgrep workflows.")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        
        by_type = {}
        for fix in fixes:
            ftype = fix.get('type', 'unknown')
            if ftype not in by_type:
                by_type[ftype] = []
            by_type[ftype].append(fix)
        
        lines.append(f"- **Total Fixes:** {len(fixes)}")
        for ftype, flist in by_type.items():
            lines.append(f"- **{ftype.title()} Fixes:** {len(flist)}")
        lines.append("")
        
        lines.append("## Changes")
        lines.append("")
        
        for i, fix in enumerate(fixes, 1):
            lines.append(f"### {i}. {fix.get('file', 'Unknown')}")
            lines.append("")
            lines.append(f"- **Type:** {fix.get('type', 'unknown').title()}")
            lines.append(f"- **Action:** {fix.get('action', 'unknown').title()}")
            lines.append(f"- **Severity:** {fix.get('severity', 'UNKNOWN')}")
            if fix.get('suggestion'):
                lines.append(f"- **Suggestion:** {fix['suggestion']}")
            lines.append("")
        
        lines.append("## Testing")
        lines.append("")
        lines.append("- [ ] Review all automated changes")
        lines.append("- [ ] Run linters and tests")
        lines.append("- [ ] Verify fixes address violations")
        lines.append("- [ ] Check for breaking changes")
        lines.append("")
        
        lines.append("## Notes")
        lines.append("")
        lines.append("This PR was generated automatically. Please review carefully before merging.")
        lines.append("")
        lines.append("---")
        lines.append(f"*Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*")
        
        # Write to file
        with open(self.output_dir / 'pr-description.md', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
    
    def _create_patch_file(self, index: int, fix: dict):
        """Create a patch file for a fix"""
        patch_file = self.output_dir / f"fix-{index:03d}.patch"
        
        # For now, create a placeholder patch
        # In a real implementation, this would parse the AI suggestion
        # and create a proper git diff format patch
        
        patch_content = f"""# Fix for {fix.get('file', 'unknown')}
# Type: {fix.get('type')}
# Severity: {fix.get('severity')}

AI Suggestion:
{fix.get('ai_suggestion', 'No suggestion available')}
"""
        
        with open(patch_file, 'w', encoding='utf-8') as f:
            f.write(patch_content)


# ---------------------------------------------------------------------
# Main Function
# ---------------------------------------------------------------------

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='AI Auto-Fix Tool - Generate code fixes automatically'
    )
    parser.add_argument(
        '--artifacts-dir',
        required=True,
        help='Directory containing analysis artifacts'
    )
    parser.add_argument(
        '--repo-root',
        default='.',
        help='Repository root directory'
    )
    parser.add_argument(
        '--branch-name',
        help='Branch name for fixes'
    )
    parser.add_argument(
        '--output-dir',
        default='auto-fix-patches',
        help='Output directory for patches'
    )
    
    args = parser.parse_args()
    
    print("🤖 AI Auto-Fix Tool")
    print("=" * 60)
    print("")
    
    # Load artifacts
    loader = ArtifactLoader(args.artifacts_dir)
    loader.load_all()
    
    # Get fixable issues
    print("\n🔍 Analyzing issues...")
    issues = loader.get_fixable_issues()
    print(f"Found {len(issues)} issue(s)")
    
    if not issues:
        print("✅ No fixable issues found")
        return 0
    
    # Generate fixes
    print("\n🤖 Generating fixes...")
    generator = AIFixGenerator()
    fixes = generator.generate_fixes(issues, args.repo_root)
    
    if not fixes:
        print("⚠️  No fixes generated")
        return 1
    
    print(f"Generated {len(fixes)} fix(es)")
    
    # Generate patches
    patch_gen = PatchGenerator(args.output_dir)
    success = patch_gen.generate_patches(fixes)
    
    if success:
        print(f"\n✅ Patches generated in {args.output_dir}")
        return 0
    else:
        print("\n⚠️  No patches generated")
        return 1


if __name__ == '__main__':
    sys.exit(main())
