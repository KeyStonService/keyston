/**
 * Example 4: Event Subscription
 * 
 * Demonstrates how to subscribe to self-healing events
 * and react to validation failures, recoveries, and other events
 */

import { pathValidationEvents, PathValidationEventType } from '../../src/events/path-validation-events';
import { SelfHealingPathValidator } from '../../src/utils/self-healing-path-validator';

async function eventSubscriptionExample() {
  console.log('=== Example 4: Event Subscription ===\n');

  let eventCount = 0;

  // Subscribe to recovery events
  pathValidationEvents.on(PathValidationEventType.STRUCTURE_RECOVERED, (event) => {
    eventCount++;
    console.log('🔄 Structure recovered:');
    console.log('   - File path:', event.data.filePath);
    console.log('   - Recovery successful:', event.data.recoverySuccessful);
    console.log('   - Timestamp:', event.timestamp);
    console.log('   - Source:', event.source);
  });

  // Subscribe to fallback events
  pathValidationEvents.on(PathValidationEventType.FALLBACK_TRIGGERED, (event) => {
    eventCount++;
    console.log('⚠️  Fallback triggered:');
    console.log('   - File path:', event.data.filePath);
    console.log('   - Error:', event.data.error);
    console.log('   - Error code:', event.data.errorCode);
    console.log('   - Timestamp:', event.timestamp);
  });

  // Subscribe to validation failed events
  pathValidationEvents.on(PathValidationEventType.VALIDATION_FAILED, (event) => {
    eventCount++;
    console.log('❌ Validation failed:');
    console.log('   - File path:', event.data.filePath);
    console.log('   - Error:', event.data.error);
    console.log('   - Timestamp:', event.timestamp);
  });

  // Subscribe to structure missing events
  pathValidationEvents.on(PathValidationEventType.STRUCTURE_MISSING, (event) => {
    eventCount++;
    console.log('🔍 Structure missing:');
    console.log('   - File path:', event.data.filePath);
    console.log('   - Safe root:', event.data.safeRoot);
    console.log('   - Timestamp:', event.timestamp);
  });

  // Subscribe to snapshot created events
  pathValidationEvents.on(PathValidationEventType.SNAPSHOT_CREATED, (event) => {
    eventCount++;
    console.log('📸 Snapshot created:');
    console.log('   - Snapshot ID:', event.data.snapshotId);
    console.log('   - Timestamp:', event.timestamp);
  });

  // Subscribe to DAG node events
  pathValidationEvents.on(PathValidationEventType.DAG_NODE_REBUILT, (event) => {
    eventCount++;
    console.log('🔧 DAG node rebuilt:');
    console.log('   - Node ID:', event.data.dagNodeId);
    console.log('   - File path:', event.data.filePath);
    console.log('   - Timestamp:', event.timestamp);
  });

  console.log('✅ Event listeners registered for 6 event types\n');
  console.log('📡 Waiting for events... (simulating with a test)\n');

  // Simulate some events by creating a validator and attempting validation
  const validator = new SelfHealingPathValidator({
    enableAutoRecovery: true,
    enableSnapshotting: false, // Disable periodic snapshots for demo
    dagEnabled: true,
  });

  // Create a snapshot to trigger event
  try {
    await validator.createSnapshot();
  } catch (error) {
    // Ignore errors in demo
  }

  // Clean up
  validator.dispose();

  // Wait a moment for events to process
  await new Promise((resolve) => setTimeout(resolve, 100));

  console.log('\n📊 Total events captured:', eventCount);
  console.log('\n=== Example Complete ===\n');
}

// Run the example if executed directly
if (require.main === module) {
  eventSubscriptionExample()
    .then(() => {
      console.log('Example completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Example failed:', error);
      process.exit(1);
    });
}

export { eventSubscriptionExample };
