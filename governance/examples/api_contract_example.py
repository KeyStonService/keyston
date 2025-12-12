#!/usr/bin/env python3
"""API Contract Example"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from api_contract import GovernanceValidator, ModuleRole

validator = GovernanceValidator()
validator.register_contract(
    module_name="sensor",
    role=ModuleRole.SENSOR_INTERFACE,
    input_schema={"type": "object"},
    output_schema={"type": "object"},
    max_latency_ms=50
)
print("✅ API Contract module working!")
