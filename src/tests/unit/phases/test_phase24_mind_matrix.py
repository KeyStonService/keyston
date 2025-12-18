# ═══════════════════════════════════════════════════════════════════════════════
#                    SynergyMesh Phase 24 Mind Matrix Tests
#                    第二十四階段心智矩陣測試
# ═══════════════════════════════════════════════════════════════════════════════
"""
Tests for Phase 24: Mind Matrix System Integration.

最小測試向量，保證相容與不重疊。
Minimal test vectors ensuring compatibility and no overlap.
"""

import sys
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

# Add runtime to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from runtime.mind_matrix.main import (
    ExecutiveRole,
    MindMatrix,
    MindMatrixModel,
)


class TestTopologyLoadAndSelfcheck:
    """Tests for topology loading and self-check validation."""

    @pytest.fixture
    def topology_path(self) -> Path:
        """Get path to topology config file."""
        return Path(__file__).parent.parent.parent / "config" / "topology-mind-matrix.yaml"

    @pytest.fixture
    def topology_config(self, topology_path: Path) -> dict:
        """Load topology configuration."""
        with open(topology_path, encoding="utf-8") as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def mind_matrix(self, topology_config: dict) -> MindMatrix:
        """Create MindMatrix instance."""
        return MindMatrix(topology_config)

    def test_topology_load_and_selfcheck(self, mind_matrix: MindMatrix) -> None:
        """Test that topology loads and passes self-check."""
        # Verify tool pipeline has exactly 8 stages
        assert len(mind_matrix.get_tool_pipeline_stages()) == 8

        # Verify YAML validation pipeline has exactly 7 stages
        assert len(mind_matrix.get_yaml_validation_stages()) == 7

    def test_tool_pipeline_stages_content(self, mind_matrix: MindMatrix) -> None:
        """Test tool pipeline stages have correct content."""
        stages = mind_matrix.get_tool_pipeline_stages()

        expected_stages = [
            "interface_metadata",
            "param_validation",
            "permission_resolution",
            "security_assessment",
            "approval_chain",
            "tool_execution",
            "history_freeze",
            "continuous_monitoring",
        ]

        assert stages == expected_stages

    def test_yaml_validation_stages_content(self, mind_matrix: MindMatrix) -> None:
        """Test YAML validation stages have correct content."""
        stages = mind_matrix.get_yaml_validation_stages()

        expected_stages = [
            "lint",
            "format",
            "schema",
            "vector_tests",
            "policy_gate",
            "sbom",
            "signature_verification",
        ]

        assert stages == expected_stages


class TestExecutiveRoles:
    """Tests for executive role definitions."""

    @pytest.fixture
    def mind_matrix(self) -> MindMatrix:
        """Create MindMatrix instance from config file."""
        topology_path = Path(__file__).parent.parent.parent / "config" / "topology-mind-matrix.yaml"
        with open(topology_path, encoding="utf-8") as f:
            topology = yaml.safe_load(f)
        return MindMatrix(topology)

    def test_executive_roles_minimum(self, mind_matrix: MindMatrix) -> None:
        """Test that minimum required executive roles exist."""
        roles = mind_matrix.get_executive_roles()
        ids = {r.id for r in roles}

        # CEO role must exist
        assert "synergymesh.ceo" in ids

        # CISO role must exist
        assert "synergymesh.ciso" in ids

    def test_ceo_mission_exists(self, mind_matrix: MindMatrix) -> None:
        """Test that CEO has defined missions."""
        mission = mind_matrix.get_ceo_mission("synergymesh.ceo")

        assert mission is not None
        assert len(mission) > 0

    def test_ceo_mission_content(self, mind_matrix: MindMatrix) -> None:
        """Test CEO mission content."""
        mission = mind_matrix.get_ceo_mission("synergymesh.ceo")

        assert mission is not None
        # Should contain key mission elements
        mission_text = " ".join(mission)
        assert "自治" in mission_text or "全域一致性" in mission_text

    def test_executive_role_structure(self, mind_matrix: MindMatrix) -> None:
        """Test that executive roles have proper structure."""
        roles = mind_matrix.get_executive_roles()

        for role in roles:
            assert isinstance(role, ExecutiveRole)
            assert role.id is not None
            assert role.title is not None
            assert role.kind is not None
            assert isinstance(role.domains, list)
            assert isinstance(role.values, list)


class TestGovernancePrinciples:
    """Tests for governance principles coverage."""

    @pytest.fixture
    def mind_matrix(self) -> MindMatrix:
        """Create MindMatrix instance from config file."""
        topology_path = Path(__file__).parent.parent.parent / "config" / "topology-mind-matrix.yaml"
        with open(topology_path, encoding="utf-8") as f:
            topology = yaml.safe_load(f)
        return MindMatrix(topology)

    def test_governance_principles_cover(self, mind_matrix: MindMatrix) -> None:
        """Test that all required governance principles are defined."""
        gp = set(mind_matrix.model.governance_principles)

        must_have = {
            "depth_first",
            "verifiability_first",
            "security_first",
            "automation_first",
            "traceability_first",
        }

        assert must_have.issubset(gp)

    def test_governance_principles_count(self, mind_matrix: MindMatrix) -> None:
        """Test governance principles count."""
        principles = mind_matrix.get_governance_principles()

        # Should have at least 5 core principles
        assert len(principles) >= 5


