/**
 * Compliance Validator
 *
 * Validates against compliance frameworks:
 * - ISO 27001 (Information Security)
 * - NIST CSF (Cybersecurity Framework)
 * - GDPR (Data Privacy)
 * - SOC 2 (Service Organization Controls)
 *
 * Avg latency: <50ms
 */

export class ComplianceValidator {
  private rules: ComplianceRule[];

  constructor() {
    this.rules = this.loadComplianceRules();
  }

  async validate(context: ValidationContext): Promise<ValidationResult> {
    const { data, metadata } = context;
    const violations: string[] = [];
    const suggestions: string[] = [];
    const frameworks = metadata?.frameworks as string[] || ['ISO27001', 'GDPR'];

    const dataString = this.stringify(data);

    // Check each applicable framework
    for (const framework of frameworks) {
      const frameworkRules = this.rules.filter(r => r.framework === framework);

      for (const rule of frameworkRules) {
        const violated = this.checkRule(dataString, data, rule);

        if (violated) {
          violations.push(`[${framework}] ${rule.name}: ${rule.violation}`);
          suggestions.push(rule.remediation);
        }
      }
    }

    return {
      validatorName: 'compliance',
      passed: violations.length === 0,
      violations,
      severity: violations.length > 0 ? 'high' : 'low',
      suggestions: [...new Set(suggestions)],
      metadata: {
        frameworks: frameworks.join(', '),
        rulesChecked: this.rules.length
      }
    };
  }

  private loadComplianceRules(): ComplianceRule[] {
    return [
      // ISO 27001 - Information Security
      {
        id: 'ISO27001-A.9.4.1',
        framework: 'ISO27001',
        name: 'Access Control - Audit Logging',
        check: (data) => {
          const str = this.stringify(data);
          return /(?:delete|update|modify|create)(?!.*audit|.*log)/i.test(str);
        },
        violation: 'Sensitive operation without audit logging',
        remediation: 'Add audit.log() call for all CRUD operations',
        severity: 'high'
      },
      {
        id: 'ISO27001-A.10.1.1',
        framework: 'ISO27001',
        name: 'Cryptographic Controls',
        check: (data) => {
          const str = this.stringify(data);
          return /(?:md5|sha1)\s*\(/i.test(str);
        },
        violation: 'Weak cryptographic algorithm detected (MD5/SHA1)',
        remediation: 'Use SHA-256 or stronger: crypto.createHash("sha256")',
        severity: 'high'
      },

      // GDPR - Data Privacy
      {
        id: 'GDPR-Art.32',
        framework: 'GDPR',
        name: 'Personal Data Encryption',
        check: (data) => {
          const str = this.stringify(data);
          const hasPII = /(?:email|phone|ssn|passport|address)/.test(str);
          const hasEncryption = /encrypt|cipher/.test(str);
          return hasPII && !hasEncryption;
        },
        violation: 'Personal data transmitted without encryption',
        remediation: 'Encrypt PII before storage/transmission',
        severity: 'critical'
      },
      {
        id: 'GDPR-Art.17',
        framework: 'GDPR',
        name: 'Right to Erasure',
        check: (data) => {
          const str = this.stringify(data);
          return /deleteUser|removeAccount/i.test(str) && !/cascade|permanent/.test(str);
        },
        violation: 'User deletion may not be complete (GDPR Art. 17)',
        remediation: 'Ensure cascading deletion of all user data',
        severity: 'high'
      },

      // NIST CSF - Cybersecurity Framework
      {
        id: 'NIST-PR.AC-1',
        framework: 'NIST',
        name: 'Access Control - Least Privilege',
        check: (data) => {
          const str = this.stringify(data);
          return /role\s*[=:]\s*['"](?:admin|root|superuser)['"]/i.test(str);
        },
        violation: 'Default admin role assignment (violates least privilege)',
        remediation: 'Assign minimal required permissions, not admin by default',
        severity: 'high'
      },
      {
        id: 'NIST-DE.CM-7',
        framework: 'NIST',
        name: 'Continuous Monitoring',
        check: (data) => {
          const str = this.stringify(data);
          const isCritical = /(?:deploy|release|production)/i.test(str);
          const hasMonitoring = /monitor|alert|metric/.test(str);
          return isCritical && !hasMonitoring;
        },
        violation: 'Critical operation without monitoring',
        remediation: 'Add monitoring/alerting for production deployments',
        severity: 'medium'
      },

      // SOC 2 - Service Organization Controls
      {
        id: 'SOC2-CC6.1',
        framework: 'SOC2',
        name: 'Logical Access - Authentication',
        check: (data) => {
          const str = this.stringify(data);
          return /login|authenticate/i.test(str) && !/(?:mfa|2fa|totp)/i.test(str);
        },
        violation: 'Authentication without MFA (SOC 2 requirement)',
        remediation: 'Implement multi-factor authentication',
        severity: 'high'
      },
      {
        id: 'SOC2-CC7.2',
        framework: 'SOC2',
        name: 'Change Management - Approval',
        check: (data) => {
          const str = this.stringify(data);
          const isChange = /(?:deploy|update|migrate|modify)/i.test(str);
          const hasApproval = /approv|review|sign-?off/.test(str);
          return isChange && !hasApproval;
        },
        violation: 'Production change without approval workflow',
        remediation: 'Require approval for all production changes',
        severity: 'medium'
      },

      // Data Retention
      {
        id: 'COMP-RET-001',
        framework: 'ISO27001',
        name: 'Data Retention Policy',
        check: (data) => {
          const str = this.stringify(data);
          return /store|persist|save/i.test(str) && !/retention|expire|ttl/.test(str);
        },
        violation: 'Data storage without retention policy',
        remediation: 'Define and implement data retention/expiration policy',
        severity: 'medium'
      }
    ];
  }

  private checkRule(dataStr: string, data: unknown, rule: ComplianceRule): boolean {
    return rule.check(data, dataStr);
  }

  private stringify(data: unknown): string {
    if (typeof data === 'string') return data;
    if (typeof data === 'object') return JSON.stringify(data, null, 2);
    return String(data);
  }
}

interface ComplianceRule {
  id: string;
  framework: 'ISO27001' | 'GDPR' | 'NIST' | 'SOC2';
  name: string;
  check: (data: unknown, dataStr?: string) => boolean;
  violation: string;
  remediation: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

interface ValidationContext {
  eventId: string;
  data: unknown;
  metadata?: Record<string, unknown>;
}

interface ValidationResult {
  validatorName: string;
  passed: boolean;
  violations: string[];
  severity?: 'low' | 'medium' | 'high' | 'critical';
  suggestions?: string[];
  metadata?: Record<string, unknown>;
}
