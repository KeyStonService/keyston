import { AgentContext, AgentInsight } from '../../types.js';

export class DevOpsScaler {
  scale(context: AgentContext): AgentInsight {
    const demand = this._estimateDemand(context);
    const desiredReplicas = Math.max(1, Math.ceil(demand * 10));
    return {
      title: 'Auto Scaling Plan',
      description: `Targeting ${desiredReplicas} replicas to satisfy projected load`,
      signal: demand > 0.7 ? 'warn' : 'info',
      data: { demandIndex: demand, desiredReplicas },
    };
  }

  private _estimateDemand(context: AgentContext): number {
    const payload = context.payload ?? {};
    const demand = payload['demandIndex'];
    if (typeof demand === 'number') {
      return Math.max(0, Math.min(1, demand));
    }
    return 0.5;
  }
}
