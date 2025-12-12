/**
 * Security Validator
 *
 * Detects security vulnerabilities in real-time:
 * - Hardcoded credentials
 * - SQL injection
 * - XSS vulnerabilities
 * - Path traversal
 * - Secrets exposure
 *
 * Avg latency: <30ms
 */

export class SecurityValidator {
  private patterns: SecurityPattern[];

  constructor() {
    this.patterns = this.loadSecurityPatterns();
  }

  async validate(context: ValidationContext): Promise<ValidationResult> {
    const { data } = context;
    const violations: string[] = [];
    const suggestions: string[] = [];
    let maxSeverity: Severity = 'low';

    // Convert data to string for pattern matching
    const dataString = this.stringify(data);

    // Run all security checks
    for (const pattern of this.patterns) {
      const matches = this.checkPattern(dataString, pattern);

      if (matches.length > 0) {
        violations.push(...matches.map(m => `${pattern.name}: ${m}`));
        suggestions.push(pattern.fix);

        if (this.isMoreSevere(pattern.severity, maxSeverity)) {
          maxSeverity = pattern.severity;
        }
      }
    }

    return {
      validatorName: 'security',
      passed: violations.length === 0,
      violations,
      severity: maxSeverity,
      suggestions: [...new Set(suggestions)] // Remove duplicates
    };
  }

  private loadSecurityPatterns(): SecurityPattern[] {
    return [
      // Hardcoded credentials
      {
        name: 'Hardcoded Password',
        pattern: /password\s*[=:]\s*['"][^'"]+['"]/gi,
        severity: 'critical',
        fix: 'Use environment variables or secure vault (e.g., process.env.PASSWORD)'
      },
      {
        name: 'Hardcoded API Key',
        pattern: /(?:api[_-]?key|apikey|access[_-]?token)\s*[=:]\s*['"][^'"]+['"]/gi,
        severity: 'critical',
        fix: 'Store API keys in environment variables or secrets manager'
      },
      {
        name: 'Bearer Token in Code',
        pattern: /bearer\s+[a-zA-Z0-9_-]{20,}/gi,
        severity: 'critical',
        fix: 'Never hardcode tokens; use secure credential storage'
      },

      // SQL Injection
      {
        name: 'SQL Injection Risk',
        pattern: /(?:SELECT|INSERT|UPDATE|DELETE).*(?:\+|concat)/gi,
        severity: 'critical',
        fix: 'Use parameterized queries or ORM instead of string concatenation'
      },
      {
        name: 'Raw SQL Query',
        pattern: /\.query\([^)]*\+[^)]*\)/gi,
        severity: 'high',
        fix: 'Use prepared statements: .query("SELECT * FROM users WHERE id = ?", [id])'
      },

      // XSS Vulnerabilities
      {
        name: 'Unsafe HTML Rendering',
        pattern: /innerHTML\s*=|dangerouslySetInnerHTML/gi,
        severity: 'high',
        fix: 'Sanitize user input or use safe rendering methods'
      },
      {
        name: 'eval() Usage',
        pattern: /\beval\s*\(/gi,
        severity: 'critical',
        fix: 'Avoid eval(); use JSON.parse() or alternative safe methods'
      },

      // Path Traversal
      {
        name: 'Path Traversal Risk',
        pattern: /\.\.[/\\]/g,
        severity: 'high',
        fix: 'Validate and sanitize file paths; use path.normalize()'
      },

      // Secrets Exposure
      {
        name: 'Private Key in Code',
        pattern: /-----BEGIN (?:RSA )?PRIVATE KEY-----/g,
        severity: 'critical',
        fix: 'Never commit private keys; use secure key management'
      },
      {
        name: 'AWS Access Key',
        pattern: /AKIA[0-9A-Z]{16}/g,
        severity: 'critical',
        fix: 'Revoke exposed key immediately and use IAM roles'
      },

      // Insecure Randomness
      {
        name: 'Weak Random Generation',
        pattern: /Math\.random\(\)/gi,
        severity: 'medium',
        fix: 'Use crypto.randomBytes() for security-sensitive randomness'
      },

      // Command Injection
      {
        name: 'Command Injection Risk',
        pattern: /exec\(|spawn\([^)]*\+/gi,
        severity: 'critical',
        fix: 'Avoid shell execution with user input; use safe alternatives'
      },

      // Debugging Code
      {
        name: 'Debug Code in Production',
        pattern: /console\.(log|debug|trace)/gi,
        severity: 'low',
        fix: 'Remove debug logs or use proper logger with levels'
      }
    ];
  }

  private checkPattern(data: string, pattern: SecurityPattern): string[] {
    const matches: string[] = [];
    const regex = new RegExp(pattern.pattern);
    let match;

    while ((match = regex.exec(data)) !== null) {
      matches.push(match[0]);
    }

    return matches;
  }

  private stringify(data: unknown): string {
    if (typeof data === 'string') return data;
    if (typeof data === 'object') return JSON.stringify(data, null, 2);
    return String(data);
  }

  private isMoreSevere(a: Severity, b: Severity): boolean {
    const levels = { low: 0, medium: 1, high: 2, critical: 3 };
    return levels[a] > levels[b];
  }
}

interface SecurityPattern {
  name: string;
  pattern: RegExp;
  severity: Severity;
  fix: string;
}

type Severity = 'low' | 'medium' | 'high' | 'critical';

interface ValidationContext {
  eventId: string;
  data: unknown;
  metadata?: Record<string, unknown>;
}

interface ValidationResult {
  validatorName: string;
  passed: boolean;
  violations: string[];
  severity?: Severity;
  suggestions?: string[];
}
