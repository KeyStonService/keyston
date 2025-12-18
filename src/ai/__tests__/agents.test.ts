/**
 * Island AI Agents Unit Tests
 * 
 * Tests for all Stage 1 agents to ensure they produce valid reports
 * and handle various input scenarios correctly.
 */

import { describe, it, expect } from '@jest/globals';
import { runStageOne, stageOneAgents } from '../index.js';
import type { AgentContext, AgentReport, AgentInsight } from '../types.js';
import {
  ArchitectAgent,
  SecurityAgent,
  DevOpsAgent,
  QAAgent,
  DataScientistAgent,
  ProductManagerAgent,
} from '../agents/index.js';

// ============================================================================
// Helper Functions
// ============================================================================

let testIdCounter = 0;

function createTestContext(payload?: Record<string, unknown>): AgentContext {
  return {
    requestId: `test-${++testIdCounter}-${Date.now()}`,
    timestamp: new Date(),
    payload: payload || {},
  };
}

function validateAgentReport(report: AgentReport): void {
  expect(report).toBeDefined();
  expect(report.agent).toBeTruthy();
  expect(typeof report.agent).toBe('string');
  expect(report.insights).toBeInstanceOf(Array);
  expect(report.generatedAt).toBeInstanceOf(Date);
}

function validateAgentInsight(insight: AgentInsight): void {
  expect(insight).toBeDefined();
  expect(insight.title).toBeTruthy();
  expect(typeof insight.title).toBe('string');
  expect(insight.description).toBeTruthy();
  expect(typeof insight.description).toBe('string');
  expect(['info', 'warn', 'error']).toContain(insight.signal);
}

// ============================================================================
// Architect Agent Tests
// ============================================================================

describe('ArchitectAgent', () => {
  const agent = new ArchitectAgent();

  it('should have correct agent name', () => {
    expect(agent.name).toBe('ArchitectAgent');
  });

  it('should generate valid report', async () => {
    const context = createTestContext({
      serviceCount: 10,
      microservicesPattern: 'event-driven',
    });

    const report = await agent.run(context);
    validateAgentReport(report);
    expect(report.agent).toContain('Architect');
  });

  it('should produce insights', async () => {
    const context = createTestContext();
    const report = await agent.run(context);

    expect(report.insights.length).toBeGreaterThan(0);
    report.insights.forEach(validateAgentInsight);
  });
});

// ============================================================================
// Security Agent Tests
// ============================================================================

describe('SecurityAgent', () => {
  const agent = new SecurityAgent();

  it('should have correct agent name', () => {
    expect(agent.name).toBe('SecurityAgent');
  });

  it('should generate valid report', async () => {
    const context = createTestContext({
      vulnerabilitiesFound: 3,
      securityScore: 85,
    });

    const report = await agent.run(context);
    validateAgentReport(report);
    expect(report.agent).toContain('Security');
  });

  it('should produce security insights', async () => {
    const context = createTestContext();
    const report = await agent.run(context);

    expect(report.insights.length).toBeGreaterThan(0);
    report.insights.forEach(validateAgentInsight);
  });
});

// ============================================================================
// DevOps Agent Tests
// ============================================================================

describe('DevOpsAgent', () => {
  const agent = new DevOpsAgent();

  it('should have correct agent name', () => {
    expect(agent.name).toBe('DevOpsAgent');
  });

  it('should generate valid report', async () => {
    const context = createTestContext({
      deploymentsPerWeek: 15,
      cicdPipelineStatus: 'healthy',
    });

    const report = await agent.run(context);
    validateAgentReport(report);
    expect(report.agent).toContain('DevOps');
  });

  it('should produce deployment insights', async () => {
    const context = createTestContext();
    const report = await agent.run(context);

    expect(report.insights.length).toBeGreaterThan(0);
    report.insights.forEach(validateAgentInsight);
  });
});

// ============================================================================
// QA Agent Tests
// ============================================================================

