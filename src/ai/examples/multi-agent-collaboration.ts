/**
 * Multi-Agent Collaboration Example
 * 
 * 展示如何使用 Agent Coordinator 進行多 Agent 協作
 * Demonstrates how to use Agent Coordinator for multi-agent collaboration
 */

import { AgentCoordinator, AgentCollaboration } from '../src/collaboration/index.js';
import { AgentContext } from '../src/types.js';
import { ArchitectAgent } from '../src/agents/architect/index.js';
import { SecurityAgent } from '../src/agents/security/index.js';
import { DevOpsAgent } from '../src/agents/devops/index.js';

/**
 * 場景 1: 安全漏洞自動修復流程
 * Scenario 1: Automated Security Vulnerability Remediation
 */
async function securityVulnerabilityRemediation() {
  console.log('\n=== Security Vulnerability Remediation ===\n');

  const coordinator = new AgentCoordinator();
  
  // 創建 Agent 實例
  const securityAgent = new SecurityAgent();
  const architectAgent = new ArchitectAgent();
  const devOpsAgent = new DevOpsAgent();

  // 配置順序協作：安全檢測 → 架構評估 → 部署影響分析
  // Configure sequential collaboration: Security scan → Architecture assessment → Deployment impact
  const collaboration: AgentCollaboration = {
    coordinatorId: 'vuln-fix-001',
    participants: [securityAgent, architectAgent, devOpsAgent],
    strategy: 'sequential'
  };

  const context: AgentContext = {
    requestId: 'security-scan-001',
    timestamp: new Date(),
    payload: {
      repository: 'unmanned-island',
      branch: 'main',
      scanType: 'full'
    }
  };

  const result = await coordinator.orchestrate(collaboration, context);

  console.log('Coordination Result:');
  console.log(`- Strategy: ${result.strategy}`);
  console.log(`- Success: ${result.success}`);
  console.log(`- Execution Time: ${result.executionTime}ms`);
  console.log(`- Total Insights: ${result.allInsights.length}`);
  
  // 顯示每個 Agent 的發現
  // Display findings from each agent
  console.log('\nAgent Reports:');
  for (const report of result.individualReports) {
    console.log(`\n[${report.agent}]`);
    for (const insight of report.insights) {
      console.log(`  ${insight.signal.toUpperCase()}: ${insight.title}`);
      console.log(`    ${insight.description}`);
    }
  }

  // 檢查是否有嚴重問題
  // Check for critical issues
  const criticalIssues = result.allInsights.filter(i => i.signal === 'error');
  if (criticalIssues.length > 0) {
    console.log(`\n⚠️  Found ${criticalIssues.length} critical issues requiring attention`);
  }
}

/**
 * 場景 2: 並行性能分析
 * Scenario 2: Parallel Performance Analysis
 */
async function parallelPerformanceAnalysis() {
  console.log('\n=== Parallel Performance Analysis ===\n');

  const coordinator = new AgentCoordinator();
  
  const architectAgent = new ArchitectAgent();
  const devOpsAgent = new DevOpsAgent();

  // 配置並行協作：同時進行架構分析和運維監控
  // Configure parallel collaboration: Simultaneous architecture analysis and ops monitoring
  const collaboration: AgentCollaboration = {
    coordinatorId: 'perf-analysis-001',
    participants: [architectAgent, devOpsAgent],
    strategy: 'parallel'
  };

  const context: AgentContext = {
    requestId: 'perf-analysis-001',
    timestamp: new Date(),
    payload: {
      analysisType: 'performance',
      metrics: ['response-time', 'throughput', 'resource-usage']
    }
  };

  console.log('Starting parallel analysis...');
  const startTime = Date.now();
  const result = await coordinator.orchestrate(collaboration, context);
  const totalTime = Date.now() - startTime;

  console.log(`\nCompleted in ${totalTime}ms (parallel execution)`);
  console.log(`Agent execution time: ${result.executionTime}ms`);
  console.log(`Time saved: ~${totalTime - result.executionTime}ms\n`);

  // 聚合所有性能指標
  // Aggregate all performance metrics
  const performanceInsights = result.allInsights.filter(
    i => i.data && 'performance' in i.data
  );
  
  console.log(`Found ${performanceInsights.length} performance-related insights`);
}

/**
 * 場景 3: 條件執行 - 漸進式問題診斷
 * Scenario 3: Conditional Execution - Progressive Problem Diagnosis
 */
