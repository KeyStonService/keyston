import { AgentContext, AgentInsight } from '../../types.js';

export class SecurityScanner {
  scan(context: AgentContext): AgentInsight {
    const issues = this.detectIssues(context);
    return {
      title: 'Vulnerability Scan',
      description: `Identified ${issues} potential weaknesses`,
      signal: issues > 0 ? 'warn' : 'info'
    };
  }

  private detectIssues(context: AgentContext): number {
    const payload = context.payload ?? {};
    const findings = payload['securityFindings'];
    if (Array.isArray(findings)) {
      return findings.length;
    }
    return 0;
  }
}
