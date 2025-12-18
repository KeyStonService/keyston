/**
 * Advisory Validator Service
 *
 * Comprehensive validation for OSV-format security advisories
 * Following GitHub Advisory Database standards
 *
 * @module validators/advisory-validator
 * @author SynergyMesh Team
 * @license MIT
 */

import {
  Advisory,
  AdvisorySchema,
  AdvisoryValidationResult,
  Ecosystem,
  GHSA_ID_PATTERN,
  CVE_ID_PATTERN,
  CWE_ID_PATTERN,
} from '../types/advisory.js';

/**
 * Validation rule definition
 */
interface ValidationRule {
  id: string;
  name: string;
  severity: 'error' | 'warning';
  validate: (advisory: Advisory) => string | null;
}

/**
 * Built-in validation rules
 */
const VALIDATION_RULES: ValidationRule[] = [
  // Structure Rules
  {
    id: 'STRUCTURE_001',
    name: 'Valid GHSA ID format',
    severity: 'error',
    validate: (advisory) => {
      if (!GHSA_ID_PATTERN.test(advisory.id)) {
        return `Invalid GHSA ID format: ${advisory.id}. Expected format: GHSA-xxxx-xxxx-xxxx`;
      }
      return null;
    },
  },
  {
    id: 'STRUCTURE_002',
    name: 'Modified timestamp required',
    severity: 'error',
    validate: (advisory) => {
      if (!advisory.modified) {
        return 'Modified timestamp is required';
      }
      const date = new Date(advisory.modified);
      if (isNaN(date.getTime())) {
        return `Invalid modified timestamp: ${advisory.modified}`;
      }
      return null;
    },
  },
  {
    id: 'STRUCTURE_003',
    name: 'Summary required',
    severity: 'error',
    validate: (advisory) => {
      if (!advisory.summary || advisory.summary.trim().length === 0) {
        return 'Summary is required and cannot be empty';
      }
      return null;
    },
  },
  {
    id: 'STRUCTURE_004',
    name: 'At least one affected package',
    severity: 'error',
    validate: (advisory) => {
      if (!advisory.affected || advisory.affected.length === 0) {
        return 'At least one affected package is required';
      }
      return null;
    },
  },

  // Content Rules
  {
    id: 'CONTENT_001',
    name: 'Summary length appropriate',
    severity: 'warning',
    validate: (advisory) => {
      if (advisory.summary.length > 500) {
        return `Summary is too long (${advisory.summary.length} chars). Consider using details field for longer descriptions.`;
      }
      if (advisory.summary.length < 10) {
        return `Summary is too short (${advisory.summary.length} chars). Please provide a more descriptive summary.`;
      }
      return null;
    },
  },
  {
    id: 'CONTENT_002',
    name: 'Details provided for complex issues',
    severity: 'warning',
    validate: (advisory) => {
      const hasCVE = advisory.aliases?.some((a) => CVE_ID_PATTERN.test(a));
      if (hasCVE && (!advisory.details || advisory.details.length < 50)) {
        return 'CVE-linked advisories should include detailed description';
      }
      return null;
    },
  },
  {
    id: 'CONTENT_003',
    name: 'CWE IDs format validation',
    severity: 'error',
    validate: (advisory) => {
      const cweIds = advisory.database_specific?.cwe_ids || [];
      const invalidCWEs = cweIds.filter((id) => !CWE_ID_PATTERN.test(id));
      if (invalidCWEs.length > 0) {
        return `Invalid CWE ID format: ${invalidCWEs.join(', ')}. Expected format: CWE-NNN`;
      }
      return null;
    },
  },

  // Affected Package Rules
  {
    id: 'AFFECTED_001',
    name: 'Package name required',
    severity: 'error',
    validate: (advisory) => {
      for (let i = 0; i < advisory.affected.length; i++) {
        const pkg = advisory.affected[i];
        if (!pkg.package?.name || pkg.package.name.trim().length === 0) {
          return `Affected package ${i + 1}: Package name is required`;
        }
      }
      return null;
    },
  },
  {
    id: 'AFFECTED_002',
    name: 'Valid ecosystem',
    severity: 'error',
    validate: (advisory) => {
      const validEcosystems: Ecosystem[] = [
        'actions',
        'composer',
        'erlang',
        'go',
        'maven',
        'npm',
        'nuget',
        'other',
        'pip',
        'pub',
        'rubygems',
        'rust',
        'swift',
      ];
      for (let i = 0; i < advisory.affected.length; i++) {
        const ecosystem = advisory.affected[i].package?.ecosystem;
        if (!ecosystem || !validEcosystems.includes(ecosystem)) {
          return `Affected package ${i + 1}: Invalid ecosystem "${ecosystem}"`;
        }
      }
      return null;
    },
  },
  {
    id: 'AFFECTED_003',
    name: 'Version range specified',
    severity: 'warning',
    validate: (advisory) => {
      for (let i = 0; i < advisory.affected.length; i++) {
        const pkg = advisory.affected[i];
        const hasVersions = pkg.versions && pkg.versions.length > 0;
        const hasRanges = pkg.ranges && pkg.ranges.length > 0;
        if (!hasVersions && !hasRanges) {
          return `Affected package ${i + 1}: No versions or ranges specified`;
        }
      }
      return null;
    },
  },
  {
    id: 'AFFECTED_004',
    name: 'Range events are valid',
    severity: 'error',
    validate: (advisory) => {
      for (let i = 0; i < advisory.affected.length; i++) {
        const ranges = advisory.affected[i].ranges || [];
        for (let j = 0; j < ranges.length; j++) {
          const events = ranges[j].events;
          if (!events || events.length === 0) {
            return `Affected package ${i + 1}, range ${j + 1}: No events specified`;
          }
          // Check for at least one introduced event
          const hasIntroduced = events.some((e) => e.introduced !== undefined);
          if (!hasIntroduced) {
            return `Affected package ${i + 1}, range ${j + 1}: Missing 'introduced' event`;
          }
        }
      }
      return null;
    },
  },

  // Reference Rules
  {
    id: 'REFERENCE_001',
    name: 'References have valid URLs',
    severity: 'error',
    validate: (advisory) => {
      const refs = advisory.references || [];
      for (let i = 0; i < refs.length; i++) {
        try {
          new URL(refs[i].url);
        } catch {
          return `Reference ${i + 1}: Invalid URL "${refs[i].url}"`;
        }
      }
      return null;
    },
  },
  {
    id: 'REFERENCE_002',
    name: 'Primary source reference recommended',
    severity: 'warning',
    validate: (advisory) => {
      const refs = advisory.references || [];
      const hasPrimarySource = refs.some((r) => r.type === 'ADVISORY' || r.type === 'REPORT');
      if (!hasPrimarySource && refs.length > 0) {
        return 'Consider including a primary source reference (ADVISORY or REPORT type)';
      }
      return null;
    },
  },

  // Alias Rules
  {
    id: 'ALIAS_001',
    name: 'CVE format validation',
    severity: 'error',
    validate: (advisory) => {
      const aliases = advisory.aliases || [];
      const cves = aliases.filter((a) => a.startsWith('CVE-'));
      const invalidCVEs = cves.filter((a) => !CVE_ID_PATTERN.test(a));
      if (invalidCVEs.length > 0) {
        return `Invalid CVE format: ${invalidCVEs.join(', ')}. Expected format: CVE-YYYY-NNNNN`;
      }
      return null;
    },
  },

  // Severity Rules
  {
    id: 'SEVERITY_001',
    name: 'CVSS score validation',
    severity: 'error',
    validate: (advisory) => {
      const severities = advisory.severity || [];
      for (const sev of severities) {
        if (sev.type === 'CVSS_V3' || sev.type === 'CVSS_V4') {
          // Extract score from vector string
          const scoreMatch = sev.score.match(/^CVSS:[34]\.\d\/.*$/);
          if (!scoreMatch) {
            return `Invalid CVSS vector string format: ${sev.score}`;
          }
        }
      }
      return null;
    },
  },

  // GitHub Specific Rules
  {
    id: 'GITHUB_001',
    name: 'Review status consistency',
    severity: 'warning',
    validate: (advisory) => {
      const dbSpecific = advisory.database_specific;
      if (dbSpecific?.github_reviewed && !dbSpecific?.github_reviewed_at) {
        return 'github_reviewed_at should be set when github_reviewed is true';
      }
      return null;
    },
  },
];

