#!/usr/bin/env python3
"""
evidence_collect.py - Generate evidence chain
"""

import os
import hashlib
import json
# import yaml
from pathlib import Path
from datetime import datetime

def calculate_file_hash(filepath, algorithm="sha256"):
    """Calculate hash of a file"""
    hash_func = hashlib.new(algorithm)
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def collect_evidence():
    """Collect evidence from the repository"""
    evidence_dir = Path("dist/evidence")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    
    evidence = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "git_commit": os.popen("git rev-parse HEAD").read().strip(),
        "git_branch": os.popen("git rev-parse --abbrev-ref HEAD").read().strip(),
        "artifacts": {}
    }
    
    # Collect YAML files
    for yaml_file in Path(".").rglob("*.yaml"):
        if ".git" in str(yaml_file) or "dist" in str(yaml_file):
            continue
            
        rel_path = str(yaml_file)
        evidence["artifacts"][rel_path] = {
            "sha256": calculate_file_hash(yaml_file),
            "size": yaml_file.stat().st_size,
            "type": "yaml"
        }
    
    # Collect scripts
    for script_file in Path(".").rglob("*.sh"):
        if ".git" in str(script_file) or "dist" in str(script_file):
            continue
            
        rel_path = str(script_file)
        evidence["artifacts"][rel_path] = {
            "sha256": calculate_file_hash(script_file),
            "size": script_file.stat().st_size,
            "type": "script"
        }
    
    # Write evidence file
    evidence_file = evidence_dir / "evidence.json"
    with open(evidence_file, 'w') as f:
        json.dump(evidence, f, indent=2)
    
    print(f"  📄 Evidence collected: {evidence_file}")
    print(f"  📊 Total artifacts: {len(evidence['artifacts'])}")
    
    return True

if __name__ == "__main__":
    print("🔍 Collecting evidence...")
    success = collect_evidence()
    if success:
        print("✅ Evidence collection complete")
        exit(0)
    else:
        print("❌ Evidence collection failed")
        exit(1)