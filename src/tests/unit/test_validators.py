#!/usr/bin/env python3
"""Unit tests for validators"""
import pytest
from core.validators import SyntaxValidator, SecurityValidator

def test_syntax_validator():
    """Test syntax validator"""
    validator = SyntaxValidator({})
    result = validator.validate({"language": "python", "code": "print('hello')"})
    assert result["is_valid"] is True

def test_security_validator():
    """Test security validator"""
    validator = SecurityValidator({})
    result = validator.validate({"code": "x = 1"})
    assert result is not None
