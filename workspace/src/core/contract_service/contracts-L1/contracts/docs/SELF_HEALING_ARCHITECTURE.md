# Self-Healing Path Validation Architecture

## Overview

This document describes the event-driven self-healing architecture for path validation in the SynergyMesh platform. The system goes beyond simple fallback mechanisms to implement true **structural self-repair** capabilities.

## Core Concepts

### 1. **承襲結構 (Inherited Structure)**

The governance DAG, path boundaries, and normalization strategies are embedded in the system. When failures occur, the system leverages these inherited rules to automatically reconstruct missing structures.

### 2. **短暫策略 (Transient Strategy)**

The self-healing mechanism is not permanent modification but temporary repair logic that activates during anomalous situations, ensuring system continuity.

### 3. **自我修復 (Self-Repair)**

Through fallback, normalize, and DAG reconstruction, missing nodes or truncated structures are completed automatically, preventing system-wide failure.

## Architecture Components

### Event System (`src/events/path-validation-events.ts`)

**Purpose**: Event-driven notification system for path validation lifecycle

**Events**:

- `VALIDATION_FAILED`: Path validation failed
- `STRUCTURE_MISSING`: Directory/file structure is missing
- `STRUCTURE_RECOVERED`: Structure successfully recovered
- `FALLBACK_TRIGGERED`: Fallback mechanism activated
- `DAG_NODE_MISSING`: DAG node is broken/missing
- `DAG_NODE_REBUILT`: DAG node successfully rebuilt
- `SNAPSHOT_CREATED`: Structure snapshot created

**Key Interfaces**:

```typescript
interface PathValidationEvent {
  type: PathValidationEventType;
  timestamp: string;
  source: string;
  data: PathValidationEventData;
}

interface StructureSnapshot {
  id: string;
  timestamp: string;
  pathMappings: Map<string, string>;
  boundaries: { safeRoot: string; allowedPrefixes: string[] };
  dagNodes: Map<string, DAGNodeState>;
}
```

### Self-Healing Path Validator (`src/utils/self-healing-path-validator.ts`)

**Purpose**: Extends PathValidator with automatic recovery capabilities

**Features**:

1. **Structure Snapshots**: Maintains periodic snapshots of valid path states
2. **Automatic Recovery**: Attempts to recover missing structures on validation failure
3. **DAG Tracking**: Tracks path dependencies in a directed acyclic graph
4. **Event-Driven**: Emits and responds to validation events

**Configuration**:

```typescript
interface SelfHealingConfig {
  enableAutoRecovery?: boolean;     // Default: true
  enableSnapshotting?: boolean;     // Default: true
  snapshotInterval?: number;        // Default: 60000ms (1 min)
  maxRecoveryAttempts?: number;     // Default: 3
  dagEnabled?: boolean;             // Default: true
}
```

**Recovery Flow**:

1. Validation attempt fails (ENOENT, path not found)
2. Emit `STRUCTURE_MISSING` event
3. Check current snapshot for path mapping
4. If found in snapshot, attempt to recreate directory structure
5. If not found, try to rebuild from DAG dependencies
6. Retry validation after recovery
7. Emit `STRUCTURE_RECOVERED` event with success status

### Governance Integration (`src/governance/self-healing-integration.ts`)

**Purpose**: Connect self-healing to governance policies and monitoring

**Capabilities**:

1. **Metrics Collection**: Track validation failures, recoveries, success rates
2. **Attestation**: Create SLSA-compliant attestations for self-healing events
3. **Policy Compliance**: Check events against governance policies
4. **Reporting**: Export governance reports with compliance status

**Metrics**:

```typescript
interface SelfHealingMetrics {
  totalValidations: number;
  totalFailures: number;
  totalRecoveries: number;
  successfulRecoveries: number;
  failedRecoveries: number;
  snapshotsCreated: number;
  dagNodesRebuilt: number;
}
```

**Policy Checks**:

- Excessive recovery attempts (>5 in 1 minute)
- Boundary violations
- Recovery failures

### Provenance Service Integration (`src/services/provenance.ts`)

**Updates**:

