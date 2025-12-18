"""
YAML Schema Validator (YAML Schema 驗證器)

JSON Schema 驗證系統，用於驗證 YAML 模組的結構和內容。

Reference: Schema validation best practices [8]
"""

import json
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class ValidationErrorType(Enum):
    """驗證錯誤類型"""
    TYPE_MISMATCH = "type_mismatch"
    REQUIRED_FIELD_MISSING = "required_field_missing"
    PATTERN_MISMATCH = "pattern_mismatch"
    VALUE_OUT_OF_RANGE = "value_out_of_range"
    ENUM_VIOLATION = "enum_violation"
    ARRAY_LENGTH_ERROR = "array_length_error"
    ADDITIONAL_PROPERTY = "additional_property"
    FORMAT_ERROR = "format_error"
    CUSTOM_VALIDATION_FAILED = "custom_validation_failed"


@dataclass
class ValidationError:
    """驗證錯誤"""
    path: str
    error_type: ValidationErrorType
    message: str
    expected: Any = None
    actual: Any = None
    suggestion: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'path': self.path,
            'error_type': self.error_type.value,
            'message': self.message,
            'expected': self.expected,
            'actual': self.actual,
            'suggestion': self.suggestion,
        }


@dataclass
class ValidationResult:
    """驗證結果"""
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    validated_at: str | None = None
    schema_version: str | None = None

    def add_error(self, error: ValidationError) -> None:
        """添加錯誤"""
        self.errors.append(error)
        self.valid = False

    def add_warning(self, warning: str) -> None:
        """添加警告"""
        self.warnings.append(warning)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            'valid': self.valid,
            'errors': [e.to_dict() for e in self.errors],
            'warnings': self.warnings,
            'validated_at': self.validated_at,
            'schema_version': self.schema_version,
        }


class SchemaRegistry:
    """
    Schema 註冊表
    
    管理和存儲所有 JSON Schema 定義。
    """

    def __init__(self):
        self._schemas: dict[str, dict[str, Any]] = {}
        self._schema_versions: dict[str, list[str]] = {}

    def register(self, schema_id: str, schema: dict[str, Any], version: str = "1.0.0") -> None:
        """註冊 Schema"""
        full_id = f"{schema_id}@{version}"
        self._schemas[full_id] = schema

        if schema_id not in self._schema_versions:
            self._schema_versions[schema_id] = []
        self._schema_versions[schema_id].append(version)

    def get(self, schema_id: str, version: str | None = None) -> dict[str, Any] | None:
        """獲取 Schema"""
        if version:
            full_id = f"{schema_id}@{version}"
            return self._schemas.get(full_id)

        # 獲取最新版本
        versions = self._schema_versions.get(schema_id, [])
        if not versions:
            return None

        latest_version = sorted(versions)[-1]
        return self._schemas.get(f"{schema_id}@{latest_version}")

    def list_schemas(self) -> list[str]:
        """列出所有 Schema"""
        return list(self._schema_versions.keys())

    def get_versions(self, schema_id: str) -> list[str]:
        """獲取 Schema 的所有版本"""
        return self._schema_versions.get(schema_id, [])


