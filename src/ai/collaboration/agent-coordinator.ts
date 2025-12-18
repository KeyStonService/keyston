/**
 * Agent Coordinator - Stage 2 Multi-Agent Collaboration
 * 
 * 實現多 Agent 協作機制，支持順序、並行、條件分支和迭代執行策略。
 * Implements multi-agent collaboration mechanisms supporting sequential, parallel,
 * conditional branching, and iterative execution strategies.
 */

import { AgentModule, AgentContext, AgentReport, AgentInsight } from '../types.js';

/**
 * 協作策略類型
 * Collaboration strategy types
 */
export type CollaborationStrategy =
  | 'sequential'    // 順序執行 - Execute agents one after another
  | 'parallel'      // 並行執行 - Execute agents concurrently
  | 'conditional'   // 條件分支 - Execute based on conditions
  | 'iterative';    // 迭代執行 - Execute agents repeatedly until condition met

/**
 * 同步屏障 - 用於協調多個 Agent 的執行
 * Synchronization barrier for coordinating agent execution
 */
export interface SyncBarrier {
  id: string;
  requiredAgents: string[];
  timeout?: number; // milliseconds
}

/**
 * Agent 協作配置
 * Agent collaboration configuration
 */
export interface AgentCollaboration {
  coordinatorId: string;
  participants: AgentModule[];
  strategy: CollaborationStrategy;
  syncBarrier?: SyncBarrier;
  condition?: (reports: AgentReport[]) => boolean;
  maxIterations?: number;
}

/**
 * 聚合報告 - 包含所有參與 Agent 的 insights
 * Aggregated report containing insights from all participating agents
 */
export interface AggregatedReport {
  coordinatorId: string;
  strategy: CollaborationStrategy;
  allInsights: AgentInsight[];
  individualReports: AgentReport[];
  executionTime: number;
  success: boolean;
}

/**
 * Agent 洞察 - 用於 Agent 間共享知識
 * Agent insight for knowledge sharing between agents
 */
export interface AgentKnowledge {
  sourceAgent: string;
  timestamp: Date;
  insights: AgentInsight[];
  metadata?: Record<string, unknown>;
}

/**
 * Agent Coordinator - 協調多個 Agent 的協作執行
 * Coordinates collaborative execution of multiple agents
 */
export class AgentCoordinator {
  private knowledgeBase: Map<string, AgentKnowledge[]> = new Map();
  private barrierStatus: Map<string, Set<string>> = new Map();

  /**
   * 編排 Agent 協作執行
   * Orchestrate agent collaboration execution
   */
  async orchestrate(
    collaboration: AgentCollaboration,
    context: AgentContext
  ): Promise<AggregatedReport> {
    const startTime = Date.now();
    let reports: AgentReport[] = [];

    try {
      switch (collaboration.strategy) {
        case 'sequential':
          reports = await this.executeSequential(collaboration.participants, context);
          break;
        case 'parallel':
          reports = await this.executeParallel(collaboration.participants, context);
          break;
        case 'conditional':
          reports = await this.executeConditional(
            collaboration.participants,
            context,
            collaboration.condition
          );
          break;
        case 'iterative':
          reports = await this.executeIterative(
            collaboration.participants,
            context,
            collaboration.condition,
            collaboration.maxIterations || 5
          );
          break;
        default:
          throw new Error(`Unknown collaboration strategy: ${collaboration.strategy}`);
      }

      const allInsights = reports.flatMap(r => r.insights);
      const executionTime = Date.now() - startTime;

      return {
        coordinatorId: collaboration.coordinatorId,
        strategy: collaboration.strategy,
        allInsights,
        individualReports: reports,
        executionTime,
        success: true
      };
    } catch (error) {
      const executionTime = Date.now() - startTime;
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      return {
        coordinatorId: collaboration.coordinatorId,
        strategy: collaboration.strategy,
        allInsights: [{
          title: 'Orchestration Failed',
          description: errorMessage,
          signal: 'error'
        }],
        individualReports: reports,
        executionTime,
        success: false
      };
    }
  }

  /**
   * 順序執行 Agents
   * Execute agents sequentially
   */
  private async executeSequential(
    agents: AgentModule[],
    context: AgentContext
  ): Promise<AgentReport[]> {
    const reports: AgentReport[] = [];

    for (const agent of agents) {
      const report = await agent.run(context);
      reports.push(report);
      
      // 將 insights 加入知識庫供後續 agents 參考
      // Add insights to knowledge base for subsequent agents
      await this.shareInsights(agent.name, agents.map(a => a.name), report.insights);
    }

    return reports;
  }