/**
 * Advisory Validator class
 */
export class AdvisoryValidator {
  private _rules: ValidationRule[] = [];
  private _customRules: ValidationRule[] = [];

  constructor(options: { includeDefaultRules?: boolean } = {}) {
    const { includeDefaultRules = true } = options;

    if (includeDefaultRules) {
      this._rules = [...VALIDATION_RULES];
    }
  }

  /**
   * Add a custom validation rule
   */
  addRule(rule: ValidationRule): void {
    this._customRules.push(rule);
  }

  /**
   * Remove a rule by ID
   */
  removeRule(ruleId: string): void {
    this._rules = this._rules.filter((r) => r.id !== ruleId);
    this._customRules = this._customRules.filter((r) => r.id !== ruleId);
  }

  /**
   * Get all active rules
   */
  getRules(): ValidationRule[] {
    return [...this._rules, ...this._customRules];
  }

  /**
   * Validate an advisory against all rules
   */
  validate(advisory: Advisory): AdvisoryValidationResult {
    const result: AdvisoryValidationResult = {
      valid: true,
      errors: [],
      warnings: [],
    };

    // First, validate against Zod schema
    const schemaResult = AdvisorySchema.safeParse(advisory);
    if (!schemaResult.success) {
      result.valid = false;
      for (const error of schemaResult.error.errors) {
        result.errors.push({
          path: error.path.join('.'),
          code: 'SCHEMA_ERROR',
          message: error.message,
        });
      }
    }

    // Run all validation rules
    const allRules = this.getRules();
    for (const rule of allRules) {
      const errorMessage = rule.validate(advisory);
      if (errorMessage) {
        if (rule.severity === 'error') {
          result.valid = false;
          result.errors.push({
            path: '',
            code: rule.id,
            message: errorMessage,
          });
        } else {
          result.warnings.push({
            path: '',
            code: rule.id,
            message: errorMessage,
            suggestion: this._getSuggestion(rule.id),
          });
        }
      }
    }

    return result;
  }

