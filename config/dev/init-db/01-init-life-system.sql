-- Life System Database Initialization
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Brain Engine Tables
CREATE TABLE IF NOT EXISTS brain_decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    context JSONB NOT NULL,
    decision JSONB NOT NULL,
    confidence DECIMAL(3,2),
    reasoning TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    executed_at TIMESTAMP,
    success BOOLEAN
);

CREATE TABLE IF NOT EXISTS brain_learning_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pattern_type VARCHAR(100) NOT NULL,
    pattern_data JSONB NOT NULL,
    effectiveness_score DECIMAL(3,2),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Heart Engine Tables
CREATE TABLE IF NOT EXISTS heart_orchestrations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type VARCHAR(100) NOT NULL,
    orchestration_data JSONB NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    brain_decision_id UUID REFERENCES brain_decisions(id),
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS heart_resource_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_id VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    health_status VARCHAR(50) NOT NULL,
    health_data JSONB,
    last_check TIMESTAMP DEFAULT NOW()
);

-- Heartbeat Engine Tables
CREATE TABLE IF NOT EXISTS heartbeat_vitals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    component VARCHAR(100) NOT NULL,
    vital_signs JSONB NOT NULL,
    status VARCHAR(50) NOT NULL,
    recorded_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS heartbeat_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    severity VARCHAR(20) NOT NULL,
    component VARCHAR(100) NOT NULL,
    alert_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    alert_data JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);

-- Consciousness Integration Tables
CREATE TABLE IF NOT EXISTS consciousness_states (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    consciousness_level INTEGER NOT NULL,
    system_health JSONB NOT NULL,
    brain_activity JSONB,
    heart_rhythm JSONB,
    vital_signs JSONB,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_brain_decisions_created_at ON brain_decisions(created_at);
CREATE INDEX IF NOT EXISTS idx_brain_learning_patterns_type ON brain_learning_patterns(pattern_type);
CREATE INDEX IF NOT EXISTS idx_heart_orchestrations_status ON heart_orchestrations(status);
CREATE INDEX IF NOT EXISTS idx_heart_resource_health_type ON heart_resource_health(resource_type);
CREATE INDEX IF NOT EXISTS idx_heartbeat_vitals_component ON heartbeat_vitals(component);
CREATE INDEX IF NOT EXISTS idx_heartbeat_alerts_severity ON heartbeat_alerts(severity);
CREATE INDEX IF NOT EXISTS idx_consciousness_states_recorded_at ON consciousness_states(recorded_at);

COMMIT;
