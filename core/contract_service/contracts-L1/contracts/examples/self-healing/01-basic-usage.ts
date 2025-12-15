/**
 * Example 1: Basic Self-Healing Usage
 * 
 * Demonstrates basic usage of self-healing path validation
 * with ProvenanceService (self-healing enabled by default)
 */

import { ProvenanceService } from '../../src/services/provenance';

async function basicUsageExample() {
  console.log('=== Example 1: Basic Self-Healing Usage ===\n');

  // ProvenanceService now uses self-healing by default
  const provenanceService = new ProvenanceService();

  try {
    // This will automatically attempt recovery if path is missing
    const digest = await provenanceService.generateFileDigest('data/file.txt');
    console.log('✅ File digest:', digest);
  } catch (error) {
    console.error('❌ Failed after recovery attempts:', error);
  }

  console.log('\n=== Example Complete ===\n');
}

// Run the example if executed directly
if (require.main === module) {
  basicUsageExample()
    .then(() => {
      console.log('Example completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Example failed:', error);
      process.exit(1);
    });
}

export { basicUsageExample };
