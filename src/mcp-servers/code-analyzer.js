#!/usr/bin/env node

/**
 * Code Analyzer MCP Server
 * Enterprise-grade code analysis with issue detection and improvement suggestions
 *
 * @module code-analyzer
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
const AnalyzeCodeSchema = z.object({
  code: z.string().min(1, 'Code content is required'),
  language: z.string().optional().default('javascript'),
  options: z
    .object({
      checkComplexity: z.boolean().optional().default(true),
      checkSecurity: z.boolean().optional().default(true),
      checkPerformance: z.boolean().optional().default(true),
      checkBestPractices: z.boolean().optional().default(true),
    })
    .optional()
    .default({}),
});

const DetectIssuesSchema = z.object({
  code: z.string().min(1, 'Code content is required'),
  severity: z.enum(['critical', 'high', 'medium', 'low', 'info']).optional().default('medium'),
});

const SuggestImprovementsSchema = z.object({
  code: z.string().min(1, 'Code content is required'),
  context: z.string().optional(),
});

/**
 * Code analysis engine
 */
class CodeAnalyzer {
  /**
   * Analyze code quality and complexity
   */
  analyzeCode(code, language = 'javascript', options = {}) {
    const lines = code.split('\n');
    const nonEmptyLines = lines.filter((line) => line.trim().length > 0);

    const analysis = {
      language,
      metrics: {
        totalLines: lines.length,
        codeLines: nonEmptyLines.length,
        commentLines: lines.filter((line) => line.trim().startsWith('//')).length,
        blankLines: lines.length - nonEmptyLines.length,
      },
      complexity: this._calculateComplexity(code),
      issues: [],
      score: 0,
    };

    if (options.checkComplexity) {
      analysis.complexity = this._calculateComplexity(code);
    }

    if (options.checkSecurity) {
      analysis.issues.push(...this._detectSecurityIssues(code));
    }

    if (options.checkPerformance) {
      analysis.issues.push(...this._detectPerformanceIssues(code));
    }

    if (options.checkBestPractices) {
      analysis.issues.push(...this._detectBestPracticeIssues(code));
    }

    // Calculate overall quality score (0-100)
    analysis.score = this._calculateQualityScore(analysis);

    return analysis;
  }

  /**
   * Detect code issues
   */
  detectIssues(code, severityFilter = 'medium') {
    const issues = [];

    // Security issues
    issues.push(...this._detectSecurityIssues(code));

    // Performance issues
    issues.push(...this._detectPerformanceIssues(code));

    // Best practice issues
    issues.push(...this._detectBestPracticeIssues(code));

    // Code smell issues
    issues.push(...this._detectCodeSmells(code));

    // Filter by severity
    const severityLevels = ['critical', 'high', 'medium', 'low', 'info'];
    const minSeverityIndex = severityLevels.indexOf(severityFilter);

    return issues.filter((issue) => {
      const issueSeverityIndex = severityLevels.indexOf(issue.severity);
      return issueSeverityIndex <= minSeverityIndex;
    });
  }

  /**
   * Provide code improvement suggestions
   */
  suggestImprovements(code, context = '') {
    const issues = this.detectIssues(code, 'info');
    const suggestions = [];

    // Generate improvement suggestions based on issues
    for (const issue of issues) {
      suggestions.push({
        type: issue.type,
        severity: issue.severity,
        description: issue.message,
        suggestion: this._generateSuggestion(issue, code),
        line: issue.line,
        priority: this._calculatePriority(issue.severity),
      });
    }

    // Add context-specific suggestions
    if (context) {
      suggestions.push(...this._generateContextSuggestions(code, context));
    }

    // Sort by priority
    suggestions.sort((a, b) => b.priority - a.priority);

    return {
      totalSuggestions: suggestions.length,
      suggestions: suggestions.slice(0, 20), // Top 20 suggestions
      summary: this._generateSummary(suggestions),
    };
  }

  // Private helper methods

