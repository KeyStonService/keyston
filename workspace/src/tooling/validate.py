#!/usr/bin/env python3
"""
Development Validation Tool
Wrapper tool that calls the authoritative controlplane validators.

IMPORTANT: This tool does NOT replace controlplane validators.
It only provides a convenient interface to call them from the workspace.
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Optional

# Path to authoritative validator
CONTROLPLANE_VALIDATOR = Path(__file__).parent.parent.parent.parent / "controlplane" / "baseline" / "validation" / "validate-root-specs.py"

def run_validation(verbose: bool = False) -> int:
    """
    Run the authoritative controlplane validator.
    
    Args:
        verbose: Enable verbose output
    
    Returns:
        Exit code from validator (0 = success, 1 = failure)
    """
    if not CONTROLPLANE_VALIDATOR.exists():
        print(f"ERROR: Authoritative validator not found at: {CONTROLPLANE_VALIDATOR}")
        print("This tool requires the controlplane validator to be present.")
        return 1
    
    print("=" * 80)
    print("DEVELOPMENT VALIDATION TOOL")
    print("=" * 80)
    print(f"Calling authoritative validator: {CONTROLPLANE_VALIDATOR}")
    print("=" * 80)
    print()
    
    # Call the authoritative validator
    # Safe subprocess usage: hardcoded command with parameter list, no shell=True
    cmd = [sys.executable, str(CONTROLPLANE_VALIDATOR)]
    if verbose:
        cmd.append("--verbose")
    
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        print(f"ERROR: Failed to run validator: {str(e)}")
        return 1

def validate_naming(target: str, target_type: str) -> int:
    """
    Validate naming conventions by calling controlplane validator.
    
    Args:
        target: The name to validate
        target_type: Type of target ('file', 'directory', 'identifier', 'version', 'urn')
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    validator_path = CONTROLPLANE_VALIDATOR.parent / "validators" / "validate_naming.py"
    
    if not validator_path.exists():
        print(f"ERROR: Naming validator not found at: {validator_path}")
        return 1
    
    print(f"Validating {target_type}: {target}")
    
    # Import and call the validator
    sys.path.insert(0, str(validator_path.parent))
    try:
        from validate_naming import validate_naming as validate
        is_valid, errors, warnings = validate(target, target_type)
        
        if is_valid:
            print(f"✓ PASS: {target}")
        else:
            print(f"✗ FAIL: {target}")
            for error in errors:
                print(f"  ERROR: {error}")
        
        for warning in warnings:
            print(f"  WARNING: {warning}")
        
        return 0 if is_valid else 1
    except Exception as e:
        print(f"ERROR: Validation failed: {str(e)}")
        return 1

def validate_namespace(namespace: str) -> int:
    """
    Validate namespace by calling controlplane validator.
    
    Args:
        namespace: The namespace to validate
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    validator_path = CONTROLPLANE_VALIDATOR.parent / "validators" / "validate_namespace.py"
    
    if not validator_path.exists():
        print(f"ERROR: Namespace validator not found at: {validator_path}")
        return 1
    
    print(f"Validating namespace: {namespace}")
    
    # Import and call the validator
    sys.path.insert(0, str(validator_path.parent))
    try:
        from validate_namespace import validate_namespace as validate
        is_valid, errors, warnings = validate(namespace, check_registration=True)
        
        if is_valid:
            print(f"✓ PASS: {namespace}")
        else:
            print(f"✗ FAIL: {namespace}")
            for error in errors:
                print(f"  ERROR: {error}")
        
        for warning in warnings:
            print(f"  WARNING: {warning}")
        
        return 0 if is_valid else 1
    except Exception as e:
        print(f"ERROR: Validation failed: {str(e)}")
        return 1

def validate_urn(urn: str) -> int:
    """
    Validate URN by calling controlplane validator.
    
    Args:
        urn: The URN to validate
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    validator_path = CONTROLPLANE_VALIDATOR.parent / "validators" / "validate_urn.py"
    
    if not validator_path.exists():
        print(f"ERROR: URN validator not found at: {validator_path}")
        return 1
    
    print(f"Validating URN: {urn}")
    
    # Import and call the validator
    sys.path.insert(0, str(validator_path.parent))
    try:
        from validate_urn import validate_urn as validate
        is_valid, errors, warnings = validate(urn, check_registration=True)
        
        if is_valid:
            print(f"✓ PASS: {urn}")
        else:
            print(f"✗ FAIL: {urn}")
            for error in errors:
                print(f"  ERROR: {error}")
        
        for warning in warnings:
            print(f"  WARNING: {warning}")
        
        return 0 if is_valid else 1
    except Exception as e:
        print(f"ERROR: Validation failed: {str(e)}")
        return 1

