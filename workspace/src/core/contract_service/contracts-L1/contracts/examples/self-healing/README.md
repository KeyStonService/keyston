# Self-Healing Path Validation - Examples

This directory contains executable examples demonstrating the self-healing path validation architecture.

## Overview

These examples materialize the concepts described in the [Self-Healing Architecture Documentation](../../docs/SELF_HEALING_ARCHITECTURE.md) into runnable code.

## Examples

### 01. Basic Usage (`01-basic-usage.ts`)

**What it demonstrates:**

- Default self-healing behavior with `ProvenanceService`
- Automatic recovery attempts on validation failures
- Simple file digest generation

**Run:**

```bash
npx tsx examples/self-healing/01-basic-usage.ts
```

### 02. Custom Configuration (`02-custom-configuration.ts`)

**What it demonstrates:**

- Creating a `SelfHealingPathValidator` with custom settings
- Configuring recovery attempts, snapshot intervals, and DAG tracking
- Manual snapshot creation
- Resource cleanup with `dispose()`

**Run:**

```bash
npx tsx examples/self-healing/02-custom-configuration.ts
```

**Key Configuration Options:**

```typescript
{
  safeRoot: string,              // Base directory for file operations
  enableAutoRecovery: boolean,   // Auto-attempt recovery on failures
  enableSnapshotting: boolean,   // Enable periodic snapshots
  snapshotInterval: number,      // Snapshot frequency (ms)
  maxRecoveryAttempts: number,   // Max recovery tries per path
  dagEnabled: boolean            // Enable DAG dependency tracking
}
```

### 03. Monitoring & Governance (`03-monitoring-governance.ts`)

**What it demonstrates:**

- Accessing real-time metrics from governance system
- Retrieving attestations for audit
- Calculating success rates
- Exporting governance reports

**Run:**

```bash
npx tsx examples/self-healing/03-monitoring-governance.ts
```

**Metrics Available:**

- Total validations and failures
- Recovery success/failure counts
- Snapshot and DAG node statistics
- Success rate percentage

### 04. Event Subscription (`04-event-subscription.ts`)

**What it demonstrates:**

- Subscribing to 6 different event types
- Reacting to validation lifecycle events
- Custom event handling logic
- Event-driven monitoring

**Run:**

```bash
npx tsx examples/self-healing/04-event-subscription.ts
```

**Event Types:**

- `VALIDATION_FAILED` - Path validation failed
- `STRUCTURE_MISSING` - Directory/file structure missing
- `STRUCTURE_RECOVERED` - Structure successfully recovered
- `FALLBACK_TRIGGERED` - Fallback mechanism activated
- `SNAPSHOT_CREATED` - Structure snapshot created
- `DAG_NODE_REBUILT` - DAG node successfully rebuilt

### 05. Complete Demo (`05-complete-demo.ts`)

**What it demonstrates:**

- End-to-end self-healing workflow
- All features integrated together
- Real file operations in temp directory
- Event tracking and metrics collection

**Run:**

```bash
npx tsx examples/self-healing/05-complete-demo.ts
```

**Demo Steps:**

1. Setup event listeners
2. Configure self-healing validator
3. Create test files
4. Validate existing files
5. Create structure snapshot
6. Test auto-recovery
7. ProvenanceService integration
8. Review governance metrics
9. Summarize captured events
10. Cleanup and verification

## Running All Examples

Run all examples sequentially:

```bash
npm run examples:self-healing
```

Or run them individually with tsx:

```bash
npx tsx examples/self-healing/01-basic-usage.ts
npx tsx examples/self-healing/02-custom-configuration.ts
npx tsx examples/self-healing/03-monitoring-governance.ts
npx tsx examples/self-healing/04-event-subscription.ts
npx tsx examples/self-healing/05-complete-demo.ts
```

## Expected Output

Each example produces console output showing:

- ✅ Successful operations
- ❌ Expected failures
- 📊 Metrics and statistics
- 🔄 Recovery attempts
- 📸 Snapshot creation
- 📡 Event notifications

## Integration with Tests

These examples complement the test suite in `src/__tests__/self-healing/`:

- **Tests**: Verify correctness and behavior
- **Examples**: Demonstrate usage and integration

## Architecture Overview

```
┌─────────────────────────────────────────┐
│   ProvenanceService (Default)           │
│   └── SelfHealingPathValidator          │
│       ├── Event Emitter (8 event types) │
│       ├── Structure Snapshots            │
│       ├── DAG Tracking                   │
│       └── Auto-Recovery                  │
└─────────────────────────────────────────┘
                     │
                     ├── Events ──▶ Event Subscribers
                     │
                     └── Metrics ──▶ Governance Integration
                                         └── Attestations
```

## Core Principles

### 1. 承襲結構 (Inherited Structure)

System uses existing governance DAG and rules to auto-complete missing structures.

### 2. 短暫策略 (Transient Strategy)

Temporary repair logic activated during anomalous situations.

### 3. 自我修復 (Self-Repair)

Automatic completion via fallback + normalize + DAG rebuild.

## Related Documentation

- [Self-Healing Architecture](../../docs/SELF_HEALING_ARCHITECTURE.md)
- [Implementation Summary](../../docs/SELF_HEALING_IMPLEMENTATION_SUMMARY.md)
- [Governance Policy](../../../../../governance/40-self-healing/policies/path-validation-self-healing.yaml)

## Troubleshooting

### Example fails with "module not found"

Make sure to build the project first:

```bash
npm run build
```

### Permission errors

Examples create files in temp directory. Ensure you have write permissions to `/tmp` or `%TEMP%`.

### Event listeners not firing

Check that event system is properly initialized before validation attempts.

## Contributing

When adding new examples:

1. Follow the existing naming pattern (`NN-description.ts`)
2. Include clear documentation at the top
3. Add entry to this README
4. Ensure example can run standalone
5. Include cleanup logic to avoid leaving test files

## License

MIT License - See root LICENSE file