  _calculateComplexity(code) {
    const cyclomaticComplexity = this._calculateCyclomaticComplexity(code);
    const cognitiveComplexity = this._calculateCognitiveComplexity(code);

    return {
      cyclomatic: cyclomaticComplexity,
      cognitive: cognitiveComplexity,
      rating: this._getComplexityRating(cyclomaticComplexity),
    };
  }

  _calculateCyclomaticComplexity(code) {
    // Count decision points (if, else, for, while, case, catch, &&, ||, ?)
    const patterns = [
      /\bif\b/g,
      /\belse\s+if\b/g,
      /\bfor\b/g,
      /\bwhile\b/g,
      /\bcase\b/g,
      /\bcatch\b/g,
      /&&/g,
      /\|\|/g,
      /\?/g,
    ];

    let complexity = 1; // Base complexity
    for (const pattern of patterns) {
      const matches = code.match(pattern);
      if (matches) {
        complexity += matches.length;
      }
    }

    return complexity;
  }

  _calculateCognitiveComplexity(code) {
    // Simplified cognitive complexity calculation
    const lines = code.split('\n');
    let complexity = 0;
    let nestingLevel = 0;

    for (const line of lines) {
      if (line.includes('{')) {
        nestingLevel++;
      }
      if (line.includes('}')) {
        nestingLevel = Math.max(0, nestingLevel - 1);
      }

      if (/\b(if|for|while|switch)\b/.test(line)) {
        complexity += 1 + nestingLevel;
      }
    }

    return complexity;
  }

  _getComplexityRating(complexity) {
    if (complexity <= 5) {
      return 'A - Simple';
    }
    if (complexity <= 10) {
      return 'B - Moderate';
    }
    if (complexity <= 20) {
      return 'C - Complex';
    }
    if (complexity <= 50) {
      return 'D - Very Complex';
    }
    return 'F - Extremely Complex';
  }

