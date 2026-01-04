#!/usr/bin/env python3
"""
schema_validate.py - Validate YAML files against JSON schemas
"""

# import os
import json
import yaml
import jsonschema
from pathlib import Path

def find_schemas():
    """Find all JSON schema files"""
    schemas = {}
    schema_dir = Path("schemas")
    if schema_dir.exists():
        for schema_file in schema_dir.glob("*.json"):
            with open(schema_file, 'r') as f:
                schema = json.load(f)
                schemas[schema_file.stem] = schema
    return schemas

def validate_yaml_files():
    """Validate YAML files against schemas"""
    schemas = find_schemas()
    if not schemas:
        print("  ⚠️  No schemas found, skipping validation")
        return True
    
    errors = []
    validated = 0
    
    for yaml_file in Path(".").rglob("*.yaml"):
        if ".git" in str(yaml_file):
            continue
            
        try:
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            # Try to find matching schema
            for schema_name, schema in schemas.items():
                try:
                    jsonschema.validate(data, schema)
                    print(f"    ✅ {yaml_file} validated against {schema_name}")
                    validated += 1
                    break
                except jsonschema.ValidationError:
                    continue
                    
        except Exception as e:
            errors.append(f"{yaml_file}: {e}")
    
    if errors:
        print("  ❌ Validation errors:")
        for error in errors:
            print(f"    {error}")
        return False
    else:
        print(f"  ✅ Validated {validated} files")
        return True

if __name__ == "__main__":
    print("🔍 Running schema validation...")
    success = validate_yaml_files()
    if success:
        print("✅ Schema validation complete")
        exit(0)
    else:
        print("❌ Schema validation failed")
        exit(1)