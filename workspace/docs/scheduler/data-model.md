# Scheduler Service Data Model

## Overview

This document describes the data model for the Scheduler Service, including database schema, relationships, and usage patterns.

## Entity Relationship Diagram

```
┌────────────────┐
│     jobs       │
│────────────────│
│ id (PK)        │◄──────────┐
│ name           │            │
│ type           │            │
│ cron_expression│            │
│ handler        │            │
│ payload        │            │
│ priority       │            │
│ status         │            │
│ ...            │            │
└────────────────┘            │
        │                     │
        │ 1:N                 │
        │                     │
        ▼                     │
┌────────────────┐            │
│job_executions  │            │
│────────────────│            │
│ id (PK)        │            │
│ job_id (FK)────┼────────────┘
│ status         │
│ started_at     │
│ duration_ms    │
│ result         │
│ error          │
│ ...            │
└────────────────┘

┌────────────────┐            ┌────────────────┐
│job_dependencies│            │   job_tags     │
│────────────────│            │────────────────│
│ id (PK)        │            │ id (PK)        │
│ job_id (FK)────┼───────┐    │ job_id (FK)────┼───┐
│ depends_on_job │       │    │ tag            │   │
│ ...            │       │    │ ...            │   │
└────────────────┘       │    └────────────────┘   │
                         │                          │
                         │                          │
                         │                          │
                  ┌──────▼────────┐                 │
                  │     jobs      │◄────────────────┘
                  │               │
                  └───────────────┘

┌────────────────┐
│  job_alerts    │
│────────────────│
│ id (PK)        │
│ job_id (FK)────┼───────►jobs
│ alert_type     │
│ condition      │
│ channels       │
│ ...            │
└────────────────┘
```

## Core Entities

### 1. Jobs Table

**Purpose**: Stores job definitions and scheduling configuration

**Schema**:

```sql
CREATE TABLE jobs (
    id UUID PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL,  -- 'cron', 'one-time', 'interval'
    
    -- Schedule
    cron_expression VARCHAR(100),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    interval_ms INTEGER,
    timezone VARCHAR(100) DEFAULT 'UTC',
    
    -- Configuration
    handler VARCHAR(255) NOT NULL,
    payload JSONB,
    priority VARCHAR(20) DEFAULT 'normal',
    
    -- Retry
    max_retries INTEGER DEFAULT 3,
    retry_delay_ms INTEGER DEFAULT 1000,
    retry_strategy VARCHAR(50) DEFAULT 'exponential',
    
    -- Limits
    timeout_ms INTEGER DEFAULT 300000,
    max_concurrent INTEGER DEFAULT 1,
    
    -- State
    status VARCHAR(50) DEFAULT 'active',
    enabled BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE
);
```

**Job Types**:

- `cron`: Recurring jobs with cron expression (e.g., "0 2 ** *")
- `one-time`: Jobs scheduled for a specific time
- `interval`: Recurring jobs at fixed intervals (e.g., every 5 minutes)

**Priority Levels**:

- `critical`: P0 - Must execute immediately
- `high`: P1 - Execute before normal jobs
- `normal`: P2 - Standard priority
- `low`: P3 - Execute when resources available

**Status Values**:

- `active`: Job is enabled and scheduled
- `paused`: Job is temporarily disabled
- `completed`: One-time job has finished
- `cancelled`: Job was cancelled
- `failed`: Job failed permanently

