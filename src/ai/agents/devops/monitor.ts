import { AgentContext, AgentInsight } from '../../types.js';

export class DevOpsMonitor {
  monitor(context: AgentContext): AgentInsight {
    const latency = this._readMetric(context, 'latencyMs');
    const errors = this._readMetric(context, 'errorRate');
    return {
      title: 'Observability Snapshot',
      description: `Latency ${latency}ms, error-rate ${errors}%`,
      signal: errors > 1 ? 'warn' : 'info',
    };
  }

  private _readMetric(context: AgentContext, key: string): number {
    const payload = context.payload ?? {};
    const metric = payload[key];
    if (typeof metric === 'number') {
      return metric;
    }
    return key === 'latencyMs' ? 120 : 0.2;
  }
}
