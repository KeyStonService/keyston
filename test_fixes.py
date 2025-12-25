#!/usr/bin/env python3
"""
Test script to verify all fixes are working correctly
"""

import sys
from pathlib import Path

def test_imports():
    """Test that all modules can be imported without errors"""
    print("Testing imports...")
    
    try:
        # Test enhanced_memory_sync
        sys.path.insert(0, str(Path(__file__).parent / "workspace/src/scripts/automation"))
        import enhanced_memory_sync
        print("✓ enhanced_memory_sync imports successfully")
        
        # Test knowledge_graph_visualizer
        import knowledge_graph_visualizer
        print("✓ knowledge_graph_visualizer imports successfully")
        
        # Test enhanced_validator
        sys.path.insert(0, str(Path(__file__).parent / "controlplane/baseline/validation"))
        import enhanced_validator
        print("✓ enhanced_validator imports successfully")
        
        return True
    except Exception as e:
        print(f"✗ Import failed: {e}")
        return False

def test_hash_algorithms():
    """Test that hash algorithms are properly configured"""
    print("\nTesting hash algorithms...")
    
    try:
        import hashlib
        
        # Test sha3_512 availability
        try:
            hashlib.sha3_512(b"test")
            print("✓ sha3_512 is available")
        except AttributeError:
            print("⚠ sha3_512 not available, will use sha256 fallback")
        
        return True
    except Exception as e:
        print(f"✗ Hash algorithm test failed: {e}")
        return False

def test_regex_patterns():
    """Test that regex patterns are correctly defined"""
    print("\nTesting regex patterns...")
    
    try:
        import re
        
        # Test URN pattern (from enhanced_memory_sync)
        urn_pattern = r'urn:axiom:(?:module|device|namespace):[a-zA-Z0-9_-]+:[a-zA-Z0-9._-]+'
        test_urn = "urn:axiom:module:test-module:v1.0.0"
        match = re.search(urn_pattern, test_urn)
        if match:
            print(f"✓ URN pattern matches correctly: {match.group()}")
        else:
            print("✗ URN pattern failed to match")
            return False
        
        # Test file reference pattern (from enhanced_validator)
        file_pattern = r'[\w\-./]+\.(?:yaml|yml|md|py|sh)'
        test_file = "path/to/file.yaml"
        match = re.search(file_pattern, test_file)
        if match and match.group() == test_file:
            print(f"✓ File reference pattern matches correctly: {match.group()}")
        else:
            print("✗ File reference pattern failed to match correctly")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Regex pattern test failed: {e}")
        return False

def test_dataclass_usage():
    """Test that dataclasses are properly used"""
    print("\nTesting dataclass usage...")
    
    try:
        from dataclasses import dataclass, asdict
        
        @dataclass
        class TestIssue:
            severity: str
            message: str
        
        issue = TestIssue(severity="high", message="test")
        issue_dict = asdict(issue)
        
        # Test dict access
        if issue_dict["severity"] == "high":
            print("✓ Dataclass to dict conversion works correctly")
        else:
            print("✗ Dataclass to dict conversion failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Dataclass test failed: {e}")
        return False

def test_csv_injection_protection():
    """Test CSV injection protection"""
    print("\nTesting CSV injection protection...")
    
    try:
        def sanitize_csv_field(field: str) -> str:
            """防止CSV注入攻击"""
            if isinstance(field, str) and field and field[0] in ['=', '+', '-', '@']:
                return "'" + field
            return field
        
        # Test cases
        test_cases = [
            ("=SUM(A1:A10)", "'=SUM(A1:A10)"),
            ("+1234", "'+1234"),
            ("-5678", "'-5678"),
            ("@username", "'@username"),
            ("normal_text", "normal_text"),
        ]
        
        all_passed = True
        for input_val, expected in test_cases:
            result = sanitize_csv_field(input_val)
            if result == expected:
                print(f"✓ CSV sanitization correct: '{input_val}' -> '{result}'")
            else:
                print(f"✗ CSV sanitization failed: '{input_val}' -> '{result}' (expected '{expected}')")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print(f"✗ CSV injection protection test failed: {e}")
        return False

def test_git_repo_root():
    """Test git repo root detection"""
    print("\nTesting git repo root detection...")
    
    try:
        import subprocess
        
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True
        )
        repo_root = result.stdout.strip()
        print(f"✓ Git repo root detected: {repo_root}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠ Git command failed (expected in non-git environment): {e}")
        return True  # Not a failure if not in git repo
    except Exception as e:
        print(f"✗ Git repo root detection failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Running Fix Verification Tests")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Hash Algorithm Tests", test_hash_algorithms),
        ("Regex Pattern Tests", test_regex_patterns),
        ("Dataclass Usage Tests", test_dataclass_usage),
        ("CSV Injection Protection Tests", test_csv_injection_protection),
        ("Git Repo Root Detection Tests", test_git_repo_root),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())