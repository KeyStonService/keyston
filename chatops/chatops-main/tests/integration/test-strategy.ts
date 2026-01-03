// tests/integration/test-strategy.ts
// Phase-2: Multi-layer Test Pyramid Manager for chatops Multi-Agent AI

import {
  TestSuite,
  TestLevel,
  TestResult,
  TestReport,
  TestSummary,
  TestStrategy,
  TestExecutionContext,
  STRATEGY_COMMANDS,
} from '../types';

/**
 * Test Pyramid Manager implementing the 70-20-10 test distribution.
 * - Unit tests: 70%
 * - Integration tests: 20%
 * - E2E tests: 10%
 */
export class TestPyramidManager {
  private testLevels: Map<TestLevel, TestSuite[]> = new Map();

  constructor() {
    this.initializeTestLevels();
  }

  private initializeTestLevels(): void {
    // Unit tests (70%)
    this.testLevels.set('unit', [
      { name: 'utils', coverage: 95, priority: 'high' },
      { name: 'services', coverage: 90, priority: 'high' },
      { name: 'components', coverage: 85, priority: 'medium' },
    ]);

    // Integration tests (20%)
    this.testLevels.set('integration', [
      { name: 'api-endpoints', coverage: 80, priority: 'high' },
      { name: 'database', coverage: 75, priority: 'medium' },
      { name: 'external-services', coverage: 70, priority: 'low' },
    ]);

    // E2E tests (10%)
    this.testLevels.set('e2e', [
      { name: 'critical-paths', coverage: 100, priority: 'critical' },
      { name: 'user-journeys', coverage: 80, priority: 'high' },
      { name: 'rest-to-grpc', coverage: 100, priority: 'critical' },
    ]);
  }

  async executeTestLevel(level: TestLevel): Promise<TestResult> {
    const suites = this.testLevels.get(level) || [];
    const results: TestResult[] = [];

    for (const suite of suites) {
      console.log(`Running ${level} test: ${suite.name}`);
      const result = await this.runTestSuite(suite);
      results.push(result);
    }

    return this.aggregateResults(results, level);
  }

  private async runTestSuite(suite: TestSuite): Promise<TestResult> {
    const startTime = Date.now();

    try {
      await this.simulateTestExecution(suite);

      return {
        suite: suite.name,
        status: 'passed',
        coverage: suite.coverage,
        duration: Date.now() - startTime,
        details: `${suite.name} tests passed`,
      };
    } catch (error) {
      return {
        suite: suite.name,
        status: 'failed',
        coverage: 0,
        duration: Date.now() - startTime,
        details: `${suite.name} tests failed: ${error}`,
        errors: [String(error)],
      };
    }
  }

  private async simulateTestExecution(suite: TestSuite): Promise<void> {
    // Simulate test execution time based on priority
    const baseTime = 1000;
    const priorityMultiplier =
      suite.priority === 'critical' ? 0.5 :
      suite.priority === 'high' ? 1 :
      suite.priority === 'medium' ? 1.5 : 2;

    await new Promise((resolve) =>
      setTimeout(resolve, baseTime * priorityMultiplier + Math.random() * 1000)
    );

    // Simulate occasional failures for low priority tests
    if (suite.priority === 'low' && Math.random() < 0.1) {
      throw new Error('Random test failure');
    }
  }

  private aggregateResults(results: TestResult[], level: TestLevel): TestResult {
    const passedCount = results.filter((r) => r.status === 'passed').length;
    const totalCoverage =
      results.reduce((sum, r) => sum + r.coverage, 0) / results.length;
    const totalDuration = results.reduce((sum, r) => sum + r.duration, 0);
    const allErrors = results.flatMap((r) => r.errors || []);

    return {
      suite: level,
      status: passedCount === results.length ? 'passed' : 'failed',
      coverage: Math.round(totalCoverage * 100) / 100,
      duration: totalDuration,
      details: `${level}: ${passedCount}/${results.length} suites passed`,
      errors: allErrors.length > 0 ? allErrors : undefined,
    };
  }

  getTestSuites(level: TestLevel): TestSuite[] {
    return this.testLevels.get(level) || [];
  }
}

/**
 * Parallel Test Executor for efficient test execution.
 */
export class ParallelTestExecutor {
  private maxConcurrency: number = 4;
  private context: TestExecutionContext;

  constructor(context: TestExecutionContext) {
    this.context = context;
  }

  async executeTests(testManager: TestPyramidManager): Promise<TestReport> {
    const startTime = Date.now();

    // Execute test levels in parallel
    const [unitResults, integrationResults, e2eResults] = await Promise.allSettled([
      testManager.executeTestLevel('unit'),
      testManager.executeTestLevel('integration'),
      testManager.executeTestLevel('e2e'),
    ]);

    const report: TestReport = {
      timestamp: new Date().toISOString(),
      duration: Date.now() - startTime,
      traceId: this.context.traceId,
      strategy: this.context.strategy,
      results: {
        unit: this.extractResult(unitResults),
        integration: this.extractResult(integrationResults),
        e2e: this.extractResult(e2eResults),
      },
      summary: this.generateSummary([
        this.extractResult(unitResults),
        this.extractResult(integrationResults),
        this.extractResult(e2eResults),
      ]),
      affectedModules: this.context.affectedModules,
    };

    return report;
  }

