import { AgentContext, AgentInsight } from '../../types.js';

export class ArchitectAnalyzer {
  analyze(context: AgentContext): AgentInsight[] {
    const services = this.resolveServices(context);
    return [
      {
        title: 'Service Inventory',
        description: `Discovered ${services} service candidates for review.`,
        signal: services > 5 ? 'warn' : 'info'
      }
    ];
  }

  private resolveServices(context: AgentContext): number {
    const payload = context.payload ?? {};
    const declared = payload['services'];
    if (Array.isArray(declared)) {
      return declared.length;
    }
    if (typeof declared === 'number') {
      return declared;
    }
    return 0;
  }
}
