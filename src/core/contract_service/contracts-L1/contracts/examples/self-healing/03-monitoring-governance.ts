/**
 * Example 3: Monitoring and Governance
 * 
 * Demonstrates how to monitor self-healing activities
 * and access governance metrics and attestations
 */

import { selfHealingGovernance } from '../../src/governance/self-healing-integration';
import { pathValidationEvents, PathValidationEventType } from '../../src/events/path-validation-events';

async function monitoringGovernanceExample() {
  console.log('=== Example 3: Monitoring and Governance ===\n');

  // Get current metrics
  const metrics = selfHealingGovernance.getMetrics();
  
  console.log('📊 Current Self-Healing Metrics:');
  console.log('   - Total validations:', metrics.totalValidations);
  console.log('   - Total failures:', metrics.totalFailures);
  console.log('   - Total recoveries:', metrics.totalRecoveries);
  console.log('   - Successful recoveries:', metrics.successfulRecoveries);
  console.log('   - Failed recoveries:', metrics.failedRecoveries);
  console.log('   - Snapshots created:', metrics.snapshotsCreated);
  console.log('   - DAG nodes rebuilt:', metrics.dagNodesRebuilt);
  console.log('   - Last event:', metrics.lastEventTimestamp);
  
  // Calculate and display success rate
  const successRate = selfHealingGovernance.getSuccessRate();
  console.log('\n✅ Success Rate:', (successRate * 100).toFixed(2) + '%');

  // Get recent attestations
  const attestations = selfHealingGovernance.getAttestations(10);
  console.log('\n📝 Recent Attestations:', attestations.length);
  
  if (attestations.length > 0) {
    console.log('   Latest attestation:');
    const latest = attestations[attestations.length - 1];
    console.log('   - ID:', latest.id);
    console.log('   - Event type:', latest.eventType);
    console.log('   - File path:', latest.filePath);
    console.log('   - Recovery attempted:', latest.recoveryAttempted);
    console.log('   - Recovery successful:', latest.recoverySuccessful);
    console.log('   - Governance compliant:', latest.governanceCompliant);
    if (latest.policyViolations.length > 0) {
      console.log('   - Policy violations:', latest.policyViolations.join(', '));
    }
  }

  // Export governance report
  console.log('\n📄 Exporting Governance Report...');
  const report = selfHealingGovernance.exportGovernanceReport();
  
  // Parse and display report summary
  const reportData = JSON.parse(report);
  console.log('   - Report timestamp:', reportData.timestamp);
  console.log('   - Success rate:', (reportData.successRate * 100).toFixed(2) + '%');
  console.log('   - Total events:', reportData.policyCompliance.totalEvents);
  console.log('   - Compliant events:', reportData.policyCompliance.compliantEvents);
  console.log('   - Violations:', reportData.policyCompliance.violations);

  console.log('\n=== Example Complete ===\n');
}

// Run the example if executed directly
if (require.main === module) {
  monitoringGovernanceExample()
    .then(() => {
      console.log('Example completed successfully');
      process.exit(0);
    })
    .catch((error) => {
      console.error('Example failed:', error);
      process.exit(1);
    });
}

export { monitoringGovernanceExample };