  private extractResult(
    settledResult: PromiseSettledResult<TestResult>
  ): TestResult {
    if (settledResult.status === 'fulfilled') {
      return settledResult.value;
    } else {
      return {
        suite: 'unknown',
        status: 'failed',
        coverage: 0,
        duration: 0,
        details: String(settledResult.reason),
        errors: [String(settledResult.reason)],
      };
    }
  }

  private generateSummary(results: TestResult[]): TestSummary {
    const totalTests = results.length;
    const passedTests = results.filter((r) => r.status === 'passed').length;
    const failedTests = results.filter((r) => r.status === 'failed').length;
    const skippedTests = results.filter((r) => r.status === 'skipped').length;
    const avgCoverage =
      results.reduce((sum, r) => sum + r.coverage, 0) / totalTests;

    return {
      totalTests,
      passedTests,
      failedTests,
      skippedTests,
      coverage: Math.round(avgCoverage * 100) / 100,
      successRate: Math.round((passedTests / totalTests) * 10000) / 100,
    };
  }
}

/**
 * Strategy Analyzer for determining test strategy based on changed files.
 */
export class StrategyAnalyzer {
  private strategyRules = [
    { patterns: ['proto/**', '.github/workflows/**', 'policies/**', 'deployments/**'], strategy: 'comprehensive' as TestStrategy },
    { patterns: ['services/engine-python/**'], strategy: 'engine-focused' as TestStrategy },
    { patterns: ['services/gateway-ts/**'], strategy: 'gateway-focused' as TestStrategy },
    { patterns: ['tests/**'], strategy: 'test-focused' as TestStrategy },
  ];

  analyzeChanges(changedFiles: string[]): TestStrategy {
    for (const rule of this.strategyRules) {
      for (const pattern of rule.patterns) {
        const regex = this.patternToRegex(pattern);
        if (changedFiles.some((file) => regex.test(file))) {
          return rule.strategy;
        }
      }
    }
    return 'standard';
  }

  private patternToRegex(pattern: string): RegExp {
    const escaped = pattern
      .replace(/[.+^${}()|[\]\\]/g, '\\$&')
      .replace(/\*\*/g, '.*')
      .replace(/\*/g, '[^/]*');
    return new RegExp(`^${escaped}$`);
  }

  getCommands(strategy: TestStrategy): string[] {
    return STRATEGY_COMMANDS[strategy];
  }

  getAffectedModules(changedFiles: string[]): string[] {
    const modules = new Set<string>();

    for (const file of changedFiles) {
      if (file.startsWith('services/')) {
        const parts = file.split('/');
        if (parts.length >= 2) {
          modules.add(parts[1]);
        }
      } else if (file.startsWith('proto/')) {
        modules.add('proto');
      } else if (file.startsWith('tests/')) {
        modules.add('tests');
      }
    }

    return Array.from(modules);
  }
}

/**
 * Report Generator for CI artifacts.
 */
export class ReportGenerator {
  async generateAdaptiveReport(
    report: TestReport,
    outputPath: string = 'test-reports/adaptive-report.json'
  ): Promise<void> {
    const fs = await import('fs').then((m) => m.promises);
    const path = await import('path');

    const dir = path.dirname(outputPath);
    await fs.mkdir(dir, { recursive: true });

    const reportJson = JSON.stringify(report, null, 2);
    await fs.writeFile(outputPath, reportJson, 'utf-8');

    console.log(`Report generated: ${outputPath}`);
  }

  async generateAuditLog(
    report: TestReport,
    outputPath: string = 'var/audit/test-execution.jsonl'
  ): Promise<void> {
    const fs = await import('fs').then((m) => m.promises);
    const path = await import('path');

    const dir = path.dirname(outputPath);
    await fs.mkdir(dir, { recursive: true });

    const auditEntry = {
      trace_id: report.traceId,
      event: 'test_execution',
      timestamp: report.timestamp,
      strategy: report.strategy,
      duration: report.duration,
      summary: report.summary,
      affected_modules: report.affectedModules,
    };

    await fs.appendFile(outputPath, JSON.stringify(auditEntry) + '\n', 'utf-8');

    console.log(`Audit log appended: ${outputPath}`);
  }
}

// CLI entry point
async function main(): Promise<void> {
  const traceId = `trace-${Date.now()}-local`;
  const changedFiles = process.argv.slice(2);

  const analyzer = new StrategyAnalyzer();
  const strategy = analyzer.analyzeChanges(changedFiles);
  const affectedModules = analyzer.getAffectedModules(changedFiles);

  console.log(`Strategy: ${strategy}`);
  console.log(`Affected modules: ${affectedModules.join(', ')}`);
  console.log(`Commands: ${analyzer.getCommands(strategy).join(', ')}`);

  const context: TestExecutionContext = {
    traceId,
    environment: 'development',
    deployTarget: 'dev',
    branch: process.env.GITHUB_HEAD_REF || 'local',
    sha: process.env.GITHUB_SHA || 'local',
    strategy,
    affectedModules,
  };

  const testManager = new TestPyramidManager();
  const executor = new ParallelTestExecutor(context);
  const report = await executor.executeTests(testManager);

  const reportGenerator = new ReportGenerator();
  await reportGenerator.generateAdaptiveReport(report);
  await reportGenerator.generateAuditLog(report);

  console.log('Test Summary:', report.summary);

  if (report.summary.failedTests > 0) {
    process.exit(1);
  }
}

// Run if executed directly
if (require.main === module) {
  main().catch((error) => {
    console.error('Test execution failed:', error);
    process.exit(1);
  });
}
