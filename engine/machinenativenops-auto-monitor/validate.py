#!/usr/bin/env python3
"""
Basic validation script for MachineNativeOps Auto-Monitor
Checks that all modules can be imported and basic structure is correct
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def check_module_structure():
    """Verify module structure is correct."""
    errors = []
    
    # Check all required files exist
    required_files = [
        "src/machinenativenops_auto_monitor/__init__.py",
        "src/machinenativenops_auto_monitor/__main__.py",
        "src/machinenativenops_auto_monitor/app.py",
        "src/machinenativenops_auto_monitor/alerts.py",
        "src/machinenativenops_auto_monitor/collectors.py",
        "src/machinenativenops_auto_monitor/config.py",
        "src/machinenativenops_auto_monitor/儲存.py",
        "requirements.txt",
        "README.md",
    ]
    
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if not full_path.exists():
            errors.append(f"❌ Missing file: {file_path}")
        else:
            print(f"✅ Found: {file_path}")
    
    return errors

def check_imports():
    """Check that basic imports work (without dependencies)."""
    errors = []
    
    # Check config module (no external dependencies)
    try:
        from machinenativenops_auto_monitor import config
        print("✅ config module imports successfully")
    except Exception as e:
        errors.append(f"❌ config import failed: {e}")
    
    # Check alerts module (no external dependencies)
    try:
        from machinenativenops_auto_monitor import alerts
        print("✅ alerts module imports successfully")
    except Exception as e:
        errors.append(f"❌ alerts import failed: {e}")
    
    return errors

def main():
    print("🔍 Validating MachineNativeOps Auto-Monitor Structure\n")
    
    all_errors = []
    
    # Check structure
    print("📁 Checking module structure...")
    all_errors.extend(check_module_structure())
    
    print("\n📦 Checking module imports...")
    all_errors.extend(check_imports())
    
    print("\n" + "="*60)
    if all_errors:
        print(f"❌ Validation failed with {len(all_errors)} error(s):")
        for error in all_errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("✅ All validation checks passed!")
        print("\n📝 Note: Full functionality requires installing dependencies:")
        print("   pip install -r requirements.txt")
        sys.exit(0)

if __name__ == "__main__":
    main()
