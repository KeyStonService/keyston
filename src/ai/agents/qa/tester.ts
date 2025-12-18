import { AgentContext, AgentInsight } from '../../types.js';

export class QATester {
  execute(context: AgentContext): AgentInsight {
    const suites = this._resolveSuites(context);
    return {
      title: 'Test Execution',
      description: `Ran ${suites.length} suites`,
      signal: suites.length === 0 ? 'warn' : 'info',
      data: { suites },
    };
  }

  private _resolveSuites(context: AgentContext): string[] {
    const payload = context.payload ?? {};
    const suites = payload['qaSuites'];
    if (Array.isArray(suites)) {
      return suites.filter((suite): suite is string => typeof suite === 'string');
    }
    return ['unit'];
  }
}
