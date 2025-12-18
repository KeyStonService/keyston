/**
 * Example 2: Custom Self-Healing Configuration
 * 
 * Demonstrates how to configure the self-healing path validator
 * with custom settings for recovery attempts, snapshots, and DAG tracking
 */

import { SelfHealingPathValidator } from '../../src/utils/self-healing-path-validator';
import { ProvenanceService } from '../../src/services/provenance';
import * as path from 'path';

async function customConfigurationExample() {
  console.log('=== Example 2: Custom Self-Healing Configuration ===\n');

  // Create a custom validator with specific configuration
  const validator = new SelfHealingPathValidator({
    safeRoot: path.resolve(process.cwd(), 'custom-root'),
    enableAutoRecovery: true,
    enableSnapshotting: true,
    snapshotInterval: 30000, // 30 seconds
    maxRecoveryAttempts: 5,
    dagEnabled: true,
  });

  console.log('✅ Created self-healing validator with custom config:');
  console.log('   - Safe root: custom-root/');
  console.log('   - Auto-recovery: enabled');
  console.log('   - Snapshots: every 30 seconds');
  console.log('   - Max recovery attempts: 5');
  console.log('   - DAG tracking: enabled\n');

  // Use the custom validator with ProvenanceService
  const service = new ProvenanceService(validator);

  try {
    // Create a snapshot manually
    const snapshot = await validator.createSnapshot();
    console.log('✅ Created snapshot:', snapshot.id);
    console.log('   - Timestamp:', snapshot.timestamp);
    console.log('   - DAG nodes:', snapshot.dagNodes.size);
    console.log('   - Safe root:', snapshot.boundaries.safeRoot);
  } catch (error) {
    console.error('❌ Snapshot creation failed:', error);
  }

  // Clean up resources
  validator.dispose();
  console.log('\n✅ Validator resources disposed');

  console.log('\n=== Example Complete ===\n');
}

// Run the example if executed directly
if (require.main === module) {
  customConfigurationExample()
    .then(() => {
      console.log('Example completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Example failed:', error);
      process.exit(1);
    });
}

export { customConfigurationExample };