1. Import self-healing components
2. Use `SelfHealingPathValidator` by default
3. Emit fallback events in catch block
4. Maintain backward compatibility with existing code

## Event Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   File Validation Request                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         SelfHealingPathValidator.validateAndResolvePath     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ├─── Success ──────────────────────────┐
                       │                                       │
                       │                                       ▼
                       │                          ┌──────────────────┐
                       │                          │ Update DAG Node  │
                       │                          │  (status: valid) │
                       │                          └──────────────────┘
                       │
                       ├─── Failure (ENOENT) ────────────────┐
                       │                                      │
                       ▼                                      ▼
          ┌───────────────────────────┐      ┌────────────────────────────┐
          │ Emit VALIDATION_FAILED    │      │ Emit STRUCTURE_MISSING     │
          └───────────┬───────────────┘      └────────────┬───────────────┘
                      │                                   │
                      │                                   ▼
                      │                  ┌────────────────────────────────┐
                      │                  │   Check Recovery Attempts      │
                      │                  │   < maxRecoveryAttempts?       │
                      │                  └────────┬───────────┬───────────┘
                      │                           │           │
                      │                     Yes   │           │  No
                      │                           ▼           ▼
                      │                  ┌─────────────┐  ┌──────────────┐
                      │                  │  Attempt    │  │ Throw Error  │
                      │                  │  Recovery   │  └──────────────┘
                      │                  └──────┬──────┘
                      │                         │
                      │                         ├─── Check Snapshot ────┐
                      │                         │                        │
                      │                         │                        ▼
                      │                         │         ┌──────────────────────┐
                      │                         │         │ Path in Snapshot?    │
                      │                         │         └──────┬───────┬───────┘
                      │                         │                │       │
                      │                         │          Yes   │       │  No
                      │                         │                ▼       ▼
                      │                         │     ┌────────────┐  ┌──────────────┐
                      │                         │     │  Restore   │  │ Create Dir   │
                      │                         │     │  from      │  │  Structure   │
                      │                         │     │  Snapshot  │  └──────────────┘
                      │                         │     └────────────┘
                      │                         │
                      │                         └──── Emit STRUCTURE_RECOVERED
                      │                         │
                      │                         └──── Retry Validation
                      │
                      └─────────────── Governance Integration ────────────┐
                                                                           │
                                                                           ▼
                                              ┌────────────────────────────────────┐
                                              │  SelfHealingGovernanceIntegration  │
                                              │  - Track Metrics                    │
                                              │  - Create Attestations             │
                                              │  - Check Policy Compliance         │
                                              │  - Generate Reports                │
                                              └────────────────────────────────────┘
```

## Usage Examples

> **💡 Executable Examples Available!**
>
> All examples below are available as runnable TypeScript files in `examples/self-healing/`.
> Run them with: `npm run examples:self-healing` or individually with `npm run example:basic`, etc.
>
> See [Examples README](../examples/self-healing/README.md) for details.

### Basic Usage with Self-Healing

**Example File:** `examples/self-healing/01-basic-usage.ts`

```typescript
import { ProvenanceService } from './services/provenance';

// ProvenanceService now uses self-healing by default
const provenanceService = new ProvenanceService();

try {
  // This will automatically attempt recovery if path is missing
  const digest = await provenanceService.generateFileDigest('data/file.txt');
  console.log('File digest:', digest);
} catch (error) {
  console.error('Failed after recovery attempts:', error);
}
```

**Run this example:**

```bash
npm run example:basic
```

### Custom Self-Healing Configuration

**Example File:** `examples/self-healing/02-custom-configuration.ts`

```typescript
import { SelfHealingPathValidator } from './utils/self-healing-path-validator';
import { ProvenanceService } from './services/provenance';

const validator = new SelfHealingPathValidator({
  safeRoot: '/custom/root',
  enableAutoRecovery: true,
  enableSnapshotting: true,
  snapshotInterval: 30000, // 30 seconds
  maxRecoveryAttempts: 5,
  dagEnabled: true,
});

const service = new ProvenanceService(validator);
```

**Run this example:**

```bash
npm run example:config
```

### Monitoring and Governance

**Example File:** `examples/self-healing/03-monitoring-governance.ts`

```typescript
import { selfHealingGovernance } from './governance/self-healing-integration';

