#!/usr/bin/env python3
"""Unit tests for contract engine"""
import pytest
from core.contract_engine import ContractRegistry, ContractDefinition

def test_contract_registry_init():
    """Test contract registry initialization"""
    registry = ContractRegistry()
    assert registry is not None

def test_contract_registration():
    """Test contract registration"""
    from datetime import datetime

    # Create a contract registry
    registry = ContractRegistry()

    # Create contract metadata
    metadata = {
        "name": "test-contract",
        "version": "1.0.0",
        "contract_type": "service",
        "description": "Test contract for unit testing",
        "author": "test-suite",
        "created_at": datetime.utcnow().isoformat(),
        "tags": ["test", "unit"],
        "dependencies": []
    }

    # Create contract definition
    from core.contract_engine import ContractMetadata, ContractType
    contract_metadata = ContractMetadata(
        name=metadata["name"],
        version=metadata["version"],
        contract_type=ContractType.SERVICE,
        description=metadata["description"],
        author=metadata["author"],
        tags=metadata["tags"],
        dependencies=metadata["dependencies"]
    )

    contract = ContractDefinition(
        metadata=contract_metadata,
        schema={"type": "object", "properties": {}},
        validation_rules=[{"rule": "required", "fields": []}],
        execution_config={"timeout": 30},
        lifecycle_config={"retention_days": 90}
    )

    # Register the contract
    contract_id = registry.register(contract)

    # Verify registration
    assert contract_id is not None
    assert len(contract_id) > 0

    # Verify we can retrieve it
    retrieved = registry.get(contract_id)
    assert retrieved is not None
    assert retrieved.metadata.name == "test-contract"
    assert retrieved.metadata.version == "1.0.0"

    # Test duplicate registration raises ValueError
    with pytest.raises(ValueError, match="already registered"):
        registry.register(contract)