**Example**:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "daily-backup",
  "description": "Backup database daily at 2 AM",
  "type": "cron",
  "cron_expression": "0 2 * * *",
  "timezone": "UTC",
  "handler": "backupHandler",
  "payload": {
    "database": "production",
    "includeIndexes": true
  },
  "priority": "high",
  "max_retries": 3,
  "retry_strategy": "exponential",
  "status": "active",
  "enabled": true
}
```

### 2. Job Executions Table

**Purpose**: Stores execution history and results

**Schema**:

```sql
CREATE TABLE job_executions (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES jobs(id),
    
    status VARCHAR(50) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER,
    
    attempt_number INTEGER DEFAULT 1,
    is_retry BOOLEAN DEFAULT FALSE,
    
    result JSONB,
    error TEXT,
    error_stack TEXT,
    
    cpu_usage DECIMAL(5,2),
    memory_usage_mb DECIMAL(10,2),
    
    worker_id VARCHAR(255),
    worker_host VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Execution Status**:

- `pending`: Queued for execution
- `running`: Currently executing
- `completed`: Finished successfully
- `failed`: Failed with error
- `timeout`: Exceeded timeout
- `cancelled`: Manually cancelled

**Example**:

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "started_at": "2026-01-15T02:00:00Z",
  "completed_at": "2026-01-15T02:05:23Z",
  "duration_ms": 323000,
  "attempt_number": 1,
  "is_retry": false,
  "result": {
    "backupSize": "2.3GB",
    "filesBackedUp": 1234,
    "checksum": "abc123"
  },
  "cpu_usage": 45.2,
  "memory_usage_mb": 512.5,
  "worker_id": "worker-01",
  "worker_host": "10.0.1.42"
}
```

### 3. Job Dependencies Table

**Purpose**: Define job chains and dependencies

**Schema**:

```sql
CREATE TABLE job_dependencies (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES jobs(id),
    depends_on_job_id UUID NOT NULL REFERENCES jobs(id),
    
    wait_for_completion BOOLEAN DEFAULT TRUE,
    required BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_dependency UNIQUE (job_id, depends_on_job_id),
    CONSTRAINT no_self_dependency CHECK (job_id != depends_on_job_id)
);
```

**Dependency Types**:

- `wait_for_completion`: Wait for dependency to finish before starting
- `required`: Fail if dependency fails

**Example - Job Chain**:

```
backup-db → verify-backup → upload-to-s3
```

```json
[
  {
    "job_id": "verify-backup-job-id",
    "depends_on_job_id": "backup-db-job-id",
    "wait_for_completion": true,
    "required": true
  },
  {
    "job_id": "upload-to-s3-job-id",
    "depends_on_job_id": "verify-backup-job-id",
    "wait_for_completion": true,
    "required": true
  }
]
```

### 4. Job Tags Table

**Purpose**: Categorize and filter jobs

**Schema**:

```sql
CREATE TABLE job_tags (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES jobs(id),
    tag VARCHAR(100) NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_job_tag UNIQUE (job_id, tag)
);
```

**Common Tags**:

- `backup`, `maintenance`, `report`, `cleanup`
- `production`, `staging`, `development`
- `critical`, `monitored`, `external`

**Example**:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "tags": ["backup", "production", "critical", "daily"]
}
```

### 5. Job Alerts Table

**Purpose**: Configure monitoring and notifications

**Schema**:

```sql
CREATE TABLE job_alerts (
    id UUID PRIMARY KEY,
    job_id UUID NOT NULL REFERENCES jobs(id),
    
    alert_type VARCHAR(50) NOT NULL,
    condition JSONB NOT NULL,
    
    channels TEXT[] DEFAULT ARRAY['dashboard'],
    recipients TEXT[],
    webhook_url VARCHAR(500),
    
    enabled BOOLEAN DEFAULT TRUE,
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    trigger_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

**Alert Types**:

- `failure`: Job execution failed
- `timeout`: Job exceeded timeout
- `retry`: Job is being retried
- `success`: Job completed successfully
- `duration`: Job took longer than expected

**Example**:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "alert_type": "failure",
  "condition": {
    "consecutive_failures": 3
  },
  "channels": ["email", "slack", "dashboard"],
  "recipients": ["ops@example.com"],
  "webhook_url": "https://hooks.slack.com/services/...",
  "enabled": true
}
```

## Indexes

### Performance Indexes

```sql
-- Jobs queries
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_next_run_at ON jobs(next_run_at) 
  WHERE status = 'active' AND enabled = TRUE;
CREATE INDEX idx_jobs_priority ON jobs(priority);

-- Executions queries
CREATE INDEX idx_job_executions_job_id ON job_executions(job_id);
CREATE INDEX idx_job_executions_status ON job_executions(status);
CREATE INDEX idx_job_executions_job_started ON job_executions(job_id, started_at DESC);

-- Tags queries
CREATE INDEX idx_job_tags_tag ON job_tags(tag);

-- Dependencies queries
CREATE INDEX idx_job_dependencies_job_id ON job_dependencies(job_id);
CREATE INDEX idx_job_dependencies_depends_on ON job_dependencies(depends_on_job_id);
```

## Views

### Active Jobs View

