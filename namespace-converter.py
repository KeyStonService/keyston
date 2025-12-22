#!/usr/bin/env python3
"""
MachineNativeOps Namespace Converter
機器原生運維命名空間轉換器

Converts legacy AXIOM namespace references to MachineNativeOps standards:
- axiom.io → machinenativeops.io
- axiom-system → machinenativeops
- urn:axiom: → urn:machinenativeops:
- AxiomGlobalBaseline → MachineNativeOpsGlobalBaseline
"""

import re
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import json

class NamespaceConverter:
    def __init__(self, dry_run=False, verbose=False):
        self.dry_run = dry_run
        self.verbose = verbose
        self.conversion_rules = {
            # Domain conversions
            r'axiom\.io/v2': 'machinenativeops.io/v2',
            r'axiom\.io/v1': 'machinenativeops.io/v1',
            r'axiom\.io/': 'machinenativeops.io/',
            r'axiom\.io': 'machinenativeops.io',
            
            # Resource type conversions
            r'AxiomGlobalBaseline': 'MachineNativeOpsGlobalBaseline',
            r'AxiomAgent': 'MachineNativeOpsAgent',
            r'AxiomService': 'MachineNativeOpsService',
            
            # URN conversions
            r'urn:axiom:': 'urn:machinenativeops:',
            
            # Namespace conversions
            r'axiom-system': 'machinenativeops',
            r'namespace:\s*axiom': 'namespace: machinenativeops',
            
            # Prefix conversions (for labels, etc.)
            r'axiom-': 'machinenativeops-',
            
            # Registry conversions
            r'registry\.axiom\.io': 'registry.machinenativeops.io',
            
            # Path conversions
            r'etc/axiom/': 'etc/machinenativeops/',
            r'/axiom/': '/machinenativeops/',
        }
        
        self.stats = {
            'files_checked': 0,
            'files_converted': 0,
            'total_conversions': 0,
            'conversions_by_rule': {},
        }
    
    def convert_file(self, file_path: Path) -> int:
        """Convert a single file and return the number of conversions made."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            converted_content = content
            file_conversions = 0
            
            for pattern, replacement in self.conversion_rules.items():
                matches = re.findall(pattern, converted_content)
                if matches:
                    match_count = len(matches)
                    file_conversions += match_count
                    converted_content = re.sub(pattern, replacement, converted_content)
                    
                    # Track conversions by rule
                    if pattern not in self.stats['conversions_by_rule']:
                        self.stats['conversions_by_rule'][pattern] = 0
                    self.stats['conversions_by_rule'][pattern] += match_count
            
            self.stats['files_checked'] += 1
            
            if file_conversions > 0:
                self.stats['files_converted'] += 1
                self.stats['total_conversions'] += file_conversions
                
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(converted_content)
                    if self.verbose:
                        print(f"✅ Updated {file_path}: {file_conversions} conversion(s)")
                else:
                    print(f"🔍 Would update {file_path}: {file_conversions} conversion(s)")
            elif self.verbose:
                print(f"⏭️  No changes needed: {file_path}")
            
            return file_conversions
            
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            return 0
    
    def convert_directory(self, directory: Path, extensions: List[str] = None) -> Dict:
        """Convert all eligible files in a directory."""
        if extensions is None:
            extensions = ['.yaml', '.yml', '.json', '.py', '.md', '.sh', '.txt']
        
        print(f"🔄 Converting namespace in: {directory}")
        print(f"📄 Target extensions: {', '.join(extensions)}\n")
        
        for file_path in directory.rglob('*'):
            if file_path.is_file() and file_path.suffix in extensions:
                # Skip certain directories
                skip_dirs = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.venv', 'venv'}
                if any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                    continue
                
                self.convert_file(file_path)
        
        return self.stats
    
    def generate_report(self) -> str:
        """Generate a conversion report."""
        report = f"""
╔══════════════════════════════════════════════════════════════╗
║     MachineNativeOps Namespace Conversion Report            ║
╚══════════════════════════════════════════════════════════════╝

📊 Conversion Summary:
  Files checked:        {self.stats['files_checked']}
  Files converted:      {self.stats['files_converted']}
  Total conversions:    {self.stats['total_conversions']}
  Mode:                 {'DRY RUN (no changes made)' if self.dry_run else 'LIVE (changes applied)'}

"""
        
        if self.stats['conversions_by_rule']:
            report += "🔧 Conversions by Rule:\n"
            for pattern, count in sorted(
                self.stats['conversions_by_rule'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                report += f"  {pattern[:40]:40} → {count:4} conversion(s)\n"
        else:
            report += "✅ No conversions needed - all files already compliant!\n"
        
        report += "\n"
        
        if self.dry_run and self.stats['total_conversions'] > 0:
            report += "⚠️  This was a DRY RUN. Run without --dry-run to apply changes.\n"
        elif self.stats['total_conversions'] > 0:
            report += "✅ All conversions have been applied successfully!\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(
        description='Convert AXIOM namespace to MachineNativeOps namespace',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run (preview changes)
  python namespace-converter.py --dry-run .
  
  # Convert all files in current directory
  python namespace-converter.py .
  
  # Convert specific directory with verbose output
  python namespace-converter.py --verbose ./config
  
  # Convert single file
  python namespace-converter.py ./config/system-manifest.yaml
        """
    )
    
    parser.add_argument(
        'path',
        help='File or directory to convert'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without applying them'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show detailed output for all files'
    )
    parser.add_argument(
        '--report',
        help='Save conversion report to file'
    )
    
    args = parser.parse_args()
    
    path = Path(args.path).resolve()
    if not path.exists():
        print(f"❌ Path not found: {path}")
        sys.exit(1)
    
    converter = NamespaceConverter(dry_run=args.dry_run, verbose=args.verbose)
    
    if path.is_file():
        converter.convert_file(path)
    elif path.is_dir():
        converter.convert_directory(path)
    
    report = converter.generate_report()
    print(report)
    
    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"📄 Report saved to: {args.report}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
