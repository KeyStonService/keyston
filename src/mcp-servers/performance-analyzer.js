#!/usr/bin/env node

/**
 * Performance Analyzer MCP Server
 * Enterprise-grade performance analysis, bottleneck identification, and optimization
 *
 * @module performance-analyzer
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
const AnalyzePerformanceSchema = z.object({
  code: z.string().min(1, 'Code content is required'),
  language: z.string().optional().default('javascript'),
  metrics: z
    .array(z.enum(['complexity', 'memory', 'loops', 'async', 'all']))
    .optional()
    .default(['all']),
});

const IdentifyBottlenecksSchema = z.object({
  code: z.string().min(1, 'Code content is required'),
  threshold: z
    .object({
      complexity: z.number().optional().default(10),
      loopDepth: z.number().optional().default(3),
      functionLength: z.number().optional().default(50),
    })
    .optional()
    .default({}),
});

const SuggestOptimizationsSchema = z.object({
  code: z.string().min(1, 'Code content is required'),
  focus: z
    .array(z.enum(['speed', 'memory', 'readability', 'all']))
    .optional()
    .default(['all']),
});

/**
 * Performance analysis engine
 */
class PerformanceAnalyzer {
  /**
   * Analyze code performance
   */
  analyzePerformance(code, language = 'javascript', metrics = ['all']) {
    const analysis = {
      timestamp: new Date().toISOString(),
      language,
      metrics: {},
      score: 0,
      grade: 'A',
    };

    const includeAll = metrics.includes('all');

    if (includeAll || metrics.includes('complexity')) {
      analysis.metrics.complexity = this._analyzeComplexity(code);
    }

    if (includeAll || metrics.includes('memory')) {
      analysis.metrics.memory = this._analyzeMemoryUsage(code);
    }

    if (includeAll || metrics.includes('loops')) {
      analysis.metrics.loops = this._analyzeLoops(code);
    }

    if (includeAll || metrics.includes('async')) {
      analysis.metrics.async = this._analyzeAsyncPerformance(code);
    }

    // Calculate overall performance score
    analysis.score = this._calculatePerformanceScore(analysis.metrics);
    analysis.grade = this._calculateGrade(analysis.score);

    return analysis;
  }

  /**
   * Identify performance bottlenecks
   */
  identifyBottlenecks(code, threshold = {}) {
    const bottlenecks = {
      timestamp: new Date().toISOString(),
      threshold: {
        complexity: threshold.complexity || 10,
        loopDepth: threshold.loopDepth || 3,
        functionLength: threshold.functionLength || 50,
      },
      critical: [],
      warnings: [],
      summary: {
        totalBottlenecks: 0,
        critical: 0,
        warnings: 0,
      },
    };

    // Check for high complexity functions
    const complexityIssues = this._findHighComplexityFunctions(
      code,
      bottlenecks.threshold.complexity
    );
    bottlenecks.critical.push(...complexityIssues.filter((i) => i.severity === 'critical'));
    bottlenecks.warnings.push(...complexityIssues.filter((i) => i.severity === 'warning'));

    // Check for nested loops
    const loopIssues = this._findDeepNestedLoops(code, bottlenecks.threshold.loopDepth);
    bottlenecks.critical.push(...loopIssues);

    // Check for large functions
    const lengthIssues = this._findLongFunctions(code, bottlenecks.threshold.functionLength);
    bottlenecks.warnings.push(...lengthIssues);

    // Check for synchronous blocking operations
    const blockingOps = this._findBlockingOperations(code);
    bottlenecks.critical.push(...blockingOps);

    // Check for memory leaks
    const memoryIssues = this._findPotentialMemoryLeaks(code);
    bottlenecks.warnings.push(...memoryIssues);

    // Update summary
    bottlenecks.summary.critical = bottlenecks.critical.length;
    bottlenecks.summary.warnings = bottlenecks.warnings.length;
    bottlenecks.summary.totalBottlenecks =
      bottlenecks.critical.length + bottlenecks.warnings.length;

    return bottlenecks;
  }