// Get current metrics
const metrics = selfHealingGovernance.getMetrics();
console.log('Success rate:', selfHealingGovernance.getSuccessRate());

// Get recent attestations
const attestations = selfHealingGovernance.getAttestations(10);

// Export governance report
const report = selfHealingGovernance.exportGovernanceReport();
console.log(report);
```

**Run this example:**

```bash
npm run example:monitoring
```

### Event Subscription

**Example File:** `examples/self-healing/04-event-subscription.ts`

```typescript
import { pathValidationEvents, PathValidationEventType } from './events/path-validation-events';

// Subscribe to recovery events
pathValidationEvents.on(PathValidationEventType.STRUCTURE_RECOVERED, (event) => {
  console.log('Structure recovered:', event.data.filePath);
  console.log('Recovery successful:', event.data.recoverySuccessful);
});

// Subscribe to fallback events
pathValidationEvents.on(PathValidationEventType.FALLBACK_TRIGGERED, (event) => {
  console.log('Fallback triggered for:', event.data.filePath);
  console.log('Error:', event.data.error);
});
```

**Run this example:**

```bash
npm run example:events
```

### Complete Demo

**Example File:** `examples/self-healing/05-complete-demo.ts`

A comprehensive demonstration showing all features integrated together with real file operations.

**Run this example:**

```bash
npm run example:demo
```

## CI/CD Integration

### Automated Validation in Pipeline

The self-healing system integrates with CI/CD through governance reports:

```yaml
# .github/workflows/self-healing-validation.yml
name: Self-Healing Validation

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Run Self-Healing Tests
        run: npm test -- --testPathPattern=self-healing
      
      - name: Generate Governance Report
        run: npm run governance:self-healing-report
      
      - name: Check Success Rate
        run: |
          RATE=$(node -e "const g = require('./dist/governance/self-healing-integration'); console.log(g.selfHealingGovernance.getSuccessRate());")
          if (( $(echo "$RATE < 0.95" | bc -l) )); then
            echo "Self-healing success rate below threshold: $RATE"
            exit 1
          fi
```

## Governance Policy Integration

Self-healing events are checked against governance policies defined in:

- `governance/40-self-healing/policies/self-healing-policies.yaml`
- `governance/40-self-healing/config/self-healing-framework.yaml`

### Policy Violations

The system tracks and reports:

1. **Excessive recovery attempts**: More than 5 attempts in 1 minute for same path
2. **Boundary violations**: Attempts to access paths outside safe boundaries
3. **Recovery failures**: Failed recovery attempts that exceed threshold

## Benefits

### 1. **避免人為干預 (Avoid Manual Intervention)**

System self-adjusts without human intervention for common path issues.

### 2. **一致性 (Consistency)**

Recovered structures adhere to original governance rules, preventing semantic drift.

### 3. **韌性 (Resilience)**

System doesn't crash on conflicts/corruption, maintains operation through self-repair.

### 4. **可追溯性 (Traceability)**

All recovery events are attested and tracked for audit purposes.

### 5. **治理閉環 (Governance Closed Loop)**

Self-healing is integrated into governance framework, not separate concern.

## Future Enhancements

1. **Multi-level DAG Recovery**: Support complex dependency chains
2. **Predictive Recovery**: Use ML to predict and prevent failures
3. **Distributed Snapshots**: Snapshot synchronization across instances
4. **Recovery Strategies**: Configurable recovery strategies per path pattern
5. **Real-time Dashboard**: Live monitoring of self-healing activities

## Related Documentation

- [Path Validator](../src/utils/path-validator.ts)
- [Provenance Service](../src/services/provenance.ts)
- [Governance Framework](/governance/40-self-healing/README.md)
- [SLSA Attestation](../src/services/attestation.ts)

## Contributing

When adding new self-healing capabilities:

1. Define new event types in `path-validation-events.ts`
2. Implement recovery logic in `self-healing-path-validator.ts`
3. Add governance checks in `self-healing-integration.ts`
4. Update this documentation
5. Add tests in `__tests__/self-healing.test.ts`
