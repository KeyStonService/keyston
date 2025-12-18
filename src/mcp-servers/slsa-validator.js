#!/usr/bin/env node

/**
 * SLSA Validator MCP Server
 * Enterprise-grade SLSA provenance validation and compliance checking
 *
 * @module slsa-validator
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
const ValidateProvenanceSchema = z.object({
  provenance: z.object({
    _type: z.string(),
    predicateType: z.string(),
    subject: z.array(z.any()),
    predicate: z.any(),
  }),
  level: z.enum(['1', '2', '3', '4']).optional().default('3'),
});

const CheckSLSAComplianceSchema = z.object({
  provenance: z.object({
    _type: z.string(),
    predicateType: z.string(),
    subject: z.array(z.any()),
    predicate: z.any(),
  }),
  targetLevel: z.enum(['1', '2', '3', '4']).default('3'),
});

const GenerateComplianceReportSchema = z.object({
  provenance: z.object({
    _type: z.string(),
    predicateType: z.string(),
    subject: z.array(z.any()),
    predicate: z.any(),
  }),
  includeRemediation: z.boolean().optional().default(true),
});

/**
 * SLSA validation engine
 */
class SLSAValidator {
  constructor() {
    this.slsaLevels = process.env.SLSA_LEVELS?.split(',') || ['1', '2', '3', '4'];
  }

  /**
   * Validate SLSA provenance data
   */
  validateProvenance(provenance, level = '3') {
    const validation = {
      valid: true,
      level,
      checks: [],
      errors: [],
      warnings: [],
      score: 100,
    };

    // Basic structure validation
    validation.checks.push(this._checkStructure(provenance));

    // Subject validation
    validation.checks.push(this._checkSubjects(provenance.subject));

    // Predicate validation
    validation.checks.push(this._checkPredicate(provenance.predicate));

    // Level-specific validation
    validation.checks.push(...this._checkLevelRequirements(provenance, level));

    // Calculate overall validity
    const failedChecks = validation.checks.filter((c) => !c.passed);
    validation.valid = failedChecks.length === 0;
    validation.errors = failedChecks.filter((c) => c.severity === 'error');
    validation.warnings = failedChecks.filter((c) => c.severity === 'warning');

    // Calculate score
    validation.score = Math.max(
      0,
      100 - validation.errors.length * 20 - validation.warnings.length * 5
    );

    return validation;
  }

  /**
   * Check SLSA compliance
   */
  checkSLSACompliance(provenance, targetLevel = '3') {
    const compliance = {
      targetLevel,
      compliant: false,
      currentLevel: '0',
      requirements: [],
      gaps: [],
      recommendations: [],
    };

    // Check each level requirement
    for (let level = 1; level <= parseInt(targetLevel); level++) {
      const levelStr = level.toString();
      const requirements = this._getLevelRequirements(levelStr);

      for (const req of requirements) {
        const check = this._checkRequirement(provenance, req);
        compliance.requirements.push({
          level: levelStr,
          requirement: req.name,
          met: check.met,
          details: check.details,
        });

        if (!check.met) {
          compliance.gaps.push({
            level: levelStr,
            requirement: req.name,
            description: req.description,
            remediation: req.remediation,
          });
        }
      }
    }

    // Determine current level
    compliance.currentLevel = this._determineCurrentLevel(compliance.requirements);
    compliance.compliant = parseInt(compliance.currentLevel) >= parseInt(targetLevel);

    // Generate recommendations
    if (!compliance.compliant) {
      compliance.recommendations = this._generateRecommendations(compliance.gaps);
    }

    return compliance;
  }

  /**
   * Generate compliance report
   */
  generateComplianceReport(provenance, includeRemediation = true) {
    const report = {
      timestamp: new Date().toISOString(),
      summary: {},
      validation: {},
      compliance: {},
      recommendations: [],
    };

    // Run validation for all levels
    const validations = {};
    for (const level of ['1', '2', '3', '4']) {
      validations[level] = this.validateProvenance(provenance, level);
    }

    report.validation = validations;

    // Run compliance check for all levels
    const complianceChecks = {};
    for (const level of ['1', '2', '3', '4']) {
      complianceChecks[level] = this.checkSLSACompliance(provenance, level);
    }

    report.compliance = complianceChecks;

    // Generate summary
    report.summary = {
      highestLevel: this._getHighestCompliantLevel(complianceChecks),
      totalChecks: Object.values(validations).reduce((sum, v) => sum + v.checks.length, 0),
      totalErrors: Object.values(validations).reduce((sum, v) => sum + v.errors.length, 0),
      totalWarnings: Object.values(validations).reduce((sum, v) => sum + v.warnings.length, 0),
      overallScore: Math.round(Object.values(validations).reduce((sum, v) => sum + v.score, 0) / 4),
    };

    // Generate recommendations
    if (includeRemediation) {
      report.recommendations = this._generateDetailedRecommendations(report);
    }

    return report;
  }

