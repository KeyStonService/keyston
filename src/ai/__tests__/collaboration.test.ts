/**
 * Agent Coordinator Tests
 * 
 * 測試 Agent 協作機制的各種場景
 * Tests various scenarios of agent collaboration mechanisms
 */

import { AgentCoordinator, AgentCollaboration, SyncBarrier } from '../collaboration/agent-coordinator.js';
import { AgentModule, AgentContext, AgentReport, AgentInsight } from '../types.js';

// Mock Agent 實現
// Mock Agent implementation
class MockAgent implements AgentModule {
  constructor(
    public readonly name: string,
    private insights: AgentInsight[],
    private delay: number = 0
  ) {}

  async run(context: AgentContext): Promise<AgentReport> {
    // 模擬處理時間
    // Simulate processing time
    if (this.delay > 0) {
      await new Promise(resolve => setTimeout(resolve, this.delay));
    }

    return {
      agent: this.name,
      insights: this.insights,
      generatedAt: new Date()
    };
  }
}

describe('AgentCoordinator', () => {
  let coordinator: AgentCoordinator;

  beforeEach(() => {
    coordinator = new AgentCoordinator();
  });

  afterEach(() => {
    coordinator.clearKnowledge();
  });

  describe('Sequential Execution', () => {
    it('should execute agents in sequence', async () => {
      const agent1 = new MockAgent('agent1', [
        { title: 'Insight 1', description: 'First insight', signal: 'info' }
      ]);
      const agent2 = new MockAgent('agent2', [
        { title: 'Insight 2', description: 'Second insight', signal: 'info' }
      ]);

      const collaboration: AgentCollaboration = {
        coordinatorId: 'test-seq-001',
        participants: [agent1, agent2],
        strategy: 'sequential'
      };

      const context: AgentContext = {
        requestId: 'test-req-001',
        timestamp: new Date()
      };

      const result = await coordinator.orchestrate(collaboration, context);

      expect(result.success).toBe(true);
      expect(result.strategy).toBe('sequential');
      expect(result.individualReports).toHaveLength(2);
      expect(result.allInsights).toHaveLength(2);
      expect(result.individualReports[0].agent).toBe('agent1');
      expect(result.individualReports[1].agent).toBe('agent2');
    });

    it('should share insights between sequential agents', async () => {
      const agent1 = new MockAgent('agent1', [
        { title: 'Security Issue', description: 'Found vulnerability', signal: 'error' }
      ]);
      const agent2 = new MockAgent('agent2', [
        { title: 'Fix Applied', description: 'Applied security fix', signal: 'info' }
      ]);

      const collaboration: AgentCollaboration = {
        coordinatorId: 'test-seq-002',
        participants: [agent1, agent2],
        strategy: 'sequential'
      };

      const context: AgentContext = {
        requestId: 'test-req-002',
        timestamp: new Date()
      };

      await coordinator.orchestrate(collaboration, context);

      // 檢查知識是否被共享
      // Check if knowledge was shared
      const sharedKnowledge = coordinator.getSharedKnowledge('agent2');
      expect(sharedKnowledge).toHaveLength(1);
      expect(sharedKnowledge[0].sourceAgent).toBe('agent1');
      expect(sharedKnowledge[0].insights[0].title).toBe('Security Issue');
    });
  });

  describe('Parallel Execution', () => {
    it('should execute agents in parallel', async () => {
      const agent1 = new MockAgent('agent1', [
        { title: 'Insight 1', description: 'First insight', signal: 'info' }
      ], 100);
      const agent2 = new MockAgent('agent2', [
        { title: 'Insight 2', description: 'Second insight', signal: 'info' }
      ], 100);
      const agent3 = new MockAgent('agent3', [
        { title: 'Insight 3', description: 'Third insight', signal: 'info' }
      ], 100);

      const collaboration: AgentCollaboration = {
        coordinatorId: 'test-par-001',
        participants: [agent1, agent2, agent3],
        strategy: 'parallel'
      };

      const context: AgentContext = {
        requestId: 'test-req-003',
        timestamp: new Date()
      };

      const startTime = Date.now();
      const result = await coordinator.orchestrate(collaboration, context);
      const executionTime = Date.now() - startTime;

      expect(result.success).toBe(true);
      expect(result.individualReports).toHaveLength(3);
      expect(result.allInsights).toHaveLength(3);
      // 並行執行應該比順序執行快
      // Parallel execution should be faster than sequential
      expect(executionTime).toBeLessThan(250); // Should be ~100ms, not 300ms
    });

    it('should handle parallel agent failures', async () => {
      const agent1 = new MockAgent('agent1', [
        { title: 'Success', description: 'OK', signal: 'info' }
      ]);
      const agent2: AgentModule = {
        name: 'failing-agent',
        async run() {
          throw new Error('Agent failure');
        }
      };

      const collaboration: AgentCollaboration = {
        coordinatorId: 'test-par-002',
        participants: [agent1, agent2],
        strategy: 'parallel'
      };

      const context: AgentContext = {
        requestId: 'test-req-004',
        timestamp: new Date()
      };

      const result = await coordinator.orchestrate(collaboration, context);

      expect(result.success).toBe(false);
      expect(result.allInsights[0].signal).toBe('error');
    });
  });

  describe('Conditional Execution', () => {
    it('should execute agents based on conditions', async () => {
      const agent1 = new MockAgent('agent1', [
        { title: 'Check 1', description: 'Initial check', signal: 'info' }
      ]);
      const agent2 = new MockAgent('agent2', [
        { title: 'Check 2', description: 'Follow-up check', signal: 'warn' }
      ]);
      const agent3 = new MockAgent('agent3', [
        { title: 'Check 3', description: 'Final check', signal: 'error' }
      ]);

      // 只有當前面的報告包含錯誤時才執行下一個
      // Only execute next agent if previous reports contain errors
      const condition = (reports: AgentReport[]) => {
        return reports.some(r => r.insights.some(i => i.signal === 'error'));
      };

      const collaboration: AgentCollaboration = {
        coordinatorId: 'test-cond-001',
        participants: [agent1, agent2, agent3],
        strategy: 'conditional',
        condition
      };

      const context: AgentContext = {
        requestId: 'test-req-005',
        timestamp: new Date()
      };

      const result = await coordinator.orchestrate(collaboration, context);

      expect(result.success).toBe(true);
      // agent1 執行（無條件），agent2 不執行（無 error），agent3 不執行
      // agent1 executes (unconditional), agent2 doesn't execute (no errors)
      expect(result.individualReports).toHaveLength(1);
      expect(result.individualReports[0].agent).toBe('agent1');
    });
  });

  describe('Iterative Execution', () => {
    it('should execute agents iteratively until condition met', async () => {
      let executionCount = 0;
      const agent = new MockAgent('iterative-agent', [
        { title: 'Iteration', description: 'Processing', signal: 'info' }
      ]);

      // 執行 3 次後停止
      // Stop after 3 executions
      const condition = (reports: AgentReport[]) => {
        executionCount++;
        return executionCount >= 3;
      };

      const collaboration: AgentCollaboration = {
        coordinatorId: 'test-iter-001',
        participants: [agent],
        strategy: 'iterative',
        condition,
        maxIterations: 10
      };

      const context: AgentContext = {
        requestId: 'test-req-006',
        timestamp: new Date()
      };

      const result = await coordinator.orchestrate(collaboration, context);

      expect(result.success).toBe(true);
      // 應該執行了 3 次
      // Should have executed 3 times
      expect(result.individualReports).toHaveLength(3);
    });

    it('should respect max iterations limit', async () => {
      const agent = new MockAgent('agent', [
        { title: 'Iteration', description: 'Never stops', signal: 'info' }
      ]);

      // 永遠不滿足的條件
      // Condition that's never met
      const condition = () => false;

      const collaboration: AgentCollaboration = {
        coordinatorId: 'test-iter-002',
        participants: [agent],
        strategy: 'iterative',
        condition,
        maxIterations: 3
      };

      const context: AgentContext = {
        requestId: 'test-req-007',
        timestamp: new Date()
      };

      const result = await coordinator.orchestrate(collaboration, context);

      expect(result.success).toBe(true);
      // 應該只執行最大次數
      // Should only execute max iterations
      expect(result.individualReports).toHaveLength(3);
    });
  });

  describe('Knowledge Sharing', () => {
    it('should share insights between agents', async () => {
      const insights: AgentInsight[] = [
        { title: 'Critical Bug', description: 'Found critical bug', signal: 'error' }
      ];

      await coordinator.shareInsights('agent1', ['agent2', 'agent3'], insights);

      const agent2Knowledge = coordinator.getSharedKnowledge('agent2');
      const agent3Knowledge = coordinator.getSharedKnowledge('agent3');

      expect(agent2Knowledge).toHaveLength(1);
      expect(agent3Knowledge).toHaveLength(1);
      expect(agent2Knowledge[0].sourceAgent).toBe('agent1');
      expect(agent2Knowledge[0].insights).toEqual(insights);
    });

    it('should not share insights with source agent', async () => {
      const insights: AgentInsight[] = [
        { title: 'Info', description: 'Some info', signal: 'info' }
      ];

      await coordinator.shareInsights('agent1', ['agent1', 'agent2'], insights);

      const agent1Knowledge = coordinator.getSharedKnowledge('agent1');
      const agent2Knowledge = coordinator.getSharedKnowledge('agent2');

      // agent1 不應該收到自己的 insights
      // agent1 should not receive its own insights
      expect(agent1Knowledge).toHaveLength(0);
      expect(agent2Knowledge).toHaveLength(1);
    });
  });

  describe('Synchronization Barrier', () => {
    it('should wait for all agents to arrive at barrier', async () => {
      const barrier: SyncBarrier = {
        id: 'barrier-001',
        requiredAgents: ['agent1', 'agent2', 'agent3'],
        timeout: 5000
      };

      // 模擬 agents 依序到達
      // Simulate agents arriving sequentially
      setTimeout(() => coordinator.arriveAtBarrier('barrier-001', 'agent1'), 10);
      setTimeout(() => coordinator.arriveAtBarrier('barrier-001', 'agent2'), 20);
      setTimeout(() => coordinator.arriveAtBarrier('barrier-001', 'agent3'), 30);

      await expect(coordinator.waitForBarrier(barrier)).resolves.toBeUndefined();
    });

    it('should timeout if not all agents arrive', async () => {
      const barrier: SyncBarrier = {
        id: 'barrier-002',
        requiredAgents: ['agent1', 'agent2', 'agent3'],
        timeout: 100
      };

      // 只有兩個 agents 到達
      // Only two agents arrive
      await coordinator.arriveAtBarrier('barrier-002', 'agent1');
      await coordinator.arriveAtBarrier('barrier-002', 'agent2');

      await expect(coordinator.waitForBarrier(barrier)).rejects.toThrow('Barrier timeout');
    });
  });

  describe('Error Handling', () => {
    it('should handle unknown strategy gracefully', async () => {
      const agent = new MockAgent('agent', [
        { title: 'Test', description: 'Test', signal: 'info' }
      ]);

      const collaboration: AgentCollaboration = {
        coordinatorId: 'test-error-001',
        participants: [agent],
        strategy: 'invalid-strategy' as any
      };

      const context: AgentContext = {
        requestId: 'test-req-008',
        timestamp: new Date()
      };

      const result = await coordinator.orchestrate(collaboration, context);

      expect(result.success).toBe(false);
      expect(result.allInsights[0].signal).toBe('error');
      expect(result.allInsights[0].description).toContain('Unknown collaboration strategy');
    });
  });

  describe('Performance Metrics', () => {
    it('should track execution time', async () => {
      const agent = new MockAgent('agent', [
        { title: 'Test', description: 'Test', signal: 'info' }
      ], 50);

      const collaboration: AgentCollaboration = {
        coordinatorId: 'test-perf-001',
        participants: [agent],
        strategy: 'sequential'
      };

      const context: AgentContext = {
        requestId: 'test-req-009',
        timestamp: new Date()
      };

      const result = await coordinator.orchestrate(collaboration, context);

      expect(result.executionTime).toBeGreaterThan(40);
      expect(result.executionTime).toBeLessThan(200);
    });
  });
});
