#!/usr/bin/env python3
"""Multi-Layer Validator - Orchestrates all validation layers"""
import logging
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    layer: str
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

class MultiLayerValidator:
    """Orchestrates multi-layer validation"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.validators = []
        logger.info("Multi-layer validator initialized")
    
    def add_validator(self, validator):
        """Add a validation layer"""
        self.validators.append(validator)
    
    def validate(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Run all validation layers"""
        results = []
        for validator in self.validators:
            try:
                result = validator.validate(data)
                results.append(result)
                if not result.is_valid and self.config.get("fail_fast", False):
                    break
            except Exception as e:
                logger.error(f"Validation error: {e}")
                results.append(ValidationResult(
                    layer=validator.__class__.__name__,
                    is_valid=False,
                    errors=[str(e)]
                ))
        return results