  // Private helper methods

  _checkStructure(provenance) {
    const check = {
      name: 'Structure Validation',
      passed: true,
      severity: 'error',
      details: [],
    };

    if (!provenance._type) {
      check.passed = false;
      check.details.push('Missing _type field');
    }

    if (!provenance.predicateType?.includes('slsa')) {
      check.passed = false;
      check.details.push('Invalid or missing predicateType');
    }

    if (!Array.isArray(provenance.subject) || provenance.subject.length === 0) {
      check.passed = false;
      check.details.push('Missing or empty subject array');
    }

    if (!provenance.predicate) {
      check.passed = false;
      check.details.push('Missing predicate');
    }

    if (check.passed) {
      check.details.push('Valid SLSA provenance structure');
    }

    return check;
  }

  _checkSubjects(subjects) {
    const check = {
      name: 'Subject Validation',
      passed: true,
      severity: 'error',
      details: [],
    };

    for (let i = 0; i < subjects.length; i++) {
      const subject = subjects[i];

      if (!subject.name) {
        check.passed = false;
        check.details.push(`Subject ${i}: Missing name`);
      }

      if (!subject.digest?.sha256) {
        check.passed = false;
        check.details.push(`Subject ${i}: Missing or invalid digest`);
      }
    }

    if (check.passed) {
      check.details.push(`All ${subjects.length} subjects are valid`);
    }

    return check;
  }

  _checkPredicate(predicate) {
    const check = {
      name: 'Predicate Validation',
      passed: true,
      severity: 'error',
      details: [],
    };

    if (!predicate.buildDefinition) {
      check.passed = false;
      check.details.push('Missing buildDefinition');
    } else {
      if (!predicate.buildDefinition.buildType) {
        check.passed = false;
        check.details.push('Missing buildType in buildDefinition');
      }
    }

    if (!predicate.runDetails) {
      check.passed = false;
      check.details.push('Missing runDetails');
    } else {
      if (!predicate.runDetails.builder) {
        check.passed = false;
        check.details.push('Missing builder information');
      }
    }

    if (check.passed) {
      check.details.push('Valid predicate structure');
    }

    return check;
  }

  _checkLevelRequirements(provenance, level) {
    const checks = [];
    const requirements = this._getLevelRequirements(level);

    for (const req of requirements) {
      const check = this._checkRequirement(provenance, req);
      checks.push({
        name: `SLSA Level ${level}: ${req.name}`,
        passed: check.met,
        severity: req.severity || 'error',
        details: [check.details],
      });
    }

    return checks;
  }

  _getLevelRequirements(level) {
    const requirements = {
      1: [
        {
          name: 'Build Process Documentation',
          description: 'Provenance must document the build process',
          check: (p) => Boolean(p.predicate?.buildDefinition),
          remediation: 'Add buildDefinition to provenance',
        },
        {
          name: 'Version Control',
          description: 'Source must be identified from version control',
          check: (p) => Boolean(p.predicate?.buildDefinition?.externalParameters),
          remediation: 'Include version control information',
        },
      ],
      2: [
        {
          name: 'Build Service',
          description: 'Built by trusted build service',
          check: (p) => Boolean(p.predicate?.runDetails?.builder?.id),
          remediation: 'Specify builder ID in runDetails',
        },
        {
          name: 'Source Integrity',
          description: 'Source integrity verified',
          check: (p) => Boolean(p.predicate?.buildDefinition?.resolvedDependencies),
          remediation: 'Include resolved dependencies',
        },
      ],
      3: [
        {
          name: 'Hardened Build Platform',
          description: 'Build platform must be hardened',
          check: (p) => {
            const metadata = p.predicate?.runDetails?.metadata;
            return metadata && (metadata.invocationId || metadata.startedOn);
          },
          remediation: 'Add comprehensive build metadata',
        },
        {
          name: 'Non-falsifiable',
          description: 'Provenance cannot be falsified by build service',
          check: (p) => Boolean(p.predicate?.runDetails?.metadata?.invocationId),
          remediation: 'Include unique invocation ID',
        },
      ],
      4: [
        {
          name: 'Hermetic Build',
          description: 'Build must be hermetic',
          check: (p) => {
            const deps = p.predicate?.buildDefinition?.resolvedDependencies;
            return deps && deps.length > 0;
          },
          remediation: 'Ensure build is hermetic with resolved dependencies',
        },
        {
          name: 'Two-Party Review',
          description: 'Changes must be reviewed',
          check: (p) => Boolean(p.predicate?.buildDefinition?.externalParameters?.reviewers),
          remediation: 'Include reviewer information',
        },
      ],
    };

    return requirements[level] || [];
  }

  _checkRequirement(provenance, req) {
    return {
      met: req.check(provenance),
      details: req.description,
    };
  }

