"""Basic tests for Project Factory"""

import pytest
from pathlib import Path
from core.project_factory.spec import ProjectSpec, ProjectType, Language
from core.project_factory.factory import ProjectFactory


def test_project_spec_creation():
    """Test creating a basic project specification."""
    spec = ProjectSpec(
        name="test-service",
        type=ProjectType.MICROSERVICE,
        language=Language.PYTHON,
        framework="fastapi",
        description="Test service"
    )
    
    assert spec.name == "test-service"
    assert spec.type == ProjectType.MICROSERVICE


def test_factory_initialization():
    """Test factory initialization."""
    factory = ProjectFactory()
    assert factory.template_engine is not None