class YAMLSchemaValidator:
    """
    YAML Schema 驗證器
    
    使用 JSON Schema 驗證 YAML 模組的結構和內容。
    """

    # 內建類型映射
    TYPE_MAP = {
        'string': str,
        'number': (int, float),
        'integer': int,
        'boolean': bool,
        'array': list,
        'object': dict,
        'null': type(None),
    }

    # 格式驗證正則表達式
    FORMAT_PATTERNS = {
        'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        'uri': r'^https?://[^\s/$.?#].[^\s]*$',
        'date': r'^\d{4}-\d{2}-\d{2}$',
        'date-time': r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',
        'uuid': r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        'semver': r'^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$',
    }

    def __init__(self, registry: SchemaRegistry | None = None):
        self.registry = registry or SchemaRegistry()
        self._custom_validators: dict[str, callable] = {}

    def register_custom_validator(self, name: str, validator: callable) -> None:
        """註冊自定義驗證器"""
        self._custom_validators[name] = validator

    def validate(self, data: Any, schema: dict[str, Any], path: str = "$") -> ValidationResult:
        """
        驗證數據是否符合 Schema
        
        Args:
            data: 待驗證的數據
            schema: JSON Schema
            path: 當前路徑（用於錯誤報告）
        
        Returns:
            ValidationResult: 驗證結果
        """
        result = ValidationResult(valid=True)
        result.schema_version = schema.get('$schema', 'unknown')

        self._validate_node(data, schema, path, result)

        return result

    def _validate_node(self, data: Any, schema: dict[str, Any], path: str, result: ValidationResult) -> None:
        """驗證單個節點"""

        # 檢查類型
        if 'type' in schema:
            self._validate_type(data, schema['type'], path, result)

        # 檢查 enum
        if 'enum' in schema:
            self._validate_enum(data, schema['enum'], path, result)

        # 檢查 const
        if 'const' in schema and data != schema['const']:
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.ENUM_VIOLATION,
                message=f"Value must be exactly {schema['const']}",
                expected=schema['const'],
                actual=data,
            ))

        # 字符串驗證
        if isinstance(data, str):
            self._validate_string(data, schema, path, result)

        # 數字驗證
        if isinstance(data, (int, float)) and not isinstance(data, bool):
            self._validate_number(data, schema, path, result)

        # 數組驗證
        if isinstance(data, list):
            self._validate_array(data, schema, path, result)

        # 對象驗證
        if isinstance(data, dict):
            self._validate_object(data, schema, path, result)

        # 自定義驗證
        if 'x-custom-validator' in schema:
            validator_name = schema['x-custom-validator']
            if validator_name in self._custom_validators:
                try:
                    self._custom_validators[validator_name](data, path, result)
                except Exception as e:
                    result.add_error(ValidationError(
                        path=path,
                        error_type=ValidationErrorType.CUSTOM_VALIDATION_FAILED,
                        message=f"Custom validator '{validator_name}' failed: {str(e)}",
                    ))

    def _validate_type(self, data: Any, expected_type: str, path: str, result: ValidationResult) -> None:
        """驗證類型"""
        if expected_type == 'any':
            return

        expected_python_type = self.TYPE_MAP.get(expected_type)
        if expected_python_type is None:
            return

        # 特殊處理：boolean 不應該是 int
        if expected_type == 'boolean' and isinstance(data, bool):
            return
        if expected_type == 'integer' and isinstance(data, bool):
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.TYPE_MISMATCH,
                message=f"Expected {expected_type}, got boolean",
                expected=expected_type,
                actual=type(data).__name__,
            ))
            return

        if not isinstance(data, expected_python_type):
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.TYPE_MISMATCH,
                message=f"Expected {expected_type}, got {type(data).__name__}",
                expected=expected_type,
                actual=type(data).__name__,
            ))

    def _validate_enum(self, data: Any, enum_values: list[Any], path: str, result: ValidationResult) -> None:
        """驗證 enum"""
        if data not in enum_values:
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.ENUM_VIOLATION,
                message=f"Value must be one of {enum_values}",
                expected=enum_values,
                actual=data,
            ))

    def _validate_string(self, data: str, schema: dict[str, Any], path: str, result: ValidationResult) -> None:
        """驗證字符串"""
        # 最小長度
        if 'minLength' in schema and len(data) < schema['minLength']:
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.VALUE_OUT_OF_RANGE,
                message=f"String length {len(data)} is less than minimum {schema['minLength']}",
                expected=f">= {schema['minLength']}",
                actual=len(data),
            ))

        # 最大長度
        if 'maxLength' in schema and len(data) > schema['maxLength']:
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.VALUE_OUT_OF_RANGE,
                message=f"String length {len(data)} is greater than maximum {schema['maxLength']}",
                expected=f"<= {schema['maxLength']}",
                actual=len(data),
            ))

        # 模式匹配
        if 'pattern' in schema and not re.match(schema['pattern'], data):
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.PATTERN_MISMATCH,
                message=f"String does not match pattern {schema['pattern']}",
                expected=schema['pattern'],
                actual=data,
            ))

        # 格式驗證
        if 'format' in schema:
            format_name = schema['format']
            if format_name in self.FORMAT_PATTERNS:
                if not re.match(self.FORMAT_PATTERNS[format_name], data):
                    result.add_error(ValidationError(
                        path=path,
                        error_type=ValidationErrorType.FORMAT_ERROR,
                        message=f"String does not match format '{format_name}'",
                        expected=format_name,
                        actual=data,
                    ))

    def _validate_number(self, data: float, schema: dict[str, Any], path: str, result: ValidationResult) -> None:
        """驗證數字"""
        # 最小值
        if 'minimum' in schema:
            if 'exclusiveMinimum' in schema and schema['exclusiveMinimum']:
                if data <= schema['minimum']:
                    result.add_error(ValidationError(
                        path=path,
                        error_type=ValidationErrorType.VALUE_OUT_OF_RANGE,
                        message=f"Value {data} must be greater than {schema['minimum']}",
                        expected=f"> {schema['minimum']}",
                        actual=data,
                    ))
            elif data < schema['minimum']:
                result.add_error(ValidationError(
                    path=path,
                    error_type=ValidationErrorType.VALUE_OUT_OF_RANGE,
                    message=f"Value {data} is less than minimum {schema['minimum']}",
                    expected=f">= {schema['minimum']}",
                    actual=data,
                ))

        # 最大值
        if 'maximum' in schema:
            if 'exclusiveMaximum' in schema and schema['exclusiveMaximum']:
                if data >= schema['maximum']:
                    result.add_error(ValidationError(
                        path=path,
                        error_type=ValidationErrorType.VALUE_OUT_OF_RANGE,
                        message=f"Value {data} must be less than {schema['maximum']}",
                        expected=f"< {schema['maximum']}",
                        actual=data,
                    ))
            elif data > schema['maximum']:
                result.add_error(ValidationError(
                    path=path,
                    error_type=ValidationErrorType.VALUE_OUT_OF_RANGE,
                    message=f"Value {data} is greater than maximum {schema['maximum']}",
                    expected=f"<= {schema['maximum']}",
                    actual=data,
                ))

        # 倍數
        if 'multipleOf' in schema and data % schema['multipleOf'] != 0:
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.VALUE_OUT_OF_RANGE,
                message=f"Value {data} is not a multiple of {schema['multipleOf']}",
                expected=f"multiple of {schema['multipleOf']}",
                actual=data,
            ))

    def _validate_array(self, data: list, schema: dict[str, Any], path: str, result: ValidationResult) -> None:
        """驗證數組"""
        # 最小項目數
        if 'minItems' in schema and len(data) < schema['minItems']:
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.ARRAY_LENGTH_ERROR,
                message=f"Array length {len(data)} is less than minimum {schema['minItems']}",
                expected=f">= {schema['minItems']} items",
                actual=len(data),
            ))

        # 最大項目數
        if 'maxItems' in schema and len(data) > schema['maxItems']:
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.ARRAY_LENGTH_ERROR,
                message=f"Array length {len(data)} is greater than maximum {schema['maxItems']}",
                expected=f"<= {schema['maxItems']} items",
                actual=len(data),
            ))

        # 唯一性
        if schema.get('uniqueItems', False):
            seen = []
            for item in data:
                item_json = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else item
                if item_json in seen:
                    result.add_error(ValidationError(
                        path=path,
                        error_type=ValidationErrorType.CUSTOM_VALIDATION_FAILED,
                        message="Array items must be unique",
                        actual=data,
                    ))
                    break
                seen.append(item_json)

        # 項目驗證
        if 'items' in schema:
            for i, item in enumerate(data):
                item_path = f"{path}[{i}]"
                self._validate_node(item, schema['items'], item_path, result)

    def _validate_object(self, data: dict, schema: dict[str, Any], path: str, result: ValidationResult) -> None:
        """驗證對象"""
        # 必需屬性
        if 'required' in schema:
            for required_prop in schema['required']:
                if required_prop not in data:
                    result.add_error(ValidationError(
                        path=f"{path}.{required_prop}",
                        error_type=ValidationErrorType.REQUIRED_FIELD_MISSING,
                        message=f"Required property '{required_prop}' is missing",
                        expected=required_prop,
                    ))

        # 屬性驗證
        if 'properties' in schema:
            for prop_name, prop_schema in schema['properties'].items():
                if prop_name in data:
                    prop_path = f"{path}.{prop_name}"
                    self._validate_node(data[prop_name], prop_schema, prop_path, result)

        # 額外屬性
        if schema.get('additionalProperties') is False:
            allowed_props = set(schema.get('properties', {}).keys())
            allowed_props.update(schema.get('patternProperties', {}).keys())

            for prop_name in data:
                if prop_name not in allowed_props:
                    result.add_error(ValidationError(
                        path=f"{path}.{prop_name}",
                        error_type=ValidationErrorType.ADDITIONAL_PROPERTY,
                        message=f"Additional property '{prop_name}' is not allowed",
                        actual=prop_name,
                    ))

        # 屬性數量
        if 'minProperties' in schema and len(data) < schema['minProperties']:
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.VALUE_OUT_OF_RANGE,
                message=f"Object has {len(data)} properties, minimum is {schema['minProperties']}",
                expected=f">= {schema['minProperties']} properties",
                actual=len(data),
            ))

        if 'maxProperties' in schema and len(data) > schema['maxProperties']:
            result.add_error(ValidationError(
                path=path,
                error_type=ValidationErrorType.VALUE_OUT_OF_RANGE,
                message=f"Object has {len(data)} properties, maximum is {schema['maxProperties']}",
                expected=f"<= {schema['maxProperties']} properties",
                actual=len(data),
            ))