  _detectSecurityIssues(code) {
    const issues = [];

    // Check for eval usage
    if (/\beval\s*\(/.test(code)) {
      issues.push({
        type: 'security',
        severity: 'critical',
        message: 'Avoid using eval() - it can execute arbitrary code',
        line: this._findLineNumber(code, /\beval\s*\(/),
      });
    }

    // Check for SQL injection vulnerability patterns
    if (/\.query\s*\(\s*['"`][^'"`]*\+/.test(code)) {
      issues.push({
        type: 'security',
        severity: 'high',
        message: 'Potential SQL injection - use parameterized queries',
        line: this._findLineNumber(code, /\.query\s*\(/),
      });
    }

    // Check for hardcoded secrets
    if (/password\s*=\s*['"][^'"]+['"]|api[_-]?key\s*=\s*['"][^'"]+['"]/i.test(code)) {
      issues.push({
        type: 'security',
        severity: 'high',
        message: 'Hardcoded credentials detected - use environment variables',
        line: this._findLineNumber(code, /password\s*=|api[_-]?key\s*=/i),
      });
    }

    return issues;
  }

  _detectPerformanceIssues(code) {
    const issues = [];

    // Check for nested loops
    const nestedLoopPattern = /for\s*\([^)]*\)[^{]*{[^}]*for\s*\([^)]*\)/;
    if (nestedLoopPattern.test(code)) {
      issues.push({
        type: 'performance',
        severity: 'medium',
        message: 'Nested loops detected - consider optimization',
        line: this._findLineNumber(code, nestedLoopPattern),
      });
    }

    // Check for synchronous operations in loops
    if (/for\s*\([^)]*\)[^{]*{[^}]*\.(readFileSync|execSync)/.test(code)) {
      issues.push({
        type: 'performance',
        severity: 'high',
        message: 'Synchronous operation in loop - use async alternatives',
        line: this._findLineNumber(code, /\.(readFileSync|execSync)/),
      });
    }

    return issues;
  }

  _detectBestPracticeIssues(code) {
    const issues = [];

    // Check for var usage
    if (/\bvar\s+/.test(code)) {
      issues.push({
        type: 'best-practice',
        severity: 'low',
        message: 'Use const or let instead of var',
        line: this._findLineNumber(code, /\bvar\s+/),
      });
    }

    // Check for console.log in production
    if (/console\.log\(/.test(code)) {
      issues.push({
        type: 'best-practice',
        severity: 'info',
        message: 'Consider using proper logging instead of console.log',
        line: this._findLineNumber(code, /console\.log\(/),
      });
    }

    // Check for missing error handling
    if (/\.then\([^)]*\)(?!\s*\.catch)/.test(code)) {
      issues.push({
        type: 'best-practice',
        severity: 'medium',
        message: 'Promise without .catch() - add error handling',
        line: this._findLineNumber(code, /\.then\(/),
      });
    }

    return issues;
  }

  _detectCodeSmells(code) {
    const issues = [];
    const lines = code.split('\n');

    // Check for long functions
    let functionLines = 0;
    let inFunction = false;
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      if (/function\s+\w+\s*\(|=>\s*{/.test(line)) {
        inFunction = true;
        functionLines = 0;
      }
      if (inFunction) {
        functionLines++;
      }
      if (line.includes('}') && inFunction) {
        if (functionLines > 50) {
          issues.push({
            type: 'code-smell',
            severity: 'medium',
            message: `Function is too long (${functionLines} lines) - consider breaking it down`,
            line: i - functionLines + 1,
          });
        }
        inFunction = false;
      }
    }

    // Check for magic numbers
    const magicNumberPattern = /\b\d{2,}\b/g;
    const matches = code.match(magicNumberPattern);
    if (matches && matches.length > 5) {
      issues.push({
        type: 'code-smell',
        severity: 'low',
        message: 'Multiple magic numbers found - consider using named constants',
        line: 1,
      });
    }

    return issues;
  }

  _findLineNumber(code, pattern) {
    const lines = code.split('\n');
    for (let i = 0; i < lines.length; i++) {
      if (pattern.test(lines[i])) {
        return i + 1;
      }
    }
    return 1;
  }

  _calculateQualityScore(analysis) {
    let score = 100;

    // Deduct points based on complexity
    if (analysis.complexity.cyclomatic > 20) {
      score -= 20;
    } else if (analysis.complexity.cyclomatic > 10) {
      score -= 10;
    } else if (analysis.complexity.cyclomatic > 5) {
      score -= 5;
    }

    // Deduct points based on issues
    for (const issue of analysis.issues) {
      switch (issue.severity) {
        case 'critical':
          score -= 15;
          break;
        case 'high':
          score -= 10;
          break;
        case 'medium':
          score -= 5;
          break;
        case 'low':
          score -= 2;
          break;
        case 'info':
          score -= 1;
          break;
      }
    }

    return Math.max(0, score);
  }

  _calculatePriority(severity) {
    const priorities = {
      critical: 100,
      high: 75,
      medium: 50,
      low: 25,
      info: 10,
    };
    return priorities[severity] || 0;
  }

  _generateSuggestion(issue, _code) {
    const suggestions = {
      security: {
        eval: 'Replace eval() with safer alternatives like Function constructor or JSON.parse()',
        'sql-injection': 'Use parameterized queries or ORM to prevent SQL injection',
        'hardcoded-credentials': 'Store credentials in environment variables and use process.env',
      },
      performance: {
        'nested-loops': 'Consider using hash maps or optimizing algorithm complexity',
        'sync-in-loop': 'Use Promise.all() or async/await with proper batching',
      },
      'best-practice': {
        var: 'Replace var with const for immutable values or let for mutable ones',
        'console-log': 'Use a proper logging library like winston or pino',
        'no-catch': 'Add .catch() to handle promise rejections',
      },
    };

    return (
      suggestions[issue.type]?.[issue.message.split(' -')[0]] ||
      'Review and refactor this code section'
    );
  }

  _generateContextSuggestions(code, context) {
    const suggestions = [];

    if (context.includes('test')) {
      suggestions.push({
        type: 'context',
        severity: 'info',
        description: 'Add test coverage',
        suggestion: 'Consider adding unit tests for this code',
        priority: 40,
      });
    }

    if (context.includes('production')) {
      suggestions.push({
        type: 'context',
        severity: 'medium',
        description: 'Production readiness',
        suggestion: 'Add error handling, logging, and monitoring',
        priority: 70,
      });
    }

    return suggestions;
  }

  _generateSummary(suggestions) {
    const bySeverity = suggestions.reduce((acc, s) => {
      acc[s.severity] = (acc[s.severity] || 0) + 1;
      return acc;
    }, {});

    return {
      total: suggestions.length,
      bySeverity,
      topPriority: suggestions[0]?.description || 'No suggestions',
    };
  }
}

/**
 * Handle tool execution requests
 */
function handleToolCall(analyzer, name, args) {
  switch (name) {
    case 'analyze-code': {
      const validated = AnalyzeCodeSchema.parse(args);
      const result = analyzer.analyzeCode(validated.code, validated.language, validated.options);
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    }

    case 'detect-issues': {
      const validated = DetectIssuesSchema.parse(args);
      const result = analyzer.detectIssues(validated.code, validated.severity);
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(
              {
                totalIssues: result.length,
                issues: result,
              },
              null,
              2
            ),
          },
        ],
      };
    }

    case 'suggest-improvements': {
      const validated = SuggestImprovementsSchema.parse(args);
      const result = analyzer.suggestImprovements(validated.code, validated.context);
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    }

    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  }
}

/**
 * Get tool definitions for the code analyzer
 */
function getToolDefinitions() {
  return [
    {
      name: 'analyze-code',
      description: 'Analyze code quality, complexity, and metrics',
      inputSchema: {
        type: 'object',
        properties: {
          code: {
            type: 'string',
            description: 'The code to analyze',
          },
          language: {
            type: 'string',
            description: 'Programming language (default: javascript)',
            default: 'javascript',
          },
          options: {
            type: 'object',
            properties: {
              checkComplexity: { type: 'boolean', default: true },
              checkSecurity: { type: 'boolean', default: true },
              checkPerformance: { type: 'boolean', default: true },
              checkBestPractices: { type: 'boolean', default: true },
            },
          },
        },
        required: ['code'],
      },
    },
    {
      name: 'detect-issues',
      description: 'Detect code issues with configurable severity filtering',
      inputSchema: {
        type: 'object',
        properties: {
          code: {
            type: 'string',
            description: 'The code to analyze for issues',
          },
          severity: {
            type: 'string',
            enum: ['critical', 'high', 'medium', 'low', 'info'],
            description: 'Minimum severity level to report',
            default: 'medium',
          },
        },
        required: ['code'],
      },
    },
    {
      name: 'suggest-improvements',
      description: 'Suggest code improvements and refactoring opportunities',
      inputSchema: {
        type: 'object',
        properties: {
          code: {
            type: 'string',
            description: 'The code to analyze for improvements',
          },
          context: {
            type: 'string',
            description: 'Additional context for targeted suggestions',
          },
        },
        required: ['code'],
      },
    },
  ];
}

/**
 * Initialize and start the MCP server
 */
async function main() {
  const analyzer = new CodeAnalyzer();
  const server = new Server(
    {
      name: 'code-analyzer',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
      },
    }
  );

  // List available tools
  server.setRequestHandler(ListToolsRequestSchema, () => ({
    tools: getToolDefinitions(),
  }));

  // Handle tool calls
  server.setRequestHandler(CallToolRequestSchema, (request) => {
    const { name, arguments: args } = request.params;

    try {
      return handleToolCall(analyzer, name, args);
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

  // Start the server
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // Log startup
  console.error('Code Analyzer MCP Server started successfully');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
