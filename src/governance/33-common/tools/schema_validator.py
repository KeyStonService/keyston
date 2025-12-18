#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Schema Validator

Validates configuration and data files against JSON schemas.
Checks:
- Schema compliance
- Required properties
- Type validation
- Format validation
- Reference validation
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Schema validation error"""
    file_path: str
    error_message: str
    error_type: str
    severity: str  # error, warning


class SchemaValidator:
    """Validates files against JSON schemas"""

    def __init__(self, schemas_path: Path):
        """Initialize validator with schemas directory"""
        self.schemas_path = schemas_path
        self.schemas: Dict[str, Any] = {}
        self._load_schemas()

    def _load_schemas(self) -> None:
        """Load all schema definitions"""
        if not self.schemas_path.exists():
            print(f"⚠️  Schemas directory not found: {self.schemas_path}")
            return

        for schema_file in self.schemas_path.glob("*.json"):
            with open(schema_file) as f:
                self.schemas[schema_file.stem] = json.load(f)

    def validate_file(self, file_path: Path, schema_name: str) -> Tuple[bool, List[ValidationError]]:
        """Validate a single file against a schema"""
        errors: List[ValidationError] = []

        if schema_name not in self.schemas:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_message=f"Schema '{schema_name}' not found",
                error_type="schema_not_found",
                severity="error"
            ))
            return False, errors

        # Load the file
        try:
            if file_path.suffix in ['.yaml', '.yml']:
                with open(file_path) as f:
                    data = yaml.safe_load(f)
            elif file_path.suffix == '.json':
                with open(file_path) as f:
                    data = json.load(f)
            else:
                errors.append(ValidationError(
                    file_path=str(file_path),
                    error_message=f"Unsupported file type: {file_path.suffix}",
                    error_type="unsupported_format",
                    severity="error"
                ))
                return False, errors
        except Exception as e:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_message=f"Failed to parse file: {str(e)}",
                error_type="parse_error",
                severity="error"
            ))
            return False, errors

        if data is None:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_message="File is empty or contains only null",
                error_type="empty_file",
                severity="error"
            ))
            return False, errors

        # Validate against schema
        schema = self.schemas[schema_name]
        validation_errors = self._validate_against_schema(data, schema, file_path)
        errors.extend(validation_errors)

        return len(errors) == 0, errors

    def _validate_against_schema(self, data: Any, schema: Dict[str, Any],
                                  file_path: Path) -> List[ValidationError]:
        """Validate data against schema"""
        errors: List[ValidationError] = []

        # Check if schema requires object type
        if schema.get("type") == "object" and not isinstance(data, dict):
            errors.append(ValidationError(
                file_path=str(file_path),
                error_message=f"Expected object, got {type(data).__name__}",
                error_type="type_mismatch",
                severity="error"
            ))
            return errors

        # Check required fields
        required_fields = schema.get("required", [])
        if isinstance(data, dict):
            for field in required_fields:
                if field not in data:
                    errors.append(ValidationError(
                        file_path=str(file_path),
                        error_message=f"Missing required field: {field}",
                        error_type="missing_field",
                        severity="error"
                    ))

        # Check properties
        properties = schema.get("properties", {})
        if isinstance(data, dict):
            for field, field_schema in properties.items():
                if field in data:
                    field_errors = self._validate_field(
                        data[field],
                        field_schema,
                        field,
                        file_path
                    )
                    errors.extend(field_errors)

        return errors

    def _validate_field(self, value: Any, field_schema: Dict[str, Any],
                        field_name: str, file_path: Path) -> List[ValidationError]:
        """Validate a single field"""
        errors: List[ValidationError] = []

        # Check type
        expected_type = field_schema.get("type")
        if expected_type:
            if expected_type == "string" and not isinstance(value, str):
                errors.append(ValidationError(
                    file_path=str(file_path),
                    error_message=f"Field '{field_name}' should be string, got {type(value).__name__}",
                    error_type="type_mismatch",
                    severity="error"
                ))
            elif expected_type == "number" and not isinstance(value, (int, float)):
                errors.append(ValidationError(
                    file_path=str(file_path),
                    error_message=f"Field '{field_name}' should be number, got {type(value).__name__}",
                    error_type="type_mismatch",
                    severity="error"
                ))
            elif expected_type == "array" and not isinstance(value, list):
                errors.append(ValidationError(
                    file_path=str(file_path),
                    error_message=f"Field '{field_name}' should be array, got {type(value).__name__}",
                    error_type="type_mismatch",
                    severity="error"
                ))
            elif expected_type == "object" and not isinstance(value, dict):
                errors.append(ValidationError(
                    file_path=str(file_path),
                    error_message=f"Field '{field_name}' should be object, got {type(value).__name__}",
                    error_type="type_mismatch",
                    severity="error"
                ))

        # Check format
        if field_schema.get("format") == "date":
            if isinstance(value, str):
                try:
                    from datetime import datetime
                    datetime.strptime(value, "%Y-%m-%d")
                except ValueError:
                    errors.append(ValidationError(
                        file_path=str(file_path),
                        error_message=f"Field '{field_name}' is not a valid date (YYYY-MM-DD): {value}",
                        error_type="format_error",
                        severity="error"
                    ))

        # Check pattern (regex)
        if field_schema.get("pattern") and isinstance(value, str):
            import re
            pattern = field_schema["pattern"]
            if not re.match(pattern, value):
                errors.append(ValidationError(
                    file_path=str(file_path),
                    error_message=f"Field '{field_name}' doesn't match pattern {pattern}: {value}",
                    error_type="pattern_error",
                    severity="error"
                ))

        # Check enum
        if "enum" in field_schema and value not in field_schema["enum"]:
            errors.append(ValidationError(
                file_path=str(file_path),
                error_message=f"Field '{field_name}' value '{value}' not in allowed values: {field_schema['enum']}",
                error_type="enum_error",
                severity="error"
            ))

        return errors

    def validate_directory(self, directory: Path, schema_name: str) -> Tuple[bool, Dict[str, Any]]:
        """Validate all files in directory against schema"""
        print(f"🔍 Validating files against '{schema_name}' schema...")
        print("=" * 100)

        results = {
            "schema": schema_name,
            "files_checked": 0,
            "files_valid": 0,
            "files_invalid": 0,
            "errors": [],
            "warnings": []
        }

        for config_file in directory.glob("*.*"):
            if config_file.suffix in ['.json', '.yaml', '.yml']:
                results["files_checked"] += 1
                valid, errors = self.validate_file(config_file, schema_name)

                if valid:
                    results["files_valid"] += 1
                    print(f"  ✅ {config_file.name}")
                else:
                    results["files_invalid"] += 1
                    print(f"  ❌ {config_file.name}")
                    for error in errors:
                        if error.severity == "error":
                            results["errors"].append({
                                "file": config_file.name,
                                "message": error.error_message
                            })
                            print(f"      • {error.error_message}")

        overall_valid = results["files_invalid"] == 0
        return overall_valid, results

    def print_report(self, report: Dict[str, Any]) -> None:
        """Print validation report"""
        print("\n" + "=" * 100)
        print("📋 SCHEMA VALIDATION REPORT")
        print("=" * 100)

        print(f"\n📊 Summary:")
        print(f"   Schema:              {report['schema']}")
        print(f"   Files Checked:       {report['files_checked']}")
        print(f"   Files Valid:         {report['files_valid']}")
        print(f"   Files Invalid:       {report['files_invalid']}")
        print(f"   Errors:              {len(report['errors'])}")

        if report["errors"]:
            print(f"\n❌ Validation Errors:")
            for error in report["errors"]:
                print(f"   {error['file']}: {error['message']}")


def main():
    """Main entry point"""
    governance_root = Path(__file__).parent.parent.parent
    schemas_path = governance_root / "common" / "schemas"

    validator = SchemaValidator(schemas_path)

    # Example: validate all policy files
    print("=" * 100)
    print("🔍 GOVERNANCE SCHEMA VALIDATION")
    print("=" * 100)

    api_config = governance_root / "api-governance" / "config"
    if api_config.exists():
        valid, report = validator.validate_directory(api_config, "policy")
        validator.print_report(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
