#!/usr/bin/env python3
"""
vector_test.py - Run test vectors (valid/invalid cases)
"""

import os
import yaml
import json
from pathlib import Path

def run_test_vectors():
    """Run test vectors for validation"""
    passed = 0
    failed = 0
    
    test_dirs = [
        "test-vectors/valid",
        "test-vectors/invalid"
    ]
    
    for test_dir in test_dirs:
        test_path = Path(test_dir)
        if not test_path.exists():
            continue
            
        is_valid = "valid" in test_dir
        
        for test_file in test_path.glob("*.yaml"):
            try:
                with open(test_file, 'r') as f:
                    _ = yaml.safe_load(f)
                
                # Basic YAML validation
                if is_valid:
                    print(f"    ✅ Valid test passed: {test_file}")
                    passed += 1
                else:
                    msg = f"Invalid test should have failed: {test_file}"
                    print(f"    ❌ {msg}")
                    failed += 1
                    
            except Exception as e:
                if not is_valid:
                    print(f"    ✅ Invalid test correctly failed: {test_file}")
                    passed += 1
                else:
                    print(f"    ❌ Valid test failed: {test_file} - {e}")
                    failed += 1
    
    print(f"  📊 Test Results: {passed} passed, {failed} failed")
    return failed == 0

if __name__ == "__main__":
    print("🧪 Running test vectors...")
    success = run_test_vectors()
    if success:
        print("✅ Test vectors complete")
        exit(0)
    else:
        print("❌ Test vectors failed")
        exit(1)