async function progressiveDiagnosis() {
  console.log('\n=== Progressive Problem Diagnosis ===\n');

  const coordinator = new AgentCoordinator();
  
  const architectAgent = new ArchitectAgent();
  const securityAgent = new SecurityAgent();
  const devOpsAgent = new DevOpsAgent();

  // 條件：只有發現警告或錯誤時才繼續深入分析
  // Condition: Only continue deeper analysis if warnings or errors are found
  const shouldContinue = (reports: any[]) => {
    return reports.some(r => 
      r.insights.some((i: any) => i.signal === 'warn' || i.signal === 'error')
    );
  };

  const collaboration: AgentCollaboration = {
    coordinatorId: 'diagnosis-001',
    participants: [architectAgent, securityAgent, devOpsAgent],
    strategy: 'conditional',
    condition: shouldContinue
  };

  const context: AgentContext = {
    requestId: 'diagnosis-001',
    timestamp: new Date(),
    payload: {
      diagnosisLevel: 'progressive'
    }
  };

  const result = await coordinator.orchestrate(collaboration, context);

  console.log('Progressive Diagnosis Results:');
  console.log(`- Agents executed: ${result.individualReports.length}`);
  console.log(`- Total insights: ${result.allInsights.length}`);
  
  if (result.individualReports.length < 3) {
    console.log('\n✓ No critical issues found, deep analysis skipped');
  } else {
    console.log('\n⚠️  Critical issues found, full diagnosis completed');
  }
}

/**
 * 場景 4: 迭代優化流程
 * Scenario 4: Iterative Optimization Process
 */
async function iterativeOptimization() {
  console.log('\n=== Iterative Optimization Process ===\n');

  const coordinator = new AgentCoordinator();
  const architectAgent = new ArchitectAgent();

  let optimizationScore = 0;
  
  // 迭代條件：優化分數達到 80 分以上
  // Iteration condition: Continue until optimization score reaches 80+
  const isOptimized = (reports: any[]) => {
    optimizationScore += 20; // 模擬優化進度
    console.log(`  Optimization score: ${optimizationScore}/100`);
    return optimizationScore >= 80;
  };

  const collaboration: AgentCollaboration = {
    coordinatorId: 'optimization-001',
    participants: [architectAgent],
    strategy: 'iterative',
    condition: isOptimized,
    maxIterations: 10
  };

  const context: AgentContext = {
    requestId: 'optimization-001',
    timestamp: new Date(),
    payload: {
      optimizationTarget: 'architecture'
    }
  };

  console.log('Starting iterative optimization...\n');
  const result = await coordinator.orchestrate(collaboration, context);

  console.log(`\nOptimization completed after ${result.individualReports.length} iterations`);
  console.log(`Final score: ${optimizationScore}/100`);
}

/**
 * 場景 5: 知識共享示例
 * Scenario 5: Knowledge Sharing Example
 */
async function knowledgeSharingExample() {
  console.log('\n=== Knowledge Sharing Between Agents ===\n');

  const coordinator = new AgentCoordinator();
  
  const securityAgent = new SecurityAgent();
  const architectAgent = new ArchitectAgent();
  const devOpsAgent = new DevOpsAgent();

  const collaboration: AgentCollaboration = {
    coordinatorId: 'knowledge-share-001',
    participants: [securityAgent, architectAgent, devOpsAgent],
    strategy: 'sequential'
  };

  const context: AgentContext = {
    requestId: 'knowledge-001',
    timestamp: new Date()
  };

  await coordinator.orchestrate(collaboration, context);

  // 檢查 Agent 間共享的知識
  // Check knowledge shared between agents
  console.log('Knowledge Base:');
  
  const architectKnowledge = coordinator.getSharedKnowledge('Architect Agent');
  console.log(`\n[Architect Agent] received ${architectKnowledge.length} knowledge items:`);
  for (const knowledge of architectKnowledge) {
    console.log(`  From: ${knowledge.sourceAgent}`);
    console.log(`  Insights: ${knowledge.insights.length}`);
  }

  const devOpsKnowledge = coordinator.getSharedKnowledge('DevOps Agent');
  console.log(`\n[DevOps Agent] received ${devOpsKnowledge.length} knowledge items:`);
  for (const knowledge of devOpsKnowledge) {
    console.log(`  From: ${knowledge.sourceAgent}`);
    console.log(`  Insights: ${knowledge.insights.length}`);
  }
}

/**
 * 執行所有示例
 * Run all examples
 */
async function main() {
  console.log('🚀 Multi-Agent Collaboration Examples\n');
  console.log('=' .repeat(60));

  try {
    await securityVulnerabilityRemediation();
    await parallelPerformanceAnalysis();
    await progressiveDiagnosis();
    await iterativeOptimization();
    await knowledgeSharingExample();

    console.log('\n' + '='.repeat(60));
    console.log('\n✓ All examples completed successfully\n');
  } catch (error) {
    console.error('\n❌ Error running examples:', error);
    process.exit(1);
  }
}

// 如果直接執行此文件，運行所有示例
// If this file is executed directly, run all examples
import { fileURLToPath } from 'url';
const isMainModule = process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1];
if (isMainModule) {
  main();
}

export {
  securityVulnerabilityRemediation,
  parallelPerformanceAnalysis,
  progressiveDiagnosis,
  iterativeOptimization,
  knowledgeSharingExample
};
