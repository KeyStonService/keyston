import { AgentContext, AgentModule } from './types.js';
import {
  ArchitectAgent,
  SecurityAgent,
  DevOpsAgent,
  QAAgent,
  DataScientistAgent,
  ProductManagerAgent,
} from './agents/index.js';

// Export Stage 1 agents and runner
export const stageOneAgents: AgentModule[] = [
  new ArchitectAgent(),
  new SecurityAgent(),
  new DevOpsAgent(),
  new QAAgent(),
  new DataScientistAgent(),
  new ProductManagerAgent(),
];

export async function runStageOne(context: AgentContext) {
  return Promise.all(stageOneAgents.map((agent) => agent.run(context)));
}

// Export Stage 2 collaboration functionality
export * from './collaboration/index.js';

// Re-export types for convenience
export * from './types.js';
