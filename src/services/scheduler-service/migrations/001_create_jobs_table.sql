-- Migration: 001_create_jobs_table
-- Description: Create database schema for scheduler service
-- Phase: 2 (Q2 2026) - Pre-designed for distributed deployment
-- Author: System
-- Date: 2025-12-16

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Jobs table - stores job definitions
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL CHECK (type IN ('cron', 'one-time', 'interval')),
    
    -- Schedule configuration
    cron_expression VARCHAR(100),  -- For cron jobs
    scheduled_at TIMESTAMP WITH TIME ZONE,  -- For one-time jobs
    interval_ms INTEGER,  -- For interval jobs (milliseconds)
    timezone VARCHAR(100) DEFAULT 'UTC',
    
    -- Job configuration
    handler VARCHAR(255) NOT NULL,  -- Function/handler to execute
    payload JSONB,  -- Job parameters
    priority VARCHAR(20) DEFAULT 'normal' CHECK (priority IN ('critical', 'high', 'normal', 'low')),
    
    -- Retry configuration
    max_retries INTEGER DEFAULT 3,
    retry_delay_ms INTEGER DEFAULT 1000,
    retry_strategy VARCHAR(50) DEFAULT 'exponential' CHECK (retry_strategy IN ('fixed', 'exponential', 'linear')),
    
    -- Execution limits
    timeout_ms INTEGER DEFAULT 300000,  -- 5 minutes default
    max_concurrent INTEGER DEFAULT 1,
    
    -- State
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'paused', 'completed', 'cancelled', 'failed')),
    enabled BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes for common queries
    CONSTRAINT unique_job_name UNIQUE (name)
);

-- Job executions table - stores execution history
CREATE TABLE IF NOT EXISTS job_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Execution details
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'running', 'completed', 'failed', 'timeout', 'cancelled')),
    started_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    -- Retry information
    attempt_number INTEGER DEFAULT 1,
    is_retry BOOLEAN DEFAULT FALSE,
    
    -- Results
    result JSONB,  -- Success result data
    error TEXT,  -- Error message if failed
    error_stack TEXT,  -- Stack trace
    
    -- Resource usage (for analytics)
    cpu_usage DECIMAL(5,2),
    memory_usage_mb DECIMAL(10,2),
    
    -- Worker information
    worker_id VARCHAR(255),
    worker_host VARCHAR(255),
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Job dependencies table - for job chains
CREATE TABLE IF NOT EXISTS job_dependencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    depends_on_job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Dependency configuration
    wait_for_completion BOOLEAN DEFAULT TRUE,
    required BOOLEAN DEFAULT TRUE,  -- Job fails if dependency fails
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_dependency UNIQUE (job_id, depends_on_job_id),
    CONSTRAINT no_self_dependency CHECK (job_id != depends_on_job_id)
);

-- Job tags table - for categorization and filtering
CREATE TABLE IF NOT EXISTS job_tags (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    tag VARCHAR(100) NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_job_tag UNIQUE (job_id, tag)
);

-- Job alerts table - for monitoring and notifications
CREATE TABLE IF NOT EXISTS job_alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    
    -- Alert configuration
    alert_type VARCHAR(50) NOT NULL CHECK (alert_type IN ('failure', 'timeout', 'retry', 'success', 'duration')),
    condition JSONB NOT NULL,  -- Alert trigger condition
    
    -- Notification settings
    channels TEXT[] DEFAULT ARRAY['dashboard'],  -- email, slack, dashboard, webhook
    recipients TEXT[],
    webhook_url VARCHAR(500),
    
    -- State
    enabled BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_type ON jobs(type);
CREATE INDEX idx_jobs_next_run_at ON jobs(next_run_at) WHERE status = 'active' AND enabled = TRUE;
CREATE INDEX idx_jobs_created_at ON jobs(created_at);
CREATE INDEX idx_jobs_priority ON jobs(priority);

CREATE INDEX idx_job_executions_job_id ON job_executions(job_id);
CREATE INDEX idx_job_executions_status ON job_executions(status);
CREATE INDEX idx_job_executions_started_at ON job_executions(started_at);
CREATE INDEX idx_job_executions_job_started ON job_executions(job_id, started_at DESC);

CREATE INDEX idx_job_dependencies_job_id ON job_dependencies(job_id);
CREATE INDEX idx_job_dependencies_depends_on ON job_dependencies(depends_on_job_id);

CREATE INDEX idx_job_tags_job_id ON job_tags(job_id);
CREATE INDEX idx_job_tags_tag ON job_tags(tag);