  _determineCurrentLevel(requirements) {
    let currentLevel = '0';

    for (let level = 1; level <= 4; level++) {
      const levelReqs = requirements.filter((r) => r.level === level.toString());
      const allMet = levelReqs.every((r) => r.met);

      if (allMet) {
        currentLevel = level.toString();
      } else {
        break;
      }
    }

    return currentLevel;
  }

  _generateRecommendations(gaps) {
    return gaps.map((gap) => ({
      priority: parseInt(gap.level) > 2 ? 'high' : 'medium',
      level: gap.level,
      requirement: gap.requirement,
      action: gap.remediation,
      impact: `Required for SLSA Level ${gap.level} compliance`,
    }));
  }

  _getHighestCompliantLevel(complianceChecks) {
    for (let level = 4; level >= 1; level--) {
      if (complianceChecks[level.toString()].compliant) {
        return level.toString();
      }
    }
    return '0';
  }

  _generateDetailedRecommendations(report) {
    const recommendations = [];
    const highestLevel = report.summary.highestLevel;

    if (highestLevel !== '4') {
      const nextLevel = (parseInt(highestLevel) + 1).toString();
      const gaps = report.compliance[nextLevel]?.gaps || [];

      recommendations.push({
        title: `Achieve SLSA Level ${nextLevel}`,
        priority: 'high',
        steps: gaps.map((g) => g.remediation),
        estimatedEffort: 'Medium',
        impact: `Improve supply chain security to Level ${nextLevel}`,
      });
    }

    if (report.summary.totalErrors > 0) {
      recommendations.push({
        title: 'Fix Critical Errors',
        priority: 'critical',
        steps: ['Review and fix all validation errors'],
        estimatedEffort: 'High',
        impact: 'Required for basic SLSA compliance',
      });
    }

    return recommendations;
  }
}

/**
 * Handle tool execution requests
 */
function handleToolCall(validator, name, args) {
  switch (name) {
    case 'validate-provenance': {
      const validated = ValidateProvenanceSchema.parse(args);
      const result = validator.validateProvenance(validated.provenance, validated.level);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    case 'check-slsa-compliance': {
      const validated = CheckSLSAComplianceSchema.parse(args);
      const result = validator.checkSLSACompliance(validated.provenance, validated.targetLevel);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    case 'generate-compliance-report': {
      const validated = GenerateComplianceReportSchema.parse(args);
      const result = validator.generateComplianceReport(
        validated.provenance,
        validated.includeRemediation
      );
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
      };
    }

    default:
      throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${name}`);
  }
}

/**
 * Get tool definitions for the slsa validator
 */
function getToolDefinitions() {
  return [
    {
      name: 'validate-provenance',
      description: 'Validate SLSA provenance data for specified level',
      inputSchema: {
        type: 'object',
        properties: {
          provenance: {
            type: 'object',
            description: 'SLSA provenance object',
          },
          level: {
            type: 'string',
            enum: ['1', '2', '3', '4'],
            default: '3',
            description: 'SLSA level to validate against',
          },
        },
        required: ['provenance'],
      },
    },
    {
      name: 'check-slsa-compliance',
      description: 'Check SLSA compliance for target level',
      inputSchema: {
        type: 'object',
        properties: {
          provenance: {
            type: 'object',
            description: 'SLSA provenance object',
          },
          targetLevel: {
            type: 'string',
            enum: ['1', '2', '3', '4'],
            default: '3',
            description: 'Target SLSA level',
          },
        },
        required: ['provenance'],
      },
    },
    {
      name: 'generate-compliance-report',
      description: 'Generate comprehensive SLSA compliance report',
      inputSchema: {
        type: 'object',
        properties: {
          provenance: {
            type: 'object',
            description: 'SLSA provenance object',
          },
          includeRemediation: {
            type: 'boolean',
            default: true,
            description: 'Include remediation recommendations',
          },
        },
        required: ['provenance'],
      },
    },
  ];
}

/**
 * Initialize and start the MCP server
 */
async function main() {
  const validator = new SLSAValidator();
  const server = new Server(
    {
      name: 'slsa-validator',
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
      return handleToolCall(validator, name, args);
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new McpError(
          ErrorCode.InvalidParams,
          `Invalid parameters: ${error.errors.map((e) => e.message).join(', ')}`
        );
      }
      // Wrap all other errors in McpError with InternalError code
      throw new McpError(
        ErrorCode.InternalError,
        error instanceof Error
          ? `Internal error: ${error.message}`
          : `Internal error: ${String(error)}`
      );
    }
  });

  const transport = new StdioServerTransport();
  await server.connect(transport);

  console.error('SLSA Validator MCP Server started successfully');
}

main().catch((error) => {
  console.error('Fatal error:', error);
  process.exit(1);
});
