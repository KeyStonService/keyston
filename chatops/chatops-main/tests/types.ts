// tests/types.ts
// Phase-2: Type definitions for Multi-Agent AI Test Automation System

/**
 * Test pyramid levels for the chatops testing framework.
 */
export type TestLevel = 'unit' | 'integration' | 'e2e';

/**
 * Priority levels for test suites.
 */
export type TestPriority = 'critical' | 'high' | 'medium' | 'low';

/**
 * Test execution status.
 */
export type TestStatus = 'passed' | 'failed' | 'skipped' | 'pending';

/**
 * Test strategy types based on changed paths.
 */
export type TestStrategy =
  | 'comprehensive'
  | 'engine-focused'
  | 'gateway-focused'
  | 'test-focused'
  | 'standard';

/**
 * Gate verdict from Policy Agent.
 */
export type GateVerdict = 'pass' | 'block' | 'need-approval';

/**
 * Test suite definition.
 */
export interface TestSuite {
  name: string;
  coverage: number;
  priority: TestPriority;
  path?: string;
  timeout?: number;
}

/**
 * Individual test result.
 */
export interface TestResult {
  suite: string;
  status: TestStatus;
  coverage: number;
  duration: number;
  details: string;
  errors?: string[];
  traceId?: string;
}

/**
 * Test report containing all results.
 */
export interface TestReport {
  timestamp: string;
  duration: number;
  traceId: string;
  strategy: TestStrategy;
  results: Record<TestLevel, TestResult>;
  summary: TestSummary;
  affectedModules: string[];
}

/**
 * Summary of test execution.
 */
export interface TestSummary {
  totalTests: number;
  passedTests: number;
  failedTests: number;
  skippedTests: number;
  coverage: number;
  successRate: number;
}

/**
 * Multi-Agent AI output contract.
 */
export interface AgentOutput {
  traceId: string;
  timestamp: string;
  agent: string;
  event: string;
  data: Record<string, unknown>;
}

/**
 * CI Agent output for test execution.
 */
export interface CIAgentOutput extends AgentOutput {
  agent: 'ci';
  event: 'test_complete';
  data: {
    strategy: TestStrategy;
    affectedModules: string[];
    report: TestReport;
  };
}

/**
 * Policy Agent output for gate verdict.
 */
export interface PolicyAgentOutput extends AgentOutput {
  agent: 'policy';
  event: 'gate_verdict';
  data: {
    verdict: GateVerdict;
    qualityScore: number;
    thresholdMet: boolean;
    blockedReasons?: string[];
  };
}

/**
 * Observability Agent output for audit.
 */
export interface ObservabilityAgentOutput extends AgentOutput {
  agent: 'observability';
  event: 'audit_record';
  data: {
    testDuration: number;
    failureRate: number;
    coverageTrend: 'up' | 'down' | 'stable';
    previousCoverage?: number;
  };
}

/**
 * Configuration for adaptive testing.
 */
export interface AdaptiveTestConfig {
  strategyRules: StrategyRule[];
  defaultStrategy: TestStrategy;
  coverageThresholds: Record<TestLevel, number>;
  timeoutMs: number;
}

/**
 * Rule for determining test strategy.
 */
export interface StrategyRule {
  pathPattern: string;
  strategy: TestStrategy;
  priority: number;
}

/**
 * Change analysis result.
 */
export interface ChangeAnalysis {
  changedFiles: string[];
  affectedModules: string[];
  recommendedStrategy: TestStrategy;
  matchedRules: StrategyRule[];
}

/**
 * Test execution context.
 */
export interface TestExecutionContext {
  traceId: string;
  environment: 'development' | 'staging' | 'production';
  deployTarget: 'dev' | 'stage' | 'prod';
  branch: string;
  sha: string;
  strategy: TestStrategy;
  affectedModules: string[];
}

/**
 * Makefile target mapping for strategies.
 */
export const STRATEGY_COMMANDS: Record<TestStrategy, string[]> = {
  comprehensive: ['make py-test', 'make ts-build', 'make e2e-rest'],
  'engine-focused': ['make py-test'],
  'gateway-focused': ['make ts-build', 'make e2e-rest'],
  'test-focused': ['make e2e-rest'],
  standard: ['make py-test', 'make ts-build'],
};

/**
 * Path patterns for strategy determination.
 */
export const STRATEGY_PATHS: Record<string, TestStrategy> = {
  'proto/**': 'comprehensive',
  '.github/workflows/**': 'comprehensive',
  'policies/**': 'comprehensive',
  'deployments/**': 'comprehensive',
  'services/engine-python/**': 'engine-focused',
  'services/gateway-ts/**': 'gateway-focused',
  'tests/**': 'test-focused',
};