  /**
   * Provide optimization suggestions
   */
  suggestOptimizations(code, focus = ['all']) {
    const suggestions = {
      timestamp: new Date().toISOString(),
      focus,
      optimizations: [],
      estimatedImpact: {
        speed: 0,
        memory: 0,
        readability: 0,
      },
    };

    const includeAll = focus.includes('all');

    if (includeAll || focus.includes('speed')) {
      suggestions.optimizations.push(...this._suggestSpeedOptimizations(code));
    }

    if (includeAll || focus.includes('memory')) {
      suggestions.optimizations.push(...this._suggestMemoryOptimizations(code));
    }

    if (includeAll || focus.includes('readability')) {
      suggestions.optimizations.push(...this._suggestReadabilityOptimizations(code));
    }

    // Sort by priority
    suggestions.optimizations.sort((a, b) => b.priority - a.priority);

    // Calculate estimated impact
    for (const opt of suggestions.optimizations) {
      suggestions.estimatedImpact.speed += opt.impact.speed || 0;
      suggestions.estimatedImpact.memory += opt.impact.memory || 0;
      suggestions.estimatedImpact.readability += opt.impact.readability || 0;
    }

    return suggestions;
  }

  // Private helper methods

  _analyzeComplexity(code) {
    const lines = code.split('\n');
    const complexity = {
      cyclomatic: this._calculateCyclomaticComplexity(code),
      cognitive: this._calculateCognitiveComplexity(code),
      halstead: this._calculateHalsteadMetrics(code),
      maintainabilityIndex: 0,
    };

    // Calculate maintainability index
    complexity.maintainabilityIndex = Math.max(
      0,
      171 -
        5.2 * Math.log(complexity.halstead.volume) -
        0.23 * complexity.cyclomatic -
        16.2 * Math.log(lines.length)
    );

    return complexity;
  }

  _analyzeMemoryUsage(code) {
    const analysis = {
      potentialLeaks: 0,
      largArrays: 0,
      closureIssues: 0,
      globalVariables: 0,
      score: 100,
    };

    // Check for potential memory leaks
    if (/setInterval\s*\(/.test(code) && !/clearInterval/.test(code)) {
      analysis.potentialLeaks++;
    }

    // Check for large array operations
    const largeArrayOps = code.match(/new\s+Array\s*\(\s*\d{5,}\s*\)/g);
    analysis.largArrays = largeArrayOps ? largeArrayOps.length : 0;

    // Check for closure issues
    const closures = code.match(/function\s+\w+\s*\([^)]*\)\s*{[^}]*function/g);
    analysis.closureIssues = closures ? closures.length : 0;

    // Check for global variables
    const globals = code.match(/^var\s+\w+|^let\s+\w+|^const\s+\w+/gm);
    analysis.globalVariables = globals ? globals.length : 0;

    // Calculate score
    analysis.score = Math.max(
      0,
      100 -
        analysis.potentialLeaks * 20 -
        analysis.largArrays * 10 -
        analysis.closureIssues * 5 -
        analysis.globalVariables * 2
    );

    return analysis;
  }