def validate_path(path: str) -> int:
    """
    Validate path by calling controlplane validator.
    
    Args:
        path: The path to validate
    
    Returns:
        Exit code (0 = success, 1 = failure)
    """
    validator_path = CONTROLPLANE_VALIDATOR.parent / "validators" / "validate_paths.py"
    
    if not validator_path.exists():
        print(f"ERROR: Path validator not found at: {validator_path}")
        return 1
    
    print(f"Validating path: {path}")
    
    # Import and call the validator
    sys.path.insert(0, str(validator_path.parent))
    try:
        from validate_paths import validate_path as validate
        is_valid, errors, warnings = validate(path, check_write_policy=True)
        
        if is_valid:
            print(f"✓ PASS: {path}")
        else:
            print(f"✗ FAIL: {path}")
            for error in errors:
                print(f"  ERROR: {error}")
        
        for warning in warnings:
            print(f"  WARNING: {warning}")
        
        return 0 if is_valid else 1
    except Exception as e:
        print(f"ERROR: Validation failed: {str(e)}")
        return 1

def print_usage():
    """Print usage information."""
    print("""
Usage: validate.py [command] [options]

Commands:
  all                    Run full validation suite (calls controlplane validator)
  naming <target> <type> Validate naming conventions
                         Types: file, directory, identifier, version, urn
  namespace <namespace>  Validate namespace
  urn <urn>              Validate URN
  path <path>            Validate path

Options:
  -v, --verbose         Enable verbose output
  -h, --help            Show this help message

Examples:
  validate.py all
  validate.py naming root.config.yaml file
  validate.py namespace machinenativeops
  validate.py urn urn:machinenativeops:module:core-validator:v1.0.0
  validate.py path controlplane/baseline/config/root.config.yaml

Note: This tool calls the authoritative validators in controlplane/baseline/validation/
      It does NOT replace them - it only provides a convenient wrapper.
""")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        return 1
    
    command = sys.argv[1]
    
    if command in ["-h", "--help"]:
        print_usage()
        return 0
    
    if command == "all":
        verbose = "-v" in sys.argv or "--verbose" in sys.argv
        return run_validation(verbose)
    
    elif command == "naming":
        if len(sys.argv) < 4:
            print("ERROR: naming command requires <target> and <type>")
            print_usage()
            return 1
        target = sys.argv[2]
        target_type = sys.argv[3]
        return validate_naming(target, target_type)
    
    elif command == "namespace":
        if len(sys.argv) < 3:
            print("ERROR: namespace command requires <namespace>")
            print_usage()
            return 1
        namespace = sys.argv[2]
        return validate_namespace(namespace)
    
    elif command == "urn":
        if len(sys.argv) < 3:
            print("ERROR: urn command requires <urn>")
            print_usage()
            return 1
        urn = sys.argv[2]
        return validate_urn(urn)
    
    elif command == "path":
        if len(sys.argv) < 3:
            print("ERROR: path command requires <path>")
            print_usage()
            return 1
        path = sys.argv[2]
        return validate_path(path)
    
    else:
        print(f"ERROR: Unknown command: {command}")
        print_usage()
        return 1

if __name__ == "__main__":
    sys.exit(main())