CREATE INDEX idx_job_alerts_job_id ON job_alerts(job_id);
CREATE INDEX idx_job_alerts_enabled ON job_alerts(enabled) WHERE enabled = TRUE;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_jobs_updated_at BEFORE UPDATE ON jobs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_job_alerts_updated_at BEFORE UPDATE ON job_alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to calculate next run time for cron jobs
CREATE OR REPLACE FUNCTION calculate_next_run(
    p_cron_expression VARCHAR,
    p_timezone VARCHAR,
    p_from_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
)
RETURNS TIMESTAMP WITH TIME ZONE AS $$
-- Note: This is a placeholder. In production, use a proper cron parser
-- or call the application layer to calculate the next run time
DECLARE
    next_run TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Simplified logic - in production, implement full cron parsing
    -- For now, return 1 hour from now as a placeholder
    next_run := p_from_time + INTERVAL '1 hour';
    RETURN next_run AT TIME ZONE p_timezone;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old execution history
CREATE OR REPLACE FUNCTION cleanup_old_executions(
    p_retention_days INTEGER DEFAULT 90,
    p_max_per_job INTEGER DEFAULT 1000
)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete executions older than retention period
    WITH old_executions AS (
        DELETE FROM job_executions
        WHERE started_at < CURRENT_TIMESTAMP - (p_retention_days || ' days')::INTERVAL
        RETURNING id
    )
    SELECT COUNT(*) INTO deleted_count FROM old_executions;
    
    -- Keep only the most recent N executions per job
    WITH ranked_executions AS (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY job_id ORDER BY started_at DESC) as rn
        FROM job_executions
    ),
    excess_executions AS (
        DELETE FROM job_executions
        WHERE id IN (SELECT id FROM ranked_executions WHERE rn > p_max_per_job)
        RETURNING id
    )
    SELECT deleted_count + COUNT(*) INTO deleted_count FROM excess_executions;
    
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Views for common queries

-- Active jobs view
CREATE OR REPLACE VIEW active_jobs AS
SELECT 
    j.*,
    COUNT(je.id) as total_executions,
    COUNT(je.id) FILTER (WHERE je.status = 'completed') as successful_executions,
    COUNT(je.id) FILTER (WHERE je.status = 'failed') as failed_executions,
    AVG(je.duration_ms) FILTER (WHERE je.status = 'completed') as avg_duration_ms
FROM jobs j
LEFT JOIN job_executions je ON j.id = je.job_id
WHERE j.status = 'active' AND j.enabled = TRUE
GROUP BY j.id;

-- Recent executions view
CREATE OR REPLACE VIEW recent_executions AS
SELECT 
    je.*,
    j.name as job_name,
    j.type as job_type,
    j.priority as job_priority
FROM job_executions je
INNER JOIN jobs j ON je.job_id = j.id
ORDER BY je.started_at DESC
LIMIT 100;

-- Failed jobs view
CREATE OR REPLACE VIEW failed_jobs AS
SELECT 
    j.*,
    COUNT(je.id) as failure_count,
    MAX(je.completed_at) as last_failure_at,
    STRING_AGG(DISTINCT je.error, '; ') as recent_errors
FROM jobs j
INNER JOIN job_executions je ON j.id = je.job_id
WHERE je.status = 'failed' 
    AND je.started_at > CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY j.id
HAVING COUNT(je.id) > 0;

-- Comments for documentation
COMMENT ON TABLE jobs IS 'Stores job definitions and configuration for the scheduler service';
COMMENT ON TABLE job_executions IS 'Stores execution history for all jobs';
COMMENT ON TABLE job_dependencies IS 'Defines dependencies between jobs for job chains';
COMMENT ON TABLE job_tags IS 'Tags for categorizing and filtering jobs';
COMMENT ON TABLE job_alerts IS 'Alert configurations for job monitoring';

COMMENT ON COLUMN jobs.handler IS 'The function or handler name to execute for this job';
COMMENT ON COLUMN jobs.payload IS 'JSON payload containing job parameters';
COMMENT ON COLUMN jobs.max_concurrent IS 'Maximum number of concurrent executions allowed';
COMMENT ON COLUMN job_executions.worker_id IS 'Identifier of the worker that executed this job';
COMMENT ON COLUMN job_dependencies.required IS 'If true, job fails when dependency fails';

-- Grant permissions (adjust based on your user setup)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO scheduler_service;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO scheduler_service;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO scheduler_service;
