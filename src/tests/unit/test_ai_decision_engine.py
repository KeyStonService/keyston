"""
AI Decision Engine Integration Tests
AI 決策引擎整合測試

Tests for verifying the AI Decision Engine core functionality.
"""

from __future__ import annotations

import pytest  # type: ignore[import-not-found]

from core.ai_decision_engine import (
    AIDecisionEngine,
    ConfidenceLevel,
    DecisionContext,
    DecisionOption,
    DecisionPriority,
    DecisionType,
)


@pytest.fixture
def engine() -> AIDecisionEngine:
    """Create a fresh AI Decision Engine instance."""
    return AIDecisionEngine()


@pytest.fixture
def sample_context() -> DecisionContext:
    """Create a sample decision context."""
    return DecisionContext(
        context_id="test-ctx-001",
        domain="deployment",
        current_state={
            "environment": "staging",
            "load": 0.5,
            "error_rate": 0.01,
            "success_rate": 0.99,
        },
        historical_data=[
            {"timestamp": "2025-01-01", "action": "deploy", "success": True},
        ],
        constraints=["max_downtime_5min", "require_rollback"],
        objectives=["minimize_risk", "maximize_uptime"],
    )


@pytest.fixture
def sample_options() -> list[DecisionOption]:
    """Create sample decision options."""
    return [
        DecisionOption(
            option_id="opt-1",
            name="Blue-Green Deployment",
            description="Deploy using blue-green strategy",
            expected_outcome={"downtime": 0, "risk": "low"},
            risk_score=0.2,
            benefit_score=0.9,
            confidence=0.85,
            prerequisites=["require_rollback"],
        ),
        DecisionOption(
            option_id="opt-2",
            name="Rolling Update",
            description="Deploy using rolling update",
            expected_outcome={"downtime": 30, "risk": "medium"},
            risk_score=0.4,
            benefit_score=0.7,
            confidence=0.75,
            prerequisites=[],
        ),
        DecisionOption(
            option_id="opt-3",
            name="Canary Deployment",
            description="Deploy using canary strategy",
            expected_outcome={"downtime": 0, "risk": "low"},
            risk_score=0.15,
            benefit_score=0.85,
            confidence=0.8,
            prerequisites=["canary_infra"],
        ),
    ]