  /**
   * Quick validation - only checks for errors
   */
  isValid(advisory: Advisory): boolean {
    const result = this.validate(advisory);
    return result.valid;
  }

  /**
   * Validate raw input before parsing
   */
  validateRaw(data: unknown): AdvisoryValidationResult {
    const result: AdvisoryValidationResult = {
      valid: true,
      errors: [],
      warnings: [],
    };

    const schemaResult = AdvisorySchema.safeParse(data);
    if (!schemaResult.success) {
      result.valid = false;
      for (const error of schemaResult.error.errors) {
        result.errors.push({
          path: error.path.join('.'),
          code: 'SCHEMA_ERROR',
          message: error.message,
        });
      }
      return result;
    }

    // If schema validation passes, run full validation
    return this.validate(schemaResult.data);
  }

  /**
   * Get suggestion for a specific rule violation
   */
  private _getSuggestion(ruleId: string): string | undefined {
    const suggestions: Record<string, string> = {
      CONTENT_001: 'Keep summary under 500 characters and move details to the details field.',
      CONTENT_002:
        'Add comprehensive details explaining the vulnerability impact and attack vectors.',
      AFFECTED_003: 'Specify either a list of affected versions or version ranges.',
      REFERENCE_002: 'Include an ADVISORY or REPORT type reference for the primary source.',
      GITHUB_001: 'Set github_reviewed_at when marking an advisory as reviewed.',
    };
    return suggestions[ruleId];
  }
}

/**
 * Standalone validation function
 */
export function validateAdvisory(advisory: Advisory): AdvisoryValidationResult {
  const validator = new AdvisoryValidator();
  return validator.validate(advisory);
}

/**
 * Parse and validate raw advisory data
 */
export function parseAndValidateAdvisory(data: unknown): {
  success: boolean;
  advisory?: Advisory;
  validation: AdvisoryValidationResult;
} {
  const validator = new AdvisoryValidator();
  const validation = validator.validateRaw(data);

  if (!validation.valid) {
    return { success: false, validation };
  }

  const schemaResult = AdvisorySchema.safeParse(data);
  if (schemaResult.success) {
    return {
      success: true,
      advisory: schemaResult.data,
      validation,
    };
  }

  return { success: false, validation };
}

export default AdvisoryValidator;
