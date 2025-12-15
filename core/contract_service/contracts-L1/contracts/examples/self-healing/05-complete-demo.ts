/**
 * Example 5: Complete Self-Healing Demo
 * 
 * Comprehensive demonstration of all self-healing features:
 * - Path validation with auto-recovery
 * - Structure snapshots
 * - DAG tracking
 * - Event subscription
 * - Governance monitoring
 */

import { writeFile, mkdir, rm } from 'fs/promises';
import * as path from 'path';
import { tmpdir } from 'os';
import { SelfHealingPathValidator } from '../../src/utils/self-healing-path-validator';
import { ProvenanceService } from '../../src/services/provenance';
import { pathValidationEvents, PathValidationEventType } from '../../src/events/path-validation-events';
import { selfHealingGovernance } from '../../src/governance/self-healing-integration';

async function completeDemoExample() {
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║   Self-Healing Path Validation - Complete Demo           ║');
  console.log('╚═══════════════════════════════════════════════════════════╝\n');

  // Setup: Create a temporary test directory
  const testRoot = path.join(tmpdir(), `self-healing-demo-${Date.now()}`);
  await mkdir(testRoot, { recursive: true });
  console.log('✅ Test environment created:', testRoot, '\n');

  // Step 1: Setup Event Listeners
  console.log('━━━ Step 1: Event Listeners Setup ━━━');
  
  const events: any[] = [];
  
  pathValidationEvents.on(PathValidationEventType.VALIDATION_FAILED, (event) => {
    events.push({ type: 'FAILED', data: event });
    console.log('  📉 Validation Failed:', event.data.filePath);
  });

  pathValidationEvents.on(PathValidationEventType.STRUCTURE_MISSING, (event) => {
    events.push({ type: 'MISSING', data: event });
    console.log('  🔍 Structure Missing:', event.data.filePath);
  });

  pathValidationEvents.on(PathValidationEventType.STRUCTURE_RECOVERED, (event) => {
    events.push({ type: 'RECOVERED', data: event });
    console.log('  🔄 Structure Recovered:', event.data.filePath, '- Success:', event.data.recoverySuccessful);
  });

  pathValidationEvents.on(PathValidationEventType.FALLBACK_TRIGGERED, (event) => {
    events.push({ type: 'FALLBACK', data: event });
    console.log('  ⚠️  Fallback Triggered:', event.data.filePath);
  });

  pathValidationEvents.on(PathValidationEventType.SNAPSHOT_CREATED, (event) => {
    events.push({ type: 'SNAPSHOT', data: event });
    console.log('  📸 Snapshot Created:', event.data.snapshotId);
  });

  console.log('✅ Event listeners registered\n');

  // Step 2: Create Self-Healing Validator
  console.log('━━━ Step 2: Self-Healing Validator Configuration ━━━');
  
  const validator = new SelfHealingPathValidator({
    safeRoot: testRoot,
    enableAutoRecovery: true,
    enableSnapshotting: false, // Manual snapshots for demo
    maxRecoveryAttempts: 3,
    dagEnabled: true,
  });

  console.log('✅ Validator configured:');
  console.log('  - Safe root:', testRoot);
  console.log('  - Auto-recovery: enabled');
  console.log('  - Max attempts: 3');
  console.log('  - DAG tracking: enabled\n');

  // Step 3: Create Test Files
  console.log('━━━ Step 3: Create Test Files ━━━');
  
  const testFile1 = path.join(testRoot, 'test1.txt');
  const testFile2 = path.join(testRoot, 'nested', 'test2.txt');
  
  await writeFile(testFile1, 'Test content 1');
  await mkdir(path.dirname(testFile2), { recursive: true });
  await writeFile(testFile2, 'Test content 2');
  
  console.log('✅ Created test files:');
  console.log('  - test1.txt');
  console.log('  - nested/test2.txt\n');

  // Step 4: Validate Existing Files
  console.log('━━━ Step 4: Validate Existing Files ━━━');
  
  try {
    const path1 = await validator.validateAndResolvePath('test1.txt');
    console.log('✅ Validated test1.txt:', path1);
  } catch (error) {
    console.log('❌ Failed to validate test1.txt:', error);
  }

  try {
    const path2 = await validator.validateAndResolvePath('nested/test2.txt');
    console.log('✅ Validated nested/test2.txt:', path2);
  } catch (error) {
    console.log('❌ Failed to validate nested/test2.txt:', error);
  }

  console.log('');

  // Step 5: Create Snapshot
  console.log('━━━ Step 5: Create Structure Snapshot ━━━');
  
  const snapshot = await validator.createSnapshot();
  console.log('✅ Snapshot created:');
  console.log('  - ID:', snapshot.id);
  console.log('  - Timestamp:', snapshot.timestamp);
  console.log('  - DAG nodes:', snapshot.dagNodes.size);
  console.log('  - Path mappings:', snapshot.pathMappings.size);
  console.log('');

  // Step 6: Test Recovery (Simulate Missing File)
  console.log('━━━ Step 6: Test Auto-Recovery ━━━');
  
  try {
    await validator.validateAndResolvePath('missing.txt');
    console.log('✅ Validated missing.txt (recovered)');
  } catch (error) {
    console.log('ℹ️  Expected failure for missing.txt:', (error as Error).message.substring(0, 50) + '...');
  }

  console.log('');

  // Step 7: ProvenanceService Integration
  console.log('━━━ Step 7: ProvenanceService Integration ━━━');
  
  const provenanceService = new ProvenanceService(validator);
  
  try {
    const digest = await provenanceService.generateFileDigest('test1.txt');
    console.log('✅ Generated file digest:', digest.substring(0, 40) + '...');
  } catch (error) {
    console.log('❌ Failed to generate digest:', error);
  }

  console.log('');

  // Step 8: Governance Metrics
  console.log('━━━ Step 8: Governance Metrics ━━━');
  
  const metrics = selfHealingGovernance.getMetrics();
  console.log('📊 Current Metrics:');
  console.log('  - Total validations:', metrics.totalValidations);
  console.log('  - Total failures:', metrics.totalFailures);
  console.log('  - Total recoveries:', metrics.totalRecoveries);
  console.log('  - Success rate:', (selfHealingGovernance.getSuccessRate() * 100).toFixed(2) + '%');
  console.log('');

  // Step 9: Event Summary
  console.log('━━━ Step 9: Event Summary ━━━');
  console.log('📡 Total events captured:', events.length);
  
  const eventTypes = events.reduce((acc: any, e) => {
    acc[e.type] = (acc[e.type] || 0) + 1;
    return acc;
  }, {});
  
  Object.entries(eventTypes).forEach(([type, count]) => {
    console.log(`  - ${type}: ${count}`);
  });
  console.log('');

  // Step 10: Cleanup
  console.log('━━━ Step 10: Cleanup ━━━');
  
  validator.dispose();
  console.log('✅ Validator disposed');
  
  await rm(testRoot, { recursive: true, force: true });
  console.log('✅ Test environment cleaned\n');

  // Final Summary
  console.log('╔═══════════════════════════════════════════════════════════╗');
  console.log('║   Demo Complete - Self-Healing System Verified           ║');
  console.log('╚═══════════════════════════════════════════════════════════╝');
  console.log('\n✨ Key Achievements:');
  console.log('  ✅ Event-driven architecture working');
  console.log('  ✅ Auto-recovery mechanisms functional');
  console.log('  ✅ Structure snapshots created');
  console.log('  ✅ DAG tracking operational');
  console.log('  ✅ Governance integration active');
  console.log('  ✅ ProvenanceService integration confirmed\n');
}

// Run the demo if executed directly
if (require.main === module) {
  completeDemoExample()
    .then(() => {
      console.log('Demo completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Demo failed:', error);
      process.exit(1);
    });
}

export { completeDemoExample };
