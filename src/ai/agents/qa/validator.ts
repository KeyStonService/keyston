import { AgentContext, AgentInsight } from '../../types.js';

export class QAValidator {
  validate(context: AgentContext): AgentInsight {
    const failures = this.extractFailures(context);
    return {
      title: 'Result Validation',
      description: failures.length === 0 ? 'All suites passed' : 'Failures detected',
      signal: failures.length === 0 ? 'info' : 'error',
      data: { failures }
    };
  }

  private extractFailures(context: AgentContext): string[] {
    const payload = context.payload ?? {};
    const failures = payload['qaFailures'];
    if (Array.isArray(failures)) {
      return failures.filter((failure): failure is string => typeof failure === 'string');
    }
    return [];
  }
}
