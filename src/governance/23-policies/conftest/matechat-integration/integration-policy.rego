# MateChat Integration Policy for SLASolve
# Defines rules and constraints for integrating AI chat features

package matechat.integration

# Define allowed integration points
allowed_integration_paths := {
    "core/contracts/contracts-L1/ai-chat-service",
    "core/contracts/contracts-L1/input-service",
    "core/contracts/contracts-L1/file-service",
    "mcp-servers/ai-model-integration",
    "advanced-system-src/markdown-renderer",
}

# Security requirements for all integrated components
security_requirements := {
    "authentication": true,
    "encryption": "TLS 1.3",
    "audit_logging": true,
    "slsa_level": 3,
}

# Performance thresholds for drone/autonomous systems
performance_thresholds := {
    "response_time_ms": 2000,
    "max_file_size_mb": 100,
    "concurrent_connections": 1000,
    "message_throughput_per_sec": 500,
}

# Component dependencies validation
allowed_dependencies := {
    "vue": "^3.5.0",
    "typescript": "^5.3.0",
    "express": "^4.21.0",
    "openai": "^4.77.0",
    "zod": "^3.22.0",
}

# Validate integration configuration
deny[msg] {
    input.integration_path
    not allowed_integration_paths[input.integration_path]
    msg := sprintf("Integration path '%s' is not allowed", [input.integration_path])
}

deny[msg] {
    input.response_time_ms > performance_thresholds.response_time_ms
    msg := sprintf("Response time %dms exceeds threshold %dms", [
        input.response_time_ms,
        performance_thresholds.response_time_ms
    ])
}

deny[msg] {
    input.slsa_level < security_requirements.slsa_level
    msg := sprintf("SLSA level %d is below required level %d", [
        input.slsa_level,
        security_requirements.slsa_level
    ])
}

# Validate that authentication is enabled
deny[msg] {
    input.authentication == false
    msg := "Authentication must be enabled for all integrated services"
}

# Allow rule - all checks passed
allow {
    count(deny) == 0
}