class TestCognitiveStack:
    """Tests for cognitive stack configuration."""

    @pytest.fixture
    def mind_matrix(self) -> MindMatrix:
        """Create MindMatrix instance from config file."""
        topology_path = Path(__file__).parent.parent.parent / "config" / "topology-mind-matrix.yaml"
        with open(topology_path, encoding="utf-8") as f:
            topology = yaml.safe_load(f)
        return MindMatrix(topology)

    def test_cognitive_stack_layers(self, mind_matrix: MindMatrix) -> None:
        """Test cognitive stack has required layers."""
        stack = mind_matrix.get_cognitive_stack()

        # Should have 4 layers: perception, reasoning, execution, proof
        assert len(stack) == 4

        layer_ids = {layer.id for layer in stack}
        expected_layers = {"L1-perception", "L2-reasoning", "L3-execution", "L4-proof"}

        assert expected_layers == layer_ids

    def test_cognitive_stack_responsibilities(self, mind_matrix: MindMatrix) -> None:
        """Test each cognitive stack layer has responsibilities."""
        stack = mind_matrix.get_cognitive_stack()

        for layer in stack:
            assert len(layer.responsibilities) > 0


class TestMultiAgentHypergraph:
    """Tests for multi-agent hypergraph configuration."""

    @pytest.fixture
    def mind_matrix(self) -> MindMatrix:
        """Create MindMatrix instance from config file."""
        topology_path = Path(__file__).parent.parent.parent / "config" / "topology-mind-matrix.yaml"
        with open(topology_path, encoding="utf-8") as f:
            topology = yaml.safe_load(f)
        return MindMatrix(topology)

    def test_agents_defined(self, mind_matrix: MindMatrix) -> None:
        """Test that agents are defined."""
        agents = mind_matrix.get_agents()

        assert len(agents) >= 1

        # Check for expected agent types
        agent_names = {agent.name for agent in agents}
        assert "reasoner" in agent_names
        assert "policy" in agent_names

    def test_coordination_mechanisms(self, mind_matrix: MindMatrix) -> None:
        """Test coordination mechanisms are defined."""
        mechanisms = mind_matrix.get_coordination_mechanisms()

        assert len(mechanisms) >= 1
        assert "sync_barrier" in mechanisms


class TestSLSAConfiguration:
    """Tests for SLSA configuration."""

    @pytest.fixture
    def mind_matrix(self) -> MindMatrix:
        """Create MindMatrix instance from config file."""
        topology_path = Path(__file__).parent.parent.parent / "config" / "topology-mind-matrix.yaml"
        with open(topology_path, encoding="utf-8") as f:
            topology = yaml.safe_load(f)
        return MindMatrix(topology)

    def test_slsa_level(self, mind_matrix: MindMatrix) -> None:
        """Test SLSA level is defined."""
        level = mind_matrix.get_slsa_level()

        assert level == "L3"

    def test_slsa_evidence_config(self, mind_matrix: MindMatrix) -> None:
        """Test SLSA evidence configuration."""
        slsa = mind_matrix.model.slsa

        assert slsa.evidence.produce is True
        assert slsa.evidence.store == "immutable_audit_log"


class TestSchemaValidation:
    """Tests for schema validation."""

    def test_invalid_config_raises_error(self) -> None:
        """Test that invalid config raises ValidationError."""
        invalid_config = {
            "mind_matrix": {
                "version": "1.0.0",
                # Missing required fields
            }
        }

        with pytest.raises(ValidationError):
            MindMatrix(invalid_config)

    def test_missing_mind_matrix_key(self) -> None:
        """Test handling of missing mind_matrix key."""
        empty_config: dict = {}

        with pytest.raises(ValidationError):
            MindMatrix(empty_config)


class TestSystemManifest:
    """Tests for system manifest configuration."""

    @pytest.fixture
    def manifest_path(self) -> Path:
        """Get path to system manifest file."""
        return Path(__file__).parent.parent.parent / "config" / "system-manifest.yaml"

    def test_manifest_exists(self, manifest_path: Path) -> None:
        """Test system manifest file exists."""
        assert manifest_path.exists()

    def test_manifest_references_topology(self, manifest_path: Path) -> None:
        """Test manifest references topology-mind-matrix.yaml."""
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        # Find mind_matrix config reference
        mind_matrix_config = None
        for config in manifest.get("configs", []):
            if config.get("id") == "mind_matrix":
                mind_matrix_config = config
                break

        assert mind_matrix_config is not None
        assert mind_matrix_config["file"] == "config/topology-mind-matrix.yaml"

    def test_manifest_boot_sequence(self, manifest_path: Path) -> None:
        """Test manifest has proper boot sequence."""
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        boot_sequence = manifest.get("boot_sequence", [])

        # mind_matrix should be last in boot sequence
        assert "mind_matrix" in boot_sequence
        assert boot_sequence[-1] == "mind_matrix"

    def test_manifest_entrypoint(self, manifest_path: Path) -> None:
        """Test manifest has proper entrypoint."""
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)

        entrypoint = manifest.get("entrypoint", {})

        assert entrypoint.get("module") == "runtime.mind_matrix.main"
        assert entrypoint.get("class") == "MindMatrix"
        assert entrypoint.get("method") == "bootstrap"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
