import { AgentContext, AgentInsight } from '../../types.js';
import { BaseAgent } from '../base-agent.js';
import { cweRules } from './rules/cwe.js';
import { customRules } from './rules/custom.js';
import { owaspRules } from './rules/owasp.js';
import { SecurityAuditor } from './auditor.js';
import { SecurityPatcher } from './patcher.js';
import { SecurityScanner } from './scanner.js';

export class SecurityAgent extends BaseAgent {
  public readonly name = 'SecurityAgent';
  private readonly scanner = new SecurityScanner();
  private readonly auditor = new SecurityAuditor();
  private readonly patcher = new SecurityPatcher();

  protected async evaluate(context: AgentContext): Promise<AgentInsight[]> {
    return [
      this.scanner.scan(context),
      this.auditor.audit(context),
      this.patcher.plan(context),
      this.ruleCoverageInsight()
    ];
  }

  private ruleCoverageInsight(): AgentInsight {
    return {
      title: 'Rule Coverage',
      description: 'OWASP Top 10, CWE Top picks, and custom controls are registered.',
      signal: 'info',
      data: {
        owasp: owaspRules.length,
        cwe: cweRules.length,
        custom: customRules.length
      }
    };
  }
}
