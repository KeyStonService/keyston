#!/usr/bin/env python3
"""
SuperAgent Configuration Management

Centralized configuration using environment variables and Pydantic settings.
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Service Identity
    service_name: str = Field(default="super-agent", env="SERVICE_NAME")
    service_version: str = Field(default="1.0.0", env="SERVICE_VERSION")
    namespace: str = Field(default="axiom-system", env="NAMESPACE")
    pod_name: str = Field(default="super-agent-local", env="POD_NAME")
    pod_ip: str = Field(default="127.0.0.1", env="POD_IP")

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8080, env="PORT")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")  # json or text

    # Agent Communication
    agent_timeout: float = Field(default=30.0, env="AGENT_TIMEOUT")
    agent_retry_attempts: int = Field(default=3, env="AGENT_RETRY_ATTEMPTS")
    agent_retry_delay: float = Field(default=1.0, env="AGENT_RETRY_DELAY")

    # Agent Registry
    monitoring_agent_url: str = Field(
        default="http://monitoring-agent:8080",
        env="MONITORING_AGENT_URL"
    )
    problem_solver_agent_url: str = Field(
        default="http://problem-solver-agent:8080",
        env="PROBLEM_SOLVER_AGENT_URL"
    )
    qa_agent_url: str = Field(
        default="http://qa-agent:8080",
        env="QA_AGENT_URL"
    )
    maintenance_agent_url: str = Field(
        default="http://maintenance-agent:8080",
        env="MAINTENANCE_AGENT_URL"
    )
    learning_agent_url: str = Field(
        default="http://learning-agent:8080",
        env="LEARNING_AGENT_URL"
    )

    # Circuit Breaker
    circuit_breaker_failure_threshold: int = Field(default=5, env="CB_FAILURE_THRESHOLD")
    circuit_breaker_recovery_timeout: float = Field(default=60.0, env="CB_RECOVERY_TIMEOUT")
    circuit_breaker_half_open_requests: int = Field(default=3, env="CB_HALF_OPEN_REQUESTS")

    # Consensus
    consensus_timeout: float = Field(default=30.0, env="CONSENSUS_TIMEOUT")
    consensus_quorum_percentage: float = Field(default=0.5, env="CONSENSUS_QUORUM_PCT")
    consensus_approval_threshold: float = Field(default=0.6, env="CONSENSUS_APPROVAL_THRESHOLD")

    # Event Store
    event_store_type: str = Field(default="memory", env="EVENT_STORE_TYPE")  # memory, sqlite, postgres
    event_store_path: str = Field(default="/var/lib/super-agent/events.db", env="EVENT_STORE_PATH")
    event_store_max_events: int = Field(default=100000, env="EVENT_STORE_MAX_EVENTS")

    # Audit Trail
    audit_enabled: bool = Field(default=True, env="AUDIT_ENABLED")
    audit_retention_days: int = Field(default=90, env="AUDIT_RETENTION_DAYS")

    # Tracing
    trace_enabled: bool = Field(default=True, env="TRACE_ENABLED")
    trace_exporter: str = Field(default="jaeger", env="TRACE_EXPORTER")
    jaeger_endpoint: str = Field(default="http://jaeger:14268/api/traces", env="JAEGER_ENDPOINT")

    # Security
    enable_signature_verification: bool = Field(default=False, env="ENABLE_SIGNATURE_VERIFICATION")
    allowed_agents: List[str] = Field(
        default=[
            "monitoring-agent",
            "problem-solver-agent",
            "qa-agent",
            "maintenance-agent",
            "learning-agent",
            "test-client"
        ],
        env="ALLOWED_AGENTS"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_agent_url(agent_name: str) -> Optional[str]:
    """Get URL for a specific agent."""
    agent_urls = {
        "monitoring-agent": settings.monitoring_agent_url,
        "problem-solver-agent": settings.problem_solver_agent_url,
        "qa-agent": settings.qa_agent_url,
        "maintenance-agent": settings.maintenance_agent_url,
        "learning-agent": settings.learning_agent_url,
    }
    return agent_urls.get(agent_name)
