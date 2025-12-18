import { AgentContext, AgentInsight } from '../../types.js';

export class SecurityAuditor {
  audit(context: AgentContext): AgentInsight {
    const policies = this.resolvePolicies(context);
    const compliant = policies.every((policy) => policy.passing);
    const failing = policies.filter((policy) => !policy.passing).map((policy) => policy.id);
    return {
      title: 'Security Audit',
      description: compliant ? 'All policies satisfied' : 'Policy failures detected',
      signal: compliant ? 'info' : 'error',
      data: { failingPolicies: failing }
    };
  }

  private resolvePolicies(context: AgentContext): Array<{ id: string; passing: boolean }> {
    const payload = context.payload ?? {};
    const policies = payload['policyResults'];
    if (Array.isArray(policies)) {
      return policies
        .filter((item): item is { id: string; passing: boolean } =>
          typeof item?.id === 'string' && typeof item?.passing === 'boolean'
        );
    }
    return [];
  }
}
