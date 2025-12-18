#!/usr/bin/env python3
"""Security Validator - Security vulnerability scanning"""
import re
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Validates security aspects"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.patterns = self._load_security_patterns()
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate security"""
        code = data.get("code", "")
        errors = []
        warnings = []
        
        # Check for hardcoded secrets
        secret_issues = self._check_hardcoded_secrets(code)
        errors.extend(secret_issues)
        
        # Check for SQL injection
        sql_issues = self._check_sql_injection(code)
        errors.extend(sql_issues)
        
        # Check for XSS vulnerabilities
        xss_issues = self._check_xss(code)
        warnings.extend(xss_issues)
        
        return {
            "layer": "security",
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _load_security_patterns(self) -> List[Tuple[str, str, str]]:
        """Load security patterns"""
        return [
            ("hardcoded_secrets", r"(password|api_key|secret)\s*=\s*['\"]\w+", "critical"),
            ("sql_injection", r"execute\(.*\+.*\)", "critical"),
            ("xss", r"innerHTML\s*=\s*", "high"),
        ]
    
    def _check_hardcoded_secrets(self, code: str) -> List[str]:
        """Check for hardcoded secrets"""
        errors = []
        pattern = r"(password|api_key|secret|token)\s*=\s*['\"][\w-]+"
        matches = re.finditer(pattern, code, re.IGNORECASE)
        for match in matches:
            errors.append(f"Hardcoded secret found: {match.group(0)}")
        return errors
    
    def _check_sql_injection(self, code: str) -> List[str]:
        """Check for SQL injection patterns"""
        errors = []
        pattern = r"execute\([^)]*\+[^)]*\)"
        matches = re.finditer(pattern, code)
        for match in matches:
            errors.append(f"Potential SQL injection: {match.group(0)}")
        return errors
    
    def _check_xss(self, code: str) -> List[str]:
        """Check for XSS vulnerabilities"""
        warnings = []
        pattern = r"innerHTML\s*=\s*"
        matches = re.finditer(pattern, code)
        for match in matches:
            warnings.append(f"Potential XSS vulnerability: {match.group(0)}")
        return warnings