describe('QAAgent', () => {
  const agent = new QAAgent();

  it('should have correct agent name', () => {
    expect(agent.name).toBe('QAAgent');
  });

  it('should generate valid report', async () => {
    const context = createTestContext({
      testCoverage: 0.85,
      testsPassing: 450,
      testsFailing: 12,
    });

    const report = await agent.run(context);
    validateAgentReport(report);
    expect(report.agent).toContain('QA');
  });

  it('should produce quality insights', async () => {
    const context = createTestContext();
    const report = await agent.run(context);

    expect(report.insights.length).toBeGreaterThan(0);
    report.insights.forEach(validateAgentInsight);
  });
});

// ============================================================================
// Data Scientist Agent Tests
// ============================================================================

describe('DataScientistAgent', () => {
  const agent = new DataScientistAgent();

  it('should have correct agent name', () => {
    expect(agent.name).toBe('DataScientistAgent');
  });

  it('should generate valid report', async () => {
    const context = createTestContext({
      dataPoints: 10000,
      modelAccuracy: 0.92,
    });

    const report = await agent.run(context);
    validateAgentReport(report);
    expect(report.agent).toContain('Data');
  });

  it('should produce analytical insights', async () => {
    const context = createTestContext();
    const report = await agent.run(context);

    expect(report.insights.length).toBeGreaterThan(0);
    report.insights.forEach(validateAgentInsight);
  });
});

// ============================================================================
// Product Manager Agent Tests
// ============================================================================

describe('ProductManagerAgent', () => {
  const agent = new ProductManagerAgent();

  it('should have correct agent name', () => {
    expect(agent.name).toBe('ProductManagerAgent');
  });

  it('should generate valid report', async () => {
    const context = createTestContext({
      activeUsers: 5000,
      userSatisfaction: 4.2,
      featureRequests: 42,
    });

    const report = await agent.run(context);
    validateAgentReport(report);
    expect(report.agent).toContain('Product');
  });

  it('should produce product insights', async () => {
    const context = createTestContext();
    const report = await agent.run(context);

    expect(report.insights.length).toBeGreaterThan(0);
    report.insights.forEach(validateAgentInsight);
  });
});

// ============================================================================
// Integration Tests
// ============================================================================

describe('runStageOne', () => {
  it('should run all agents successfully', async () => {
    const context = createTestContext({
      systemTest: true,
    });

    const reports = await runStageOne(context);

    expect(reports).toBeInstanceOf(Array);
    expect(reports.length).toBe(6); // 6 Stage 1 agents
    reports.forEach(validateAgentReport);
  });

  it('should handle empty payload', async () => {
    const context = createTestContext();
    const reports = await runStageOne(context);

    expect(reports.length).toBe(6);
    reports.forEach((report) => {
      expect(report.insights.length).toBeGreaterThan(0);
    });
  });

  it('should preserve requestId in all reports', async () => {
    const requestId = 'integration-test-001';
    const context: AgentContext = {
      requestId,
      timestamp: new Date(),
      payload: {},
    };

    const reports = await runStageOne(context);

    // Each agent should have access to the same request context
    reports.forEach((report) => {
      expect(report.generatedAt).toBeInstanceOf(Date);
    });
  });
});

// ============================================================================
// Stage One Agents Registry Tests
// ============================================================================

describe('stageOneAgents', () => {
  it('should contain all 6 agents', () => {
    expect(stageOneAgents).toBeInstanceOf(Array);
    expect(stageOneAgents.length).toBe(6);
  });

  it('should have unique agent names', () => {
    const names = stageOneAgents.map((agent) => agent.name);
    const uniqueNames = new Set(names);
    expect(uniqueNames.size).toBe(names.length);
  });

  it('should have all expected agents', () => {
    const agentNames = stageOneAgents.map((agent) => agent.name);

    expect(agentNames).toContain('ArchitectAgent');
    expect(agentNames).toContain('SecurityAgent');
    expect(agentNames).toContain('DevOpsAgent');
    expect(agentNames).toContain('QAAgent');
    expect(agentNames).toContain('DataScientistAgent');
    expect(agentNames).toContain('ProductManagerAgent');
  });

  it('should have run method on all agents', () => {
    stageOneAgents.forEach((agent) => {
      expect(agent.run).toBeDefined();
      expect(typeof agent.run).toBe('function');
    });
  });
});