  _analyzeLoops(code) {
    const analysis = {
      totalLoops: 0,
      nestedLoops: 0,
      maxDepth: 0,
      inefficientLoops: [],
    };

    // Count loops
    const loopPatterns = [/\bfor\s*\(/g, /\bwhile\s*\(/g, /\.forEach\(/g, /\.map\(/g];
    for (const pattern of loopPatterns) {
      const matches = code.match(pattern);
      analysis.totalLoops += matches ? matches.length : 0;
    }

    // Detect nested loops
    const lines = code.split('\n');
    let depth = 0;
    let maxDepth = 0;

    for (const line of lines) {
      if (/\bfor\s*\(|\bwhile\s*\(/.test(line)) {
        depth++;
        maxDepth = Math.max(maxDepth, depth);
        if (depth > 1) {
          analysis.nestedLoops++;
        }
      }
      if (line.includes('}') && depth > 0) {
        depth--;
      }
    }

    analysis.maxDepth = maxDepth;

    // Find inefficient loop patterns
    if (/for\s*\([^)]*\)[^{]*{[^}]*\.push\(/.test(code)) {
      analysis.inefficientLoops.push({
        type: 'array-push-in-loop',
        suggestion: 'Consider pre-allocating array or using array methods',
      });
    }

    return analysis;
  }

  _analyzeAsyncPerformance(code) {
    const analysis = {
      asyncFunctions: 0,
      promises: 0,
      callbacks: 0,
      potentialBlocking: 0,
      missingAwait: 0,
      score: 100,
    };

    // Count async patterns
    analysis.asyncFunctions = (code.match(/async\s+function|async\s*\(/g) || []).length;
    analysis.promises = (code.match(/new\s+Promise\(/g) || []).length;
    analysis.callbacks = (code.match(/function\s*\([^)]*\)\s*{[^}]*callback\(/g) || []).length;

    // Check for synchronous blocking operations
    if (/\.readFileSync|\.execSync|\.statSync/.test(code)) {
      analysis.potentialBlocking++;
    }

    // Check for missing await
    const asyncWithoutAwait = code.match(/async[^{]*{[^}]*(?!await)[^}]*}/g);
    analysis.missingAwait = asyncWithoutAwait ? asyncWithoutAwait.length : 0;

    // Calculate score
    analysis.score = Math.max(
      0,
      100 - analysis.potentialBlocking * 25 - analysis.missingAwait * 10
    );

    return analysis;
  }

  _calculateCyclomaticComplexity(code) {
    const patterns = [
      /\bif\b/g,
      /\belse\b/g,
      /\bfor\b/g,
      /\bwhile\b/g,
      /\bcase\b/g,
      /\bcatch\b/g,
      /&&/g,
      /\|\|/g,
      /\?/g,
    ];

    let complexity = 1;
    for (const pattern of patterns) {
      const matches = code.match(pattern);
      complexity += matches ? matches.length : 0;
    }

    return complexity;
  }

  _calculateCognitiveComplexity(code) {
    const lines = code.split('\n');
    let complexity = 0;
    let nesting = 0;

    for (const line of lines) {
      if (line.includes('{')) {
        nesting++;
      }
      if (line.includes('}')) {
        nesting = Math.max(0, nesting - 1);
      }

      if (/\b(if|for|while|switch|catch)\b/.test(line)) {
        complexity += 1 + nesting;
      }
    }

    return complexity;
  }

  _calculateHalsteadMetrics(code) {
    // Simplified Halstead metrics
    const operators = code.match(/[+\-*/%=<>!&|^~?:]/g) || [];
    const operands = code.match(/\b[a-zA-Z_][a-zA-Z0-9_]*\b|\b\d+\b/g) || [];

    const n1 = new Set(operators).size; // Unique operators
    const n2 = new Set(operands).size; // Unique operands
    const N1 = operators.length; // Total operators
    const N2 = operands.length; // Total operands

    const vocabulary = n1 + n2;
    const length = N1 + N2;
    const volume = length * Math.log2(vocabulary || 1);
    const difficulty = (n1 / 2) * (N2 / (n2 || 1));
    const effort = volume * difficulty;

    return { vocabulary, length, volume, difficulty, effort };
  }

  _calculatePerformanceScore(metrics) {
    let score = 100;

    if (metrics.complexity) {
      if (metrics.complexity.cyclomatic > 20) {
        score -= 20;
      } else if (metrics.complexity.cyclomatic > 10) {
        score -= 10;
      }
    }

    if (metrics.memory) {
      score -= (100 - metrics.memory.score) * 0.2;
    }

    if (metrics.loops) {
      score -= metrics.loops.nestedLoops * 5;
      score -= metrics.loops.inefficientLoops.length * 10;
    }

    if (metrics.async) {
      score -= (100 - metrics.async.score) * 0.3;
    }

    return Math.max(0, Math.round(score));
  }

  _calculateGrade(score) {
    if (score >= 90) {
      return 'A';
    }
    if (score >= 80) {
      return 'B';
    }
    if (score >= 70) {
      return 'C';
    }
    if (score >= 60) {
      return 'D';
    }
    return 'F';
  }

  _findHighComplexityFunctions(code, threshold) {
    const issues = [];
    const functions = code.matchAll(
      /function\s+(\w+)\s*\([^)]*\)\s*{|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>/g
    );

    for (const match of functions) {
      const name = match[1] || match[2];
      const functionCode = this._extractFunctionCode(code, match.index);
      const complexity = this._calculateCyclomaticComplexity(functionCode);

      if (complexity > threshold * 2) {
        issues.push({
          type: 'high-complexity',
          severity: 'critical',
          function: name,
          complexity,
          line: this._findLineNumber(code, match.index),
          message: `Function ${name} has very high complexity (${complexity})`,
        });
      } else if (complexity > threshold) {
        issues.push({
          type: 'high-complexity',
          severity: 'warning',
          function: name,
          complexity,
          line: this._findLineNumber(code, match.index),
          message: `Function ${name} has high complexity (${complexity})`,
        });
      }
    }

    return issues;
  }

  _findDeepNestedLoops(code, threshold) {
    const issues = [];
    const lines = code.split('\n');
    let depth = 0;
    let maxDepth = 0;
    let startLine = 0;

    for (let i = 0; i < lines.length; i++) {
      if (/\bfor\s*\(|\bwhile\s*\(/.test(lines[i])) {
        if (depth === 0) {
          startLine = i + 1;
        }
        depth++;
        maxDepth = Math.max(maxDepth, depth);
      }
      if (lines[i].includes('}') && depth > 0) {
        depth--;
        if (depth === 0 && maxDepth > threshold) {
          issues.push({
            type: 'deep-nested-loops',
            severity: 'critical',
            depth: maxDepth,
            line: startLine,
            message: `Loop nesting depth of ${maxDepth} exceeds threshold of ${threshold}`,
          });
          maxDepth = 0;
        }
      }
    }

    return issues;
  }

  _findLongFunctions(code, threshold) {
    const issues = [];
    const functions = code.matchAll(
      /function\s+(\w+)\s*\([^)]*\)\s*{|const\s+(\w+)\s*=\s*\([^)]*\)\s*=>/g
    );

    for (const match of functions) {
      const name = match[1] || match[2];
      const functionCode = this._extractFunctionCode(code, match.index);
      const lines = functionCode.split('\n').length;

      if (lines > threshold) {
        issues.push({
          type: 'long-function',
          severity: 'warning',
          function: name,
          lines,
          line: this._findLineNumber(code, match.index),
          message: `Function ${name} is ${lines} lines long (threshold: ${threshold})`,
        });
      }
    }

    return issues;
  }

  _findBlockingOperations(code) {
    const issues = [];
    const blockingOps = [
      { pattern: /\.readFileSync\(/g, name: 'readFileSync' },
      { pattern: /\.writeFileSync\(/g, name: 'writeFileSync' },
      { pattern: /\.execSync\(/g, name: 'execSync' },
      { pattern: /\.statSync\(/g, name: 'statSync' },
    ];

    for (const op of blockingOps) {
      const matches = code.matchAll(op.pattern);
      for (const match of matches) {
        issues.push({
          type: 'blocking-operation',
          severity: 'critical',
          operation: op.name,
          line: this._findLineNumber(code, match.index),
          message: `Synchronous blocking operation: ${op.name}`,
        });
      }
    }

    return issues;
  }

  _findPotentialMemoryLeaks(code) {
    const issues = [];

    // Check for timers without cleanup
    if (/setInterval\s*\(/.test(code) && !/clearInterval/.test(code)) {
      issues.push({
        type: 'memory-leak',
        severity: 'warning',
        cause: 'setInterval without clearInterval',
        message: 'Interval timer may cause memory leak',
      });
    }

    // Check for event listeners without removal
    if (/addEventListener\s*\(/.test(code) && !/removeEventListener/.test(code)) {
      issues.push({
        type: 'memory-leak',
        severity: 'warning',
        cause: 'addEventListener without removeEventListener',
        message: 'Event listener may cause memory leak',
      });
    }

    return issues;
  }

  _suggestSpeedOptimizations(code) {
    const suggestions = [];

    // Suggest replacing nested loops
    if (/for\s*\([^)]*\)[^{]*{[^}]*for\s*\(/.test(code)) {
      suggestions.push({
        type: 'speed',
        title: 'Optimize nested loops',
        description: 'Replace nested loops with hash maps or more efficient algorithms',
        priority: 90,
        impact: { speed: 30, memory: 0, readability: 5 },
        example: 'Use Map or Set for O(1) lookups instead of O(n) nested loops',
      });
    }

    // Suggest async/await optimization
    if (/\.then\([^)]*\)\.then\([^)]*\)\.then\(/.test(code)) {
      suggestions.push({
        type: 'speed',
        title: 'Use async/await for better performance',
        description: 'Convert promise chains to async/await for better readability and performance',
        priority: 60,
        impact: { speed: 10, memory: 0, readability: 15 },
        example: 'Replace .then() chains with async/await',
      });
    }

    return suggestions;
  }

  _suggestMemoryOptimizations(code) {
    const suggestions = [];

    // Suggest array pre-allocation
    if (/\.push\(/.test(code)) {
      suggestions.push({
        type: 'memory',
        title: 'Pre-allocate arrays when size is known',
        description: 'Pre-allocating arrays reduces memory reallocation overhead',
        priority: 50,
        impact: { speed: 10, memory: 20, readability: 0 },
        example: 'new Array(size) instead of repeated push()',
      });
    }

    return suggestions;
  }

  _suggestReadabilityOptimizations(code) {
    const suggestions = [];

    // Suggest extracting complex conditions
    if (/if\s*\([^)]{50,}\)/.test(code)) {
      suggestions.push({
        type: 'readability',
        title: 'Extract complex conditions',
        description: 'Move complex conditions to named variables for better readability',
        priority: 40,
        impact: { speed: 0, memory: 0, readability: 25 },
        example: 'const isValid = condition1 && condition2; if (isValid) {...}',
      });
    }

    return suggestions;
  }

  _extractFunctionCode(code, startIndex) {
    let depth = 0;
    let started = false;
    let result = '';

    for (let i = startIndex; i < code.length; i++) {
      const char = code[i];
      result += char;

      if (char === '{') {
        started = true;
        depth++;
      } else if (char === '}') {
        depth--;
        if (started && depth === 0) {
          break;
        }
      }
    }

    return result;
  }

  _findLineNumber(code, index) {
    return code.substring(0, index).split('\n').length;
  }
}

/**
 * Handle tool execution requests
 */
function handleToolCall(analyzer, name, args) {
  switch (name) {
    case 'analyze-performance': {
      const validated = AnalyzePerformanceSchema.parse(args);
      const result = analyzer.analyzePerformance(
        validated.code,
        validated.language,
        validated.metrics
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    case 'identify-bottlenecks': {
      const validated = IdentifyBottlenecksSchema.parse(args);
      const result = analyzer.identifyBottlenecks(validated.code, validated.threshold);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    case 'suggest-optimizations': {
      const validated = SuggestOptimizationsSchema.parse(args);
      const result = analyzer.suggestOptimizations(validated.code, validated.focus);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  }
}

/**
 * Get tool definitions for the performance analyzer
 */
function getToolDefinitions() {
  return [
    {
      name: 'analyze-performance',
      description: 'Analyze code performance metrics',
      inputSchema: {
        type: 'object',
        properties: {
          code: { type: 'string', description: 'Code to analyze' },
          language: { type: 'string', default: 'javascript' },
          metrics: {
            type: 'array',
            items: {
              type: 'string',
              enum: ['complexity', 'memory', 'loops', 'async', 'all'],
            },
            default: ['all'],
          },
        },
        required: ['code'],
      },
    },
    {
      name: 'identify-bottlenecks',
      description: 'Identify performance bottlenecks in code',
      inputSchema: {
        type: 'object',
        properties: {
          code: { type: 'string', description: 'Code to analyze' },
          threshold: {
            type: 'object',
            properties: {
              complexity: { type: 'number', default: 10 },
              loopDepth: { type: 'number', default: 3 },
              functionLength: { type: 'number', default: 50 },
            },
          },
        },
        required: ['code'],
      },
    },
    {
      name: 'suggest-optimizations',
      description: 'Suggest performance optimizations',
      inputSchema: {
        type: 'object',
        properties: {
          code: { type: 'string', description: 'Code to optimize' },
          focus: {
            type: 'array',
            items: {
              type: 'string',
              enum: ['speed', 'memory', 'readability', 'all'],
            },
            default: ['all'],
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
  const analyzer = new PerformanceAnalyzer();
  const server = new Server(
    {
      name: 'performance-analyzer',
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
        `Internal error: ${error instanceof Error ? error.message : String(error)}`
      );
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('Performance Analyzer MCP Server started successfully');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