```sql
CREATE VIEW active_jobs AS
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
```

### Failed Jobs View

```sql
CREATE VIEW failed_jobs AS
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
```

## Data Retention

### Execution History

- **Default retention**: 90 days
- **Max per job**: 1000 most recent executions
- **Cleanup function**: `cleanup_old_executions()`

```sql
-- Run cleanup (e.g., daily via cron)
SELECT cleanup_old_executions(retention_days := 90, max_per_job := 1000);
```

## Common Query Patterns

### 1. Get Jobs Due for Execution

```sql
SELECT * FROM jobs
WHERE status = 'active'
  AND enabled = TRUE
  AND next_run_at <= CURRENT_TIMESTAMP
ORDER BY priority DESC, next_run_at ASC
LIMIT 100;
```

### 2. Get Job Execution History

```sql
SELECT 
    je.*,
    j.name,
    j.priority
FROM job_executions je
INNER JOIN jobs j ON je.job_id = j.id
WHERE je.job_id = $1
ORDER BY je.started_at DESC
LIMIT 100;
```

### 3. Get Jobs by Tag

```sql
SELECT DISTINCT j.*
FROM jobs j
INNER JOIN job_tags jt ON j.id = jt.job_id
WHERE jt.tag = $1
  AND j.status = 'active';
```

### 4. Get Job Dependencies

```sql
WITH RECURSIVE job_chain AS (
    -- Base case: start with the job
    SELECT 
        j.id,
        j.name,
        0 as depth
    FROM jobs j
    WHERE j.id = $1
    
    UNION ALL
    
    -- Recursive case: find dependencies
    SELECT 
        j.id,
        j.name,
        jc.depth + 1
    FROM jobs j
    INNER JOIN job_dependencies jd ON j.id = jd.depends_on_job_id
    INNER JOIN job_chain jc ON jd.job_id = jc.id
)
SELECT * FROM job_chain
ORDER BY depth;
```

### 5. Get Job Performance Metrics

```sql
SELECT 
    j.name,
    j.priority,
    COUNT(je.id) as total_runs,
    COUNT(je.id) FILTER (WHERE je.status = 'completed') as successful_runs,
    COUNT(je.id) FILTER (WHERE je.status = 'failed') as failed_runs,
    AVG(je.duration_ms) as avg_duration,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY je.duration_ms) as p95_duration,
    MAX(je.duration_ms) as max_duration
FROM jobs j
LEFT JOIN job_executions je ON j.id = je.job_id
WHERE je.started_at > CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY j.id, j.name, j.priority
ORDER BY failed_runs DESC, avg_duration DESC;
```

## Data Migration Strategy

### Phase 1 (Current)

- In-memory job storage (BullMQ + Redis)
- No persistent database

### Phase 2 (Q2 2026)

- Migrate to PostgreSQL for job definitions
- Keep Redis for job queue
- Implement migrations (001_create_jobs_table.sql)

### Phase 3 (Q3 2026)

- Add audit logging
- Implement job versioning
- Add collaborative features

## Performance Considerations

### Write Optimization

- Use prepared statements
- Batch inserts for executions
- Async writes for non-critical data

### Read Optimization

- Index on commonly queried fields
- Materialized views for analytics
- Connection pooling

### Scaling Strategy

- Horizontal scaling with read replicas
- Partition executions table by date
- Archive old executions to cold storage

## Security

### Access Control

- Row-level security by created_by
- Role-based access (admin, operator, viewer)
- Audit trail for all modifications

### Data Protection

- Encrypt sensitive payloads
- Sanitize errors before storing
- Redact PII in logs

## Backup & Recovery

### Backup Strategy

- Daily full backups
- Hourly incremental backups
- Point-in-time recovery enabled

### Recovery Plan

- RPO: 1 hour
- RTO: 15 minutes
- Automated failover

## Monitoring

### Key Metrics

- Job execution rate
- Success/failure ratio
- Average execution time
- Queue depth
- Worker utilization

### Alerts

- Failed job threshold exceeded
- Long-running jobs
- Queue backlog
- Database performance

## Future Enhancements

### Phase 2

- Job versioning
- Workflow DAGs
- Conditional execution
- Job templates

### Phase 3

- Multi-tenant support
- Job marketplace
- Visual workflow editor
- Advanced analytics
