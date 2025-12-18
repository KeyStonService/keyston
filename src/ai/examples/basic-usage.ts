/**
 * Island AI Basic Usage Example
 * 
 * Demonstrates how to use Island AI Stage 1 agents for system diagnostics
 * and intelligent insights.
 */

import { runStageOne, stageOneAgents, AgentContext } from '../src/index.js';
import type { AgentReport } from '../src/types.js';

// ============================================================================
// Example 1: Run All Agents
// ============================================================================
async function runAllAgents() {
  console.log('🚀 Running Island AI Stage 1 - All Agents\n');

  const context: AgentContext = {
    requestId: 'example-001',
    timestamp: new Date(),
    payload: {
      deploymentsPerWeek: 15,
      activeUsers: 1250,
      errorRate: 0.02,
      responseTimeMs: 245,
    },
  };

  try {
    const reports = await runStageOne(context);

    console.log(`✅ Completed ${reports.length} agent diagnostics\n`);

    reports.forEach((report: AgentReport) => {
      console.log(`\n📊 ${report.agent} Agent Report`);
      console.log(`   Generated at: ${report.generatedAt.toISOString()}`);
      console.log(`   Insights: ${report.insights.length}`);

      report.insights.forEach((insight) => {
        const emoji =
          insight.signal === 'error'
            ? '❌'
            : insight.signal === 'warn'
              ? '⚠️'
              : 'ℹ️';
        console.log(`   ${emoji} [${insight.signal}] ${insight.title}`);
        console.log(`      ${insight.description}`);
      });
    });
  } catch (error) {
    console.error('❌ Error running agents:', error);
  }
}

// ============================================================================
// Example 2: Run Individual Agent
// ============================================================================
async function runIndividualAgent() {
  console.log('\n🎯 Running Individual Agent - Architect\n');

  const architectAgent = stageOneAgents.find(
    (agent) => agent.name === 'ArchitectAgent'
  );

  if (!architectAgent) {
    console.error('❌ Architect agent not found');
    return;
  }

  const context: AgentContext = {
    requestId: 'example-002',
    timestamp: new Date(),
    payload: {
      serviceCount: 42,
      microservicesPattern: 'event-driven',
      requestsPerSecond: 1500,
    },
  };

  try {
    const report = await architectAgent.run(context);

    console.log(`📐 ${report.agent} Analysis Complete`);
    console.log(`   Found ${report.insights.length} architectural insights\n`);

    report.insights.forEach((insight) => {
      console.log(`   • ${insight.title}`);
      console.log(`     ${insight.description}`);
      if (insight.data) {
        console.log(`     Data:`, insight.data);
      }
    });
  } catch (error) {
    console.error('❌ Error running architect agent:', error);
  }
}

// ============================================================================
// Example 3: Integration with SynergyMesh Core
// ============================================================================
async function integrationExample() {
  console.log('\n🔗 Island AI + SynergyMesh Integration Example\n');

  // This example shows how Island AI agents can be integrated
  // with the SynergyMesh core engine for automated diagnostics

  const context: AgentContext = {
    requestId: 'synergymesh-diagnostic-001',
    timestamp: new Date(),
    payload: {
      systemHealth: 'degraded',
      cpuUtilization: 0.78,
      memoryUsage: 0.85,
      diskIOPS: 450,
      networkLatency: 32,
    },
  };

  console.log('📋 System Metrics:', context.payload);
  console.log('\n🔍 Running diagnostic agents...\n');

  try {
    const reports = await runStageOne(context);

    // Filter critical and warning insights
    const criticalInsights = reports.flatMap((r) =>
      r.insights.filter((i) => i.signal === 'error')
    );

    const warningInsights = reports.flatMap((r) =>
      r.insights.filter((i) => i.signal === 'warn')
    );

    console.log(`\n🚨 Critical Issues: ${criticalInsights.length}`);
    criticalInsights.forEach((insight) => {
      console.log(`   ❌ ${insight.title}`);
    });

    console.log(`\n⚠️  Warnings: ${warningInsights.length}`);
    warningInsights.forEach((insight) => {
      console.log(`   ⚠️  ${insight.title}`);
    });

    // In a real integration, these insights would be:
    // 1. Sent to the Mind Matrix for decision making
    // 2. Logged to the audit trail (SLSA provenance)
    // 3. Trigger automated remediation via safety mechanisms
    // 4. Update the service registry with health status

    console.log('\n💡 Next Steps:');
    console.log('   1. Integrate with core/mind_matrix for decision making');
    console.log('   2. Connect to core/safety_mechanisms for auto-remediation');
    console.log('   3. Log to core/slsa_provenance for audit trail');
  } catch (error) {
    console.error('❌ Integration error:', error);
  }
}

// ============================================================================
// Main Execution
// ============================================================================
async function main() {
  console.log('===========================================================');
  console.log('         Island AI Stage 1 - Usage Examples');
  console.log('===========================================================\n');

  await runAllAgents();
  await runIndividualAgent();
  await integrationExample();

  console.log('\n===========================================================');
  console.log('✅ All examples completed successfully!');
  console.log('===========================================================\n');
}

// Run if executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { runAllAgents, runIndividualAgent, integrationExample };
