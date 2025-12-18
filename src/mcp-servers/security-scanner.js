#!/usr/bin/env node

/**
 * Security Scanner MCP Server
 * Enterprise-grade security scanning for vulnerabilities, dependencies, and secrets
 *
 * @module security-scanner
 * @author SynergyMesh Team
 * @license MIT
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ErrorCode,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

// Validation schemas
const ScanVulnerabilitiesSchema = z.object({
  code: z.string().min(1, 'Code content is required'),
  language: z.string().optional().default('javascript'),
  severity: z.enum(['critical', 'high', 'medium', 'low', 'all']).optional().default('all'),
});

const CheckDependenciesSchema = z.object({
  dependencies: z.record(z.string()).or(
    z.array(
      z.object({
        name: z.string(),
        version: z.string(),
      })
    )
  ),
  ecosystem: z.string().optional().default('npm'),
});

const AnalyzeSecretsSchema = z.object({
  content: z.string().min(1, 'Content is required'),
  strictMode: z.boolean().optional().default(true),
});

/**
 * Security scanning engine
 */
class SecurityScanner {
  constructor() {
    this.vulnerabilityPatterns = this._initVulnerabilityPatterns();
    this.secretPatterns = this._initSecretPatterns();
  }

  /**
   * Scan code vulnerabilities
   */
  scanVulnerabilities(code, language = 'javascript', severity = 'all') {
    const scan = {
      timestamp: new Date().toISOString(),
      language,
      severity,
      vulnerabilities: [],
      summary: {
        total: 0,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
    };

    // Scan for SQL injection
    const sqlInjection = this._detectSQLInjection(code);
    scan.vulnerabilities.push(...sqlInjection);

    // Scan for XSS
    const xss = this._detectXSS(code);
    scan.vulnerabilities.push(...xss);

    // Scan for insecure crypto
    const crypto = this._detectInsecureCrypto(code);
    scan.vulnerabilities.push(...crypto);

    // Scan for command injection
    const cmdInjection = this._detectCommandInjection(code);
    scan.vulnerabilities.push(...cmdInjection);

    // Scan for path traversal
    const pathTraversal = this._detectPathTraversal(code);
    scan.vulnerabilities.push(...pathTraversal);

    // Scan for insecure deserialization
    const deserialization = this._detectInsecureDeserialization(code);
    scan.vulnerabilities.push(...deserialization);

    // Filter by severity
    if (severity !== 'all') {
      scan.vulnerabilities = scan.vulnerabilities.filter((v) => v.severity === severity);
    }

    // Calculate summary
    for (const vuln of scan.vulnerabilities) {
      scan.summary.total++;
      scan.summary[vuln.severity]++;
    }

    return scan;
  }

  /**
   * Check dependency security
   */
  checkDependencies(dependencies, ecosystem = 'npm') {
    const check = {
      timestamp: new Date().toISOString(),
      ecosystem,
      totalDependencies: 0,
      vulnerableDependencies: [],
      summary: {
        vulnerable: 0,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
      },
      recommendations: [],
    };

    // Normalize dependencies format
    const deps = Array.isArray(dependencies)
      ? dependencies
      : Object.entries(dependencies).map(([name, version]) => ({ name, version }));

    check.totalDependencies = deps.length;

    // Check each dependency
    for (const dep of deps) {
      const vulns = this._checkDependencyVulnerabilities(dep, ecosystem);
      if (vulns.length > 0) {
        check.vulnerableDependencies.push({
          name: dep.name,
          version: dep.version,
          vulnerabilities: vulns,
        });

        for (const vuln of vulns) {
          check.summary.vulnerable++;
          check.summary[vuln.severity]++;
        }
      }
    }

    // Generate recommendations
    check.recommendations = this._generateDependencyRecommendations(check);

    return check;
  }

  /**
   * Analyze secrets in code
   */
  analyzeSecrets(content, strictMode = true) {
    const analysis = {
      timestamp: new Date().toISOString(),
      strictMode,
      secrets: [],
      summary: {
        total: 0,
        highConfidence: 0,
        mediumConfidence: 0,
        lowConfidence: 0,
      },
    };

    // Scan for various types of secrets
    for (const [type, pattern] of Object.entries(this.secretPatterns)) {
      const matches = content.matchAll(pattern.regex);

      for (const match of matches) {
        const secret = {
          type,
          value: this._maskSecret(match[0]),
          line: this._findLineNumber(content, match.index),
          confidence: pattern.confidence,
          severity: pattern.severity,
          recommendation: pattern.recommendation,
        };

        if (!strictMode || pattern.confidence === 'high') {
          analysis.secrets.push(secret);
          analysis.summary.total++;
          analysis.summary[`${pattern.confidence}Confidence`]++;
        }
      }
    }

    return analysis;
  }

  // Private helper methods

  _initVulnerabilityPatterns() {
    return {
      sqlInjection: [
        /\.query\s*\(\s*['"`][^'"`]*\$\{[^}]*\}[^'"`]*['"`]/g,
        /\.query\s*\(\s*['"`][^'"`]*\+[^)]+\)/g,
      ],
      xss: [
        /innerHTML\s*=\s*[^;]+/g,
        /document\.write\s*\([^)]*\+[^)]*\)/g,
        /\$\([^)]+\)\.html\s*\([^)]*\+[^)]*\)/g,
      ],
      commandInjection: [
        /exec\s*\(\s*['"`][^'"`]*\$\{[^}]*\}[^'"`]*['"`]/g,
        /spawn\s*\(\s*['"`][^'"`]*\$\{[^}]*\}[^'"`]*['"`]/g,
      ],
    };
  }

  _initSecretPatterns() {
    return {
      'AWS Access Key': {
        regex: /AKIA[0-9A-Z]{16}/g,
        confidence: 'high',
        severity: 'critical',
        recommendation: 'Use AWS IAM roles or environment variables',
      },
      'API Key': {
        regex: /['"]?api[_-]?key['"]?\s*[:=]\s*['"]([a-zA-Z0-9_-]{20,})['"]/gi,
        confidence: 'medium',
        severity: 'high',
        recommendation: 'Store API keys in environment variables',
      },
      'Private Key': {
        regex: /-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----/g,
        confidence: 'high',
        severity: 'critical',
        recommendation: 'Never commit private keys to source control',
      },
      Password: {
        regex: /['"]?password['"]?\s*[:=]\s*['"]([^'"]{8,})['"]/gi,
        confidence: 'medium',
        severity: 'high',
        recommendation: 'Use environment variables and secret management',
      },
      'JWT Token': {
        regex: /eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+/g,
        confidence: 'high',
        severity: 'high',
        recommendation: 'Never commit tokens to source control',
      },
      'Database URL': {
        regex: /(postgres|mysql|mongodb):\/\/[^:]+:[^@]+@[^\s'"]+/gi,
        confidence: 'high',
        severity: 'critical',
        recommendation: 'Use environment variables for database credentials',
      },
    };
  }

  _detectSQLInjection(code) {
    const vulnerabilities = [];

    for (const pattern of this.vulnerabilityPatterns.sqlInjection) {
      const matches = code.matchAll(pattern);
      for (const match of matches) {
        vulnerabilities.push({
          type: 'SQL Injection',
          severity: 'critical',
          line: this._findLineNumber(code, match.index),
          code: match[0],
          description: 'Potential SQL injection vulnerability detected',
          remediation: 'Use parameterized queries or prepared statements',
          cwe: 'CWE-89',
          owasp: 'A03:2021 - Injection',
        });
      }
    }

    return vulnerabilities;
  }

  _detectXSS(code) {
    const vulnerabilities = [];

    for (const pattern of this.vulnerabilityPatterns.xss) {
      const matches = code.matchAll(pattern);
      for (const match of matches) {
        vulnerabilities.push({
          type: 'Cross-Site Scripting (XSS)',
          severity: 'high',
          line: this._findLineNumber(code, match.index),
          code: match[0],
          description: 'Potential XSS vulnerability detected',
          remediation: 'Sanitize user input and use safe DOM manipulation methods',
          cwe: 'CWE-79',
          owasp: 'A03:2021 - Injection',
        });
      }
    }

    return vulnerabilities;
  }

  _detectInsecureCrypto(code) {
    const vulnerabilities = [];

    if (/md5|sha1(?!\d)/gi.test(code)) {
      vulnerabilities.push({
        type: 'Weak Cryptographic Hash',
        severity: 'medium',
        line: this._findLineNumber(code, code.search(/md5|sha1(?!\d)/gi)),
        code: 'MD5/SHA1 usage',
        description: 'Use of weak cryptographic hash function',
        remediation: 'Use SHA-256 or stronger hash functions',
        cwe: 'CWE-327',
        owasp: 'A02:2021 - Cryptographic Failures',
      });
    }

    return vulnerabilities;
  }

  _detectCommandInjection(code) {
    const vulnerabilities = [];

    for (const pattern of this.vulnerabilityPatterns.commandInjection) {
      const matches = code.matchAll(pattern);
      for (const match of matches) {
        vulnerabilities.push({
          type: 'Command Injection',
          severity: 'critical',
          line: this._findLineNumber(code, match.index),
          code: match[0],
          description: 'Potential command injection vulnerability',
          remediation: 'Validate and sanitize input, use safe APIs',
          cwe: 'CWE-78',
          owasp: 'A03:2021 - Injection',
        });
      }
    }

    return vulnerabilities;
  }

  _detectPathTraversal(code) {
    const vulnerabilities = [];
    const pattern = /readFile\s*\(\s*[^)]*\+[^)]+\)|readFileSync\s*\(\s*[^)]*\+[^)]+\)/g;

    const matches = code.matchAll(pattern);
    for (const match of matches) {
      vulnerabilities.push({
        type: 'Path Traversal',
        severity: 'high',
        line: this._findLineNumber(code, match.index),
        code: match[0],
        description: 'Potential path traversal vulnerability',
        remediation: 'Validate file paths and use path.resolve()',
        cwe: 'CWE-22',
        owasp: 'A01:2021 - Broken Access Control',
      });
    }

    return vulnerabilities;
  }

  _detectInsecureDeserialization(code) {
    const vulnerabilities = [];

    if (/eval\s*\(|Function\s*\(|new\s+Function\s*\(/g.test(code)) {
      vulnerabilities.push({
        type: 'Insecure Deserialization',
        severity: 'critical',
        line: this._findLineNumber(code, code.search(/eval\s*\(/)),
        code: 'eval() or Function() usage',
        description: 'Use of dangerous deserialization methods',
        remediation: 'Use JSON.parse() or safe alternatives',
        cwe: 'CWE-502',
        owasp: 'A08:2021 - Software and Data Integrity Failures',
      });
    }

    return vulnerabilities;
  }

  _checkDependencyVulnerabilities(dep, _ecosystem) {
    // Simulated vulnerability database
    const knownVulnerabilities = {
      lodash: {
        '<4.17.21': [
          {
            id: 'CVE-2021-23337',
            severity: 'high',
            description: 'Command injection vulnerability',
            fixedIn: '4.17.21',
          },
        ],
      },
      express: {
        '<4.17.3': [
          {
            id: 'CVE-2022-24999',
            severity: 'medium',
            description: 'Open redirect vulnerability',
            fixedIn: '4.17.3',
          },
        ],
      },
    };

    const vulns = [];
    if (knownVulnerabilities[dep.name]) {
      for (const [versionRange, vulnList] of Object.entries(knownVulnerabilities[dep.name])) {
        // Simplified version comparison
        if (this._versionAffected(dep.version, versionRange)) {
          vulns.push(...vulnList);
        }
      }
    }

    return vulns;
  }

  _versionAffected(version, range) {
    // Simplified version comparison (in production, use semver library)
    if (range.startsWith('<')) {
      const targetVersion = range.substring(1);
      return version < targetVersion;
    }
    return false;
  }

  _generateDependencyRecommendations(check) {
    const recommendations = [];

    if (check.summary.critical > 0) {
      recommendations.push({
        priority: 'critical',
        action: 'Update dependencies with critical vulnerabilities immediately',
        packages: check.vulnerableDependencies
          .filter((d) => d.vulnerabilities.some((v) => v.severity === 'critical'))
          .map((d) => d.name),
      });
    }

    if (check.summary.vulnerable > check.totalDependencies * 0.2) {
      recommendations.push({
        priority: 'high',
        action: 'Review and update dependency management strategy',
        impact: 'More than 20% of dependencies have known vulnerabilities',
      });
    }

    return recommendations;
  }

  _maskSecret(secret) {
    if (secret.length <= 8) {
      return '***';
    }
    return secret.substring(0, 4) + '***' + secret.substring(secret.length - 4);
  }

  _findLineNumber(content, index) {
    return content.substring(0, index).split('\n').length;
  }
}

/**
 * Get tool definitions for the security scanner
 */
function getToolDefinitions() {
  return [
    {
      name: 'scan-vulnerabilities',
      description: 'Scan code for security vulnerabilities',
      inputSchema: {
        type: 'object',
        properties: {
          code: { type: 'string', description: 'Code to scan' },
          language: { type: 'string', default: 'javascript' },
          severity: {
            type: 'string',
            enum: ['critical', 'high', 'medium', 'low', 'all'],
            default: 'all',
          },
        },
        required: ['code'],
      },
    },
    {
      name: 'check-dependencies',
      description: 'Check dependencies for known vulnerabilities',
      inputSchema: {
        type: 'object',
        properties: {
          dependencies: {
            type: ['object', 'array'],
            description: 'Dependencies to check',
          },
          ecosystem: { type: 'string', default: 'npm' },
        },
        required: ['dependencies'],
      },
    },
    {
      name: 'analyze-secrets',
      description: 'Analyze content for exposed secrets and credentials',
      inputSchema: {
        type: 'object',
        properties: {
          content: { type: 'string', description: 'Content to analyze' },
          strictMode: { type: 'boolean', default: true },
        },
        required: ['content'],
      },
    },
  ];
}

/**
 * Handle tool execution requests
 */
function handleToolCall(scanner, name, args) {
  switch (name) {
    case 'scan-vulnerabilities': {
      const validated = ScanVulnerabilitiesSchema.parse(args);
      const result = scanner.scanVulnerabilities(
        validated.code,
        validated.language,
        validated.severity
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    case 'check-dependencies': {
      const validated = CheckDependenciesSchema.parse(args);
      const result = scanner.checkDependencies(validated.dependencies, validated.ecosystem);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    case 'analyze-secrets': {
      const validated = AnalyzeSecretsSchema.parse(args);
      const result = scanner.analyzeSecrets(validated.content, validated.strictMode);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  }
}

/**
 * Initialize and start the MCP server
 */
async function main() {
  const scanner = new SecurityScanner();
  const server = new Server(
    {
      name: 'security-scanner',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  server.setRequestHandler(ListToolsRequestSchema, () => ({
    tools: getToolDefinitions(),
  }));

  server.setRequestHandler(CallToolRequestSchema, (request) => {
    const { name, arguments: args } = request.params;

    try {
      return handleToolCall(scanner, name, args);
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new McpError(
          ErrorCode.InvalidParams,
          `Invalid parameters: ${error.errors.map((e) => e.message).join(', ')}`
        );
      }
      if (error instanceof McpError) {
        throw error;
      }
      throw new McpError(
        ErrorCode.InternalError,
        error instanceof Error ? error.message : String(error)
      );
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Security Scanner MCP Server started successfully');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
