#!/usr/bin/env python3
"""
build_merkle_root.py - Generate Merkle root hash lock
"""

import os
import hashlib
import json
from pathlib import Path

def calculate_file_hash(filepath):
    """Calculate SHA256 hash of a file"""
    hash_func = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def build_merkle_tree(hashes):
    """Build Merkle tree from list of hashes"""
    if len(hashes) == 1:
        return hashes[0]
    
    next_level = []
    for i in range(0, len(hashes), 2):
        if i + 1 < len(hashes):
            combined = hashes[i] + hashes[i + 1]
        else:
            combined = hashes[i] + hashes[i]  # Duplicate odd leaf
        
        combined_hash = hashlib.sha256(combined.encode()).hexdigest()
        next_level.append(combined_hash)
    
    return build_merkle_tree(next_level)

def generate_merkle_lock():
    """Generate Merkle root hash lock"""
    # Collect all file hashes
    file_hashes = []
    hash_map = {}
    
    for file_path in Path(".").rglob("*"):
        if file_path.is_file() and ".git" not in str(file_path) and "dist" not in str(file_path):
            if file_path.suffix in ['.yaml', '.yml', '.py', '.sh', '.json', '.md']:
                file_hash = calculate_file_hash(file_path)
                rel_path = str(file_path)
                file_hashes.append(file_hash)
                hash_map[rel_path] = file_hash
    
    # Build Merkle tree
    file_hashes.sort()  # Sort for deterministic results  # Sort for deterministic results
    merkle_root = build_merkle_tree(file_hashes)
    
    # Create lock file
    lock_data = {
        "merkle_root": merkle_root,
        "timestamp": os.popen("date -u +%Y-%m-%dT%H:%M:%SZ").read().strip(),
        "file_count": len(file_hashes),
        "git_commit": os.popen("git rev-parse HEAD").read().strip(),
        "files": hash_map
    }
    
    dist_dir = Path("dist")
    dist_dir.mkdir(exist_ok=True)
    
    lock_file = dist_dir / "merkle_lock.json"
    with open(lock_file, 'w') as f:
        json.dump(lock_data, f, indent=2)
    
    print(f"  🌳 Merkle root: {merkle_root}")
    print(f"  📄 Lock file: {lock_file}")
    print(f"  📊 Files included: {len(file_hashes)}")
    
    return True

if __name__ == "__main__":
    print("🔐 Building Merkle root hash lock...")
    success = generate_merkle_lock()
    if success:
        print("✅ Merkle lock generation complete")
        exit(0)
    else:
        print("❌ Merkle lock generation failed")
        exit(1)