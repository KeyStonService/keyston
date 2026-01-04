#!/usr/bin/env python3
"""
hash_artifacts.py - Generate hash manifest for artifacts
"""

import os
import hashlib
import json
from pathlib import Path

def calculate_hashes(filepath):
    """Calculate multiple hashes for a file"""
    hashes = {}
    
    # SHA256
    sha256_hash = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256_hash.update(chunk)
    hashes["sha256"] = sha256_hash.hexdigest()
    
    # SHA512
    sha512_hash = hashlib.sha512()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha512_hash.update(chunk)
    hashes["sha512"] = sha512_hash.hexdigest()
    
    return hashes

def generate_hash_manifest():
    """Generate hash manifest for all artifacts"""
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    manifest = {
        "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip(),
        "files": {}
    }
    
    # Hash all source files
    for source_file in Path(".").rglob("*"):
        if source_file.is_file() and ".git" not in str(source_file):
            if source_file.suffix in ['.yaml', '.yml', '.py', '.sh', '.json', '.md']:
                rel_path = str(source_file)
                manifest["files"][rel_path] = calculate_hashes(source_file)
    
    # Write manifest
    manifest_file = dist_dir / "hash_manifest.json"
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"  📄 Hash manifest: {manifest_file}")
    print(f"  📊 Files hashed: {len(manifest['files'])}")
    
    return True

if __name__ == "__main__":
    print("🔐 Generating hash manifest...")
    success = generate_hash_manifest()
    if success:
        print("✅ Hash manifest complete")
        exit(0)
    else:
        print("❌ Hash manifest failed")
        exit(1)