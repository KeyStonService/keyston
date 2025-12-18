#!/usr/bin/env python3
"""Syntax Validator - Validates code syntax"""
import ast
import yaml
import json
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SyntaxValidator:
    """Validates syntax for multiple languages"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.parsers = {
            "python": self._parse_python,
            "yaml": self._parse_yaml,
            "json": self._parse_json,
        }
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate syntax"""
        language = data.get("language", "python")
        code = data.get("code", "")
        
        errors = []
        warnings = []
        
        parser = self.parsers.get(language)
        if parser:
            errors, warnings = parser(code)
        else:
            warnings.append(f"No parser for language: {language}")
        
        return {
            "layer": "syntax",
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _parse_python(self, code: str):
        """Parse Python code"""
        errors = []
        warnings = []
        try:
            ast.parse(code)
        except SyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.msg}")
        return errors, warnings
    
    def _parse_yaml(self, code: str):
        """Parse YAML"""
        errors = []
        warnings = []
        try:
            yaml.safe_load(code)
        except yaml.YAMLError as e:
            errors.append(f"YAML error: {str(e)}")
        return errors, warnings
    
    def _parse_json(self, code: str):
        """Parse JSON"""
        errors = []
        warnings = []
        try:
            json.loads(code)
        except json.JSONDecodeError as e:
            errors.append(f"JSON error at line {e.lineno}: {e.msg}")
        return errors, warnings