  /**
   * 並行執行 Agents
   * Execute agents in parallel
   */
  private async executeParallel(
    agents: AgentModule[],
    context: AgentContext
  ): Promise<AgentReport[]> {
    const reportPromises = agents.map(agent => agent.run(context));
    const reports = await Promise.all(reportPromises);

    // 並行執行完成後共享所有 insights
    // Share all insights after parallel execution completes
    for (let i = 0; i < agents.length; i++) {
      await this.shareInsights(
        agents[i].name,
        agents.map(a => a.name),
        reports[i].insights
      );
    }

    return reports;
  }

  /**
   * 條件執行 Agents
   * Execute agents based on conditions
   */
  private async executeConditional(
    agents: AgentModule[],
    context: AgentContext,
    condition?: (reports: AgentReport[]) => boolean
  ): Promise<AgentReport[]> {
    const reports: AgentReport[] = [];

    for (let i = 0; i < agents.length; i++) {
      const agent = agents[i];
      
      // 第一個 agent 總是執行，之後的 agent 檢查條件
      // First agent always executes, subsequent agents check condition
      if (i > 0 && condition && !condition(reports)) {
        continue;
      }

      const report = await agent.run(context);
      reports.push(report);
      await this.shareInsights(agent.name, agents.map(a => a.name), report.insights);
    }

    return reports;
  }

  /**
   * 迭代執行 Agents
   * Execute agents iteratively
   */
  private async executeIterative(
    agents: AgentModule[],
    context: AgentContext,
    condition?: (reports: AgentReport[]) => boolean,
    maxIterations: number = 5
  ): Promise<AgentReport[]> {
    let allReports: AgentReport[] = [];
    let iteration = 0;

    while (iteration < maxIterations) {
      iteration++;
      
      // 每次迭代執行所有 agents
      // Execute all agents in each iteration
      const iterationReports = await this.executeSequential(agents, context);
      allReports = allReports.concat(iterationReports);

      // 檢查是否滿足停止條件
      // Check if stop condition is met
      if (condition && condition(iterationReports)) {
        break;
      }
    }

    return allReports;
  }

  /**
   * 等待同步屏障
   * Wait for synchronization barrier
   */
  async waitForBarrier(barrier: SyncBarrier): Promise<void> {
    return new Promise((resolve, reject) => {
      const checkInterval = 100; // Check every 100ms
      const startTime = Date.now();
      const timeout = barrier.timeout || 30000; // Default 30s timeout

      const intervalId = setInterval(() => {
        const arrivedAgents = this.barrierStatus.get(barrier.id);
        
        // 檢查是否所有 agents 都到達
        // Check if all agents have arrived
        if (arrivedAgents && barrier.requiredAgents.every(a => arrivedAgents.has(a))) {
          clearInterval(intervalId);
          this.barrierStatus.delete(barrier.id);
          resolve();
          return;
        }

        // 檢查超時
        // Check timeout
        if (Date.now() - startTime > timeout) {
          clearInterval(intervalId);
          reject(new Error(`Barrier timeout: ${barrier.id}`));
        }
      }, checkInterval);
    });
  }

  /**
   * Agent 到達同步屏障
   * Agent arrives at synchronization barrier
   */
  async arriveAtBarrier(barrierId: string, agentName: string): Promise<void> {
    if (!this.barrierStatus.has(barrierId)) {
      this.barrierStatus.set(barrierId, new Set());
    }
    const arrivedAgents = this.barrierStatus.get(barrierId);
    if (arrivedAgents) {
      arrivedAgents.add(agentName);
    }
  }

  /**
   * 共享 Insights 給其他 Agents
   * Share insights with other agents
   */
  async shareInsights(
    sourceAgent: string,
    targetAgents: string[],
    insights: AgentInsight[]
  ): Promise<void> {
    const knowledge: AgentKnowledge = {
      sourceAgent,
      timestamp: new Date(),
      insights,
      metadata: {
        targets: targetAgents
      }
    };

    // 為每個目標 agent 存儲知識
    // Store knowledge for each target agent
    for (const targetAgent of targetAgents) {
      if (targetAgent !== sourceAgent) {
        if (!this.knowledgeBase.has(targetAgent)) {
          this.knowledgeBase.set(targetAgent, []);
        }
        const targetKnowledge = this.knowledgeBase.get(targetAgent);
        if (targetKnowledge) {
          targetKnowledge.push(knowledge);
        }
      }
    }
  }

  /**
   * 獲取可用的共享知識
   * Get available shared knowledge
   */
  getSharedKnowledge(agentName: string): AgentKnowledge[] {
    return this.knowledgeBase.get(agentName) || [];
  }

  /**
   * 清除知識庫
   * Clear knowledge base
   */
  clearKnowledge(): void {
    this.knowledgeBase.clear();
    this.barrierStatus.clear();
  }
}
