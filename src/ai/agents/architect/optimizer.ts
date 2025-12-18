import { AgentContext, AgentInsight } from '../../types.js';

export class ArchitectOptimizer {
  optimize(context: AgentContext): AgentInsight {
    const load = this.estimateLoad(context);
    const recommendation = load > 0.7 ? 'Introduce caching layer' : 'Current topology is stable';
    return {
      title: 'Topology Optimization',
      description: recommendation,
      signal: load > 0.85 ? 'warn' : 'info',
      data: { computedLoad: load }
    };
  }

  private estimateLoad(context: AgentContext): number {
    const payload = context.payload ?? {};
    const load = payload['loadIndex'];
    if (typeof load === 'number') {
      return Math.max(0, Math.min(1, load));
    }
    return 0.42;
  }
}
