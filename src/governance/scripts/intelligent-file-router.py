#!/usr/bin/env python3
"""
Intelligent File Router - Content-based Path Assignment System

Analyzes file contents and intelligently determines the correct governance
dimension directory based on actual content, keywords, structure, and semantics.
"""

import os
import sys
import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'


class IntelligentFileRouter:
    """AI-powered file content analyzer and intelligent path router."""
    
    def __init__(self, governance_dir: str = None):
        self.governance_dir = governance_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__))
        )
        self.dimension_patterns = self._load_dimension_patterns()
        
    def _load_dimension_patterns(self) -> Dict:
        """Load dimension detection patterns and keywords."""
        return {
            '00-vision-strategy': {
                'keywords': {
                    'high': ['vision', 'strategy', 'roadmap', 'objectives', 'strategic', 
                            'mission', 'instant', 'execution', 'transformation'],
                    'medium': ['goal', 'direction', 'future', 'plan', 'initiative', 'target']
                },
                'patterns': [
                    r'strategic\s+(?:plan|goal|objective)',
                    r'vision\s+(?:statement|document)',
                    r'instant\s+execution',
                    r'executive\s+summary'
                ],
                'structures': ['executive_summary', 'strategic_plan', 'vision_doc']
            },
            '01-architecture': {
                'keywords': {
                    'high': ['architecture', 'design', 'blueprint', 'pattern', 'structure',
                            'component', 'system', 'integration', 'dag', 'dependency'],
                    'medium': ['module', 'layer', 'interface', 'diagram', 'topology']
                },
                'patterns': [
                    r'architecture\s+(?:design|pattern|diagram)',
                    r'system\s+(?:architecture|design|blueprint)',
                    r'dag\s+(?:architecture|structure)',
                    r'dependency\s+(?:graph|architecture)'
                ],
                'structures': ['architecture_doc', 'design_doc', 'system_blueprint']
            },
            '02-decision': {
                'keywords': {
                    'high': ['decision', 'choice', 'alternative', 'evaluation', 'criteria'],
                    'medium': ['select', 'option', 'rationale', 'justification']
                },
                'patterns': [r'decision\s+(?:record|log|matrix)', r'adr\s*\d+']
            },
            '05-compliance': {
                'keywords': {
                    'high': ['compliance', 'regulation', 'gdpr', 'sox', 'hipaa', 'standard'],
                    'medium': ['regulatory', 'requirement', 'mandate', 'legal']
                },
                'patterns': [
                    r'(?:iso|nist|gdpr|sox|hipaa)[-\s]\d+',
                    r'compliance\s+(?:framework|requirement|standard)'
                ],
                'frameworks': ['ISO-42001', 'GDPR', 'SOC-2', 'HIPAA']
            },
            '06-security': {
                'keywords': {
                    'high': ['security', 'threat', 'vulnerability', 'attack', 'breach',
                            'encryption', 'authentication', 'authorization', 'control'],
                    'medium': ['protect', 'defense', 'secure', 'risk', 'exploit']
                },
                'patterns': [
                    r'security\s+(?:policy|control|measure|requirement)',
                    r'threat\s+(?:model|analysis|assessment)',
                    r'(?:iso-27001|nist-csf|cis-controls)'
                ],
                'frameworks': ['ISO-27001', 'NIST-CSF', 'CIS-Controls']
            },
            '07-audit': {
                'keywords': {
                    'high': ['audit', 'auditing', 'log', 'trail', 'record', 'trace'],
                    'medium': ['review', 'inspection', 'examination', 'verification']
                },
                'patterns': [r'audit\s+(?:log|trail|report|finding)'],
                'frameworks': ['ISO-19011', 'SOC-2']
            },
            '10-policy': {
                'keywords': {
                    'high': ['policy', 'rule', 'regulation', 'guideline', 'procedure'],
                    'medium': ['governance', 'standard', 'protocol', 'directive']
                },
                'patterns': [r'policy\s+(?:document|definition|statement)']
            },
            '13-metrics-reporting': {
                'keywords': {
                    'high': ['metric', 'kpi', 'measurement', 'dashboard', 'analytics',
                            'report', 'reporting', 'indicator', 'performance'],
                    'medium': ['measure', 'tracking', 'monitoring', 'telemetry']
                },
                'patterns': [
                    r'(?:kpi|metric|measurement)\s+(?:dashboard|report)',
                    r'performance\s+(?:metric|indicator|report)'
                ]
            },
            '23-policies': {
                'keywords': {
                    'high': ['policy', 'policies', 'rego', 'opa', 'conftest'],
                    'medium': ['rule', 'constraint', 'gate', 'validation']
                },
                'patterns': [r'policy\.(?:yaml|rego)', r'conftest\s+policy']
            },
            '29-docs': {
                'keywords': {
                    'high': ['documentation', 'guide', 'tutorial', 'manual', 'readme',
                            'how-to', 'quickstart', 'getting-started'],
                    'medium': ['instruction', 'help', 'reference', 'example']
                },
                'patterns': [
                    r'readme(?:\.md)?',
                    r'(?:user|admin|developer)\s+guide',
                    r'getting\s+started'
                ]
            },
            '34-config': {
                'keywords': {
                    'high': ['config', 'configuration', 'settings', 'parameters', 'env'],
                    'medium': ['setup', 'preference', 'option', 'property']
                },
                'patterns': [
                    r'config\.(?:yaml|json|toml)',
                    r'\.env(?:\.example)?',
                    r'settings\.(?:yaml|json)'
                ]
            },
            '37-behavior-contracts': {
                'keywords': {
                    'high': ['behavior', 'contract', 'agreement', 'covenant', 'sla'],
                    'medium': ['expectation', 'guarantee', 'promise', 'commitment']
                },
                'patterns': [r'(?:behavior|behavioral)\s+contract', r'sla\s+definition']
            },
            '39-automation': {
                'keywords': {
                    'high': ['automation', 'ci', 'cd', 'pipeline', 'workflow', 'github-actions',
                            'jenkins', 'gitlab-ci', 'circleci'],
                    'medium': ['build', 'deploy', 'release', 'continuous']
                },
                'patterns': [
                    r'\.github/workflows/',
                    r'(?:ci|cd)\s+(?:pipeline|workflow)',
                    r'github\s+actions'
                ]
            },
            '60-contracts': {
                'keywords': {
                    'high': ['contract', 'sla', 'agreement', 'service-level'],
                    'medium': ['guarantee', 'commitment', 'promise', 'obligation']
                },
                'patterns': [r'sla\s+(?:contract|agreement|definition)']
            }
        }
    
    def analyze_content(self, filepath: str) -> Dict[str, float]:
        """
        Analyze file content and calculate confidence scores for each dimension.
        
        Returns: Dict mapping dimension_id -> confidence_score (0-100)
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read().lower()
        except (OSError, UnicodeDecodeError, PermissionError) as e:
            print(f"{RED}Error reading {filepath}: {e}{RESET}")
            return {}
        
        scores = {}
        total_words = len(content.split())
        
        if total_words == 0:
            return scores
        
        for dimension_id, patterns in self.dimension_patterns.items():
            score = 0.0
            
            # Keyword density scoring
            high_keywords = patterns['keywords']['high']
            medium_keywords = patterns['keywords']['medium']
            
            for keyword in high_keywords:
                count = len(re.findall(r'\b' + keyword + r'\b', content))
                score += count * 10  # High weight
            
            for keyword in medium_keywords:
                count = len(re.findall(r'\b' + keyword + r'\b', content))
                score += count * 5  # Medium weight
            
            # Pattern matching
            for pattern in patterns.get('patterns', []):
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches * 15  # Pattern match bonus
            
            # Framework detection
            if 'frameworks' in patterns:
                for framework in patterns['frameworks']:
                    if framework.lower() in content:
                        score += 20  # Framework detection bonus
            
            # Normalize score to 0-100 range
            normalized_score = min(100, (score / total_words) * 1000)
            scores[dimension_id] = normalized_score
        
        return scores
    
    def classify_file(self, filepath: str) -> Tuple[Optional[str], float, List[Tuple[str, float]]]:
        """
        Classify file and return best dimension match with confidence.
        
        Returns: (best_dimension, confidence, all_ranked_matches)
        """
        scores = self.analyze_content(filepath)
        
        if not scores:
            return None, 0.0, []
        
        # Sort by score descending
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        if ranked[0][1] == 0:
            return None, 0.0, []
        
        best_dimension = ranked[0][0]
        confidence = ranked[0][1]
        
        return best_dimension, confidence, ranked[:5]  # Top 5 matches
    
    def get_current_dimension(self, filepath: str) -> Optional[str]:
        """Extract current dimension from file path."""
        rel_path = os.path.relpath(filepath, self.governance_dir)
        parts = rel_path.split(os.sep)
        
        # Check if in a numbered dimension directory
        for part in parts:
            if re.match(r'^\d{2}-[a-z-]+$', part):
                return part
        
        return None
    
    def detect_misplacements(self, verbose: bool = False) -> List[Dict]:
        """
        Scan all governance files and detect misplaced ones.
        
        Returns: List of misplacement reports
        """
        misplacements = []
        
        # Scan governance directory
        for root, dirs, files in os.walk(self.governance_dir):
            # Skip hidden directories and scripts
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'scripts']
            
            for filename in files:
                if not (filename.endswith('.md') or filename.endswith('.yaml') or 
                       filename.endswith('.yml')):
                    continue
                
                filepath = os.path.join(root, filename)
                current_dim = self.get_current_dimension(filepath)
                recommended_dim, confidence, all_matches = self.classify_file(filepath)
                
                if verbose:
                    print(f"\n{CYAN}Analyzing: {os.path.relpath(filepath, self.governance_dir)}{RESET}")
                    print(f"Current: {current_dim or 'root'}")
                    print(f"Recommended: {recommended_dim} (confidence: {confidence:.1f}%)")
                
                # Check for misplacement
                if recommended_dim and confidence >= 50:
                    if current_dim != recommended_dim:
                        # High confidence misplacement
                        if confidence >= 70:
                            misplacements.append({
                                'filepath': filepath,
                                'filename': filename,
                                'current': current_dim or 'root',
                                'recommended': recommended_dim,
                                'confidence': confidence,
                                'all_matches': all_matches,
                                'severity': 'HIGH' if confidence >= 90 else 'MEDIUM'
                            })
        
        return misplacements
    
    def suggest_moves(self, misplacements: List[Dict]) -> List[str]:
        """Generate move commands for misplaced files."""
        commands = []
        
        for item in sorted(misplacements, key=lambda x: x['confidence'], reverse=True):
            src = item['filepath']
            dst_dir = os.path.join(self.governance_dir, item['recommended'])
            dst = os.path.join(dst_dir, item['filename'])
            
            # Create directory if needed
            cmd = f"mkdir -p {dst_dir} && mv {src} {dst}"
            commands.append({
                'command': cmd,
                'file': item['filename'],
                'from': item['current'],
                'to': item['recommended'],
                'confidence': item['confidence'],
                'severity': item['severity']
            })
        
        return commands
    
    def print_report(self, misplacements: List[Dict]):
        """Print detailed misplacement report."""
        print(f"\n{BOLD}{BLUE}{'='*70}{RESET}")
        print(f"{BOLD}{BLUE}Intelligent File Router - Misplacement Report{RESET}")
        print(f"{BOLD}{BLUE}{'='*70}{RESET}\n")
        
        if not misplacements:
            print(f"{GREEN}✅ No misplacements detected! All files are correctly placed.{RESET}\n")
            return
        
        # Group by severity
        high_severity = [m for m in misplacements if m['severity'] == 'HIGH']
        medium_severity = [m for m in misplacements if m['severity'] == 'MEDIUM']
        
        print(f"{BOLD}Summary:{RESET}")
        print(f"  Total misplacements: {len(misplacements)}")
        print(f"  High confidence (≥90%): {RED}{len(high_severity)}{RESET}")
        print(f"  Medium confidence (70-89%): {YELLOW}{len(medium_severity)}{RESET}\n")
        
        # Print high severity first
        if high_severity:
            print(f"{BOLD}{RED}HIGH SEVERITY - Should be moved immediately:{RESET}\n")
            for item in high_severity:
                self._print_misplacement_item(item)
        
        if medium_severity:
            print(f"\n{BOLD}{YELLOW}MEDIUM SEVERITY - Recommended to move:{RESET}\n")
            for item in medium_severity:
                self._print_misplacement_item(item)
        
        print(f"\n{BOLD}{BLUE}{'='*70}{RESET}\n")
    
    def _print_misplacement_item(self, item: Dict):
        """Print single misplacement item."""
        severity_color = RED if item['severity'] == 'HIGH' else YELLOW
        
        print(f"{severity_color}●{RESET} {BOLD}{item['filename']}{RESET}")
        print(f"  Current location: {item['current']}")
        print(f"  {GREEN}Recommended:{RESET} {item['recommended']} "
              f"({severity_color}{item['confidence']:.1f}%{RESET} confidence)")
        
        # Show top 3 alternatives
        if len(item['all_matches']) > 1:
            print(f"  Alternatives:")
            for dim, score in item['all_matches'][1:4]:
                if score > 30:
                    print(f"    - {dim} ({score:.1f}%)")
        print()




def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Intelligent File Router - Analyze content and route to correct dimension'
    )
    parser.add_argument('--file', help='Analyze single file')
    parser.add_argument('--scan-all', action='store_true', help='Scan all governance files')
    parser.add_argument('--detect-misplacements', action='store_true',
                       help='Detect misplaced files')
    parser.add_argument('--suggest-moves', action='store_true',
                       help='Generate move commands for misplaced files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    router = IntelligentFileRouter()
    
    if args.file:
        # Analyze single file
        dim, conf, matches = router.classify_file(args.file)
        print(f"\n{BOLD}File:{RESET} {args.file}")
        print(f"{BOLD}Recommended dimension:{RESET} {GREEN}{dim}{RESET} "
              f"(confidence: {conf:.1f}%)\n")
        if matches:
            print(f"{BOLD}Top matches:{RESET}")
            for d, s in matches:
                print(f"  {d}: {s:.1f}%")
        print()
    
    elif args.scan_all or args.detect_misplacements:
        # Detect misplacements
        misplacements = router.detect_misplacements(verbose=args.verbose)
        router.print_report(misplacements)
        
        if args.suggest_moves and misplacements:
            print(f"{BOLD}{BLUE}Move Commands:{RESET}\n")
            commands = router.suggest_moves(misplacements)
            for cmd in commands:
                print(f"# {cmd['file']}: {cmd['from']} → {cmd['to']} "
                      f"({cmd['confidence']:.1f}%)")
                print(f"{cmd['command']}\n")
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
