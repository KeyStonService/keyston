import { AgentContext, AgentInsight } from '../../types.js';
import { owaspRules } from './rules/owasp.js';
import { cweRules } from './rules/cwe.js';
import { customRules } from './rules/custom.js';

export class SecurityPatcher {
  plan(context: AgentContext): AgentInsight {
    const pending = this.extractPending(context);
    const coverage = pending.length === 0 ? 1 : Math.max(0.2, 1 - pending.length * 0.1);
    return {
      title: 'Security Patch Plan',
      description: pending.length === 0 ? 'No patches required' : 'Scheduled patch rollout',
      signal: coverage < 0.6 ? 'warn' : 'info',
      data: {
        pending,
        coverage,
        rules: [...owaspRules, ...cweRules, ...customRules],
      },
    };
  }

  private extractPending(context: AgentContext): string[] {
    const payload = context.payload ?? {};
    const pending = payload['pendingPatches'];
    if (Array.isArray(pending)) {
      return pending.filter((item): item is string => typeof item === 'string');
    }
    return [];
  }
}