class TestAIDecisionEngine:
    """Tests for AI Decision Engine."""

    @pytest.mark.asyncio
    async def test_engine_initialization(self, engine: AIDecisionEngine) -> None:
        """Test engine initializes correctly."""
        assert engine is not None
        assert engine.stats["decisions_made"] == 0
        assert engine.stats["predictions_made"] == 0
        assert engine.config["min_confidence_threshold"] == 0.5

    @pytest.mark.asyncio
    async def test_make_decision_selects_best_option(
        self,
        engine: AIDecisionEngine,
        sample_context: DecisionContext,
        sample_options: list[DecisionOption],
    ) -> None:
        """Test that decision making selects the best option."""
        decision = await engine.make_decision(
            context=sample_context,
            options=sample_options,
            decision_type=DecisionType.OPERATIONAL,
            priority=DecisionPriority.HIGH,
        )

        assert decision is not None
        assert decision.decision_id.startswith("dec-")
        assert decision.selected_option is not None
        # Blue-Green should be selected (highest composite score)
        assert decision.selected_option.name == "Blue-Green Deployment"
        assert decision.confidence_level in [
            ConfidenceLevel.HIGH,
            ConfidenceLevel.VERY_HIGH,
        ]

    @pytest.mark.asyncio
    async def test_decision_includes_alternatives(
        self,
        engine: AIDecisionEngine,
        sample_context: DecisionContext,
        sample_options: list[DecisionOption],
    ) -> None:
        """Test that decision includes alternative options."""
        decision = await engine.make_decision(
            context=sample_context,
            options=sample_options,
            decision_type=DecisionType.TACTICAL,
        )

        assert len(decision.alternatives) > 0
        assert len(decision.alternatives) <= engine.config["max_alternatives"]

    @pytest.mark.asyncio
    async def test_decision_generates_reasoning(
        self,
        engine: AIDecisionEngine,
        sample_context: DecisionContext,
        sample_options: list[DecisionOption],
    ) -> None:
        """Test that decision includes human-readable reasoning."""
        decision = await engine.make_decision(
            context=sample_context,
            options=sample_options,
        )

        assert decision.reasoning != ""
        assert "Selected" in decision.reasoning
        assert "Benefit score" in decision.reasoning

    @pytest.mark.asyncio
    async def test_empty_options_returns_fallback(
        self,
        engine: AIDecisionEngine,
        sample_context: DecisionContext,
    ) -> None:
        """Test fallback decision when no options available."""
        decision = await engine.make_decision(
            context=sample_context,
            options=[],
        )

        assert decision.selected_option.name == "No Action"
        assert decision.confidence_level == ConfidenceLevel.UNCERTAIN

    @pytest.mark.asyncio
    async def test_decision_updates_statistics(
        self,
        engine: AIDecisionEngine,
        sample_context: DecisionContext,
        sample_options: list[DecisionOption],
    ) -> None:
        """Test that making decisions updates statistics."""
        initial_count = engine.stats["decisions_made"]

        await engine.make_decision(context=sample_context, options=sample_options)

        assert engine.stats["decisions_made"] == initial_count + 1

    @pytest.mark.asyncio
    async def test_prediction_outcome(self, engine: AIDecisionEngine) -> None:
        """Test prediction functionality."""
        current_state = {
            "cpu_usage": 0.4,
            "memory_usage": 0.6,
            "error_rate": 0.02,
            "success_rate": 0.98,
        }

        prediction = await engine.predict_outcome(
            current_state=current_state,
            prediction_type="system_health",
            horizon="short_term",
        )

        assert prediction is not None
        assert prediction.prediction_id.startswith("pred-")
        assert 0.0 <= prediction.probability <= 1.0
        assert len(prediction.recommendations) > 0

    @pytest.mark.asyncio
    async def test_record_outcome_updates_learning(
        self,
        engine: AIDecisionEngine,
        sample_context: DecisionContext,
        sample_options: list[DecisionOption],
    ) -> None:
        """Test that recording outcomes updates learning patterns."""
        decision = await engine.make_decision(context=sample_context, options=sample_options)

        engine.record_outcome(
            decision_id=decision.decision_id,
            success=True,
            outcome_data={"latency_improvement": 0.2},
        )

        assert engine.stats["successful_decisions"] >= 1

    @pytest.mark.asyncio
    async def test_get_statistics(
        self,
        engine: AIDecisionEngine,
        sample_context: DecisionContext,
        sample_options: list[DecisionOption],
    ) -> None:
        """Test statistics retrieval."""
        await engine.make_decision(context=sample_context, options=sample_options)
        await engine.predict_outcome(current_state={"load": 0.5}, prediction_type="capacity")

        stats = engine.get_statistics()

        assert stats["decisions_made"] >= 1
        assert stats["predictions_made"] >= 1
        assert "success_rate" in stats
        assert "domains_learned" in stats

    @pytest.mark.asyncio
    async def test_get_decision_history(
        self,
        engine: AIDecisionEngine,
        sample_context: DecisionContext,
        sample_options: list[DecisionOption],
    ) -> None:
        """Test decision history retrieval."""
        await engine.make_decision(
            context=sample_context,
            options=sample_options,
            decision_type=DecisionType.STRATEGIC,
        )

        history = engine.get_decision_history(limit=5, decision_type=DecisionType.STRATEGIC)

        assert len(history) >= 1
        assert history[0]["type"] == "strategic"

    @pytest.mark.asyncio
    async def test_prerequisite_checking(
        self,
        engine: AIDecisionEngine,
        sample_context: DecisionContext,
        sample_options: list[DecisionOption],
    ) -> None:
        """Test that prerequisites affect option scoring."""
        # Canary option requires 'canary_infra' which is not in constraints
        decision = await engine.make_decision(context=sample_context, options=sample_options)

        # Canary should be penalized for unmet prerequisites
        canary_option = next(
            (
                opt
                for opt in [decision.selected_option] + decision.alternatives
                if opt.name == "Canary Deployment"
            ),
            None,
        )

        if canary_option:
            # Should not be selected as best due to prerequisite
            assert (
                decision.selected_option.name != "Canary Deployment"
                or decision.selected_option.confidence < 0.8
            )


class TestConfidenceLevels:
    """Tests for confidence level calculations."""

    def test_very_high_confidence(self, engine: AIDecisionEngine) -> None:
        """Test very high confidence level."""
        level = engine._calculate_confidence_level(0.95)
        assert level == ConfidenceLevel.VERY_HIGH

    def test_high_confidence(self, engine: AIDecisionEngine) -> None:
        """Test high confidence level."""
        level = engine._calculate_confidence_level(0.8)
        assert level == ConfidenceLevel.HIGH

    def test_medium_confidence(self, engine: AIDecisionEngine) -> None:
        """Test medium confidence level."""
        level = engine._calculate_confidence_level(0.6)
        assert level == ConfidenceLevel.MEDIUM

    def test_low_confidence(self, engine: AIDecisionEngine) -> None:
        """Test low confidence level."""
        level = engine._calculate_confidence_level(0.3)
        assert level == ConfidenceLevel.LOW

    def test_uncertain_confidence(self, engine: AIDecisionEngine) -> None:
        """Test uncertain confidence level."""
        level = engine._calculate_confidence_level(0.2)
        assert level == ConfidenceLevel.UNCERTAIN


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
