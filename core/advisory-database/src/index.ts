/**
 * Advisory Database Module
 *
 * Professional advisory database service - GitHub Advisory Database compatible
 * Implements OSV format compliance for security vulnerability management
 *
 * @module @machinenativeops/advisory-database
 * @author SynergyMesh Team
 * @license MIT
 *
 * @example
 * import {
 *   AdvisoryService,
 *   AdvisoryBotEngine,
 *   AdvisoryValidator,
 *   generateGHSAId
 * } from '@machinenativeops/advisory-database';
 *
 * // Create a new advisory service
 * const service = new AdvisoryService();
 *
 * // Create an advisory
 * const { advisory } = await service.create({
 *   summary: 'SQL Injection in example-package',
 *   affected: [{
 *     package: { name: 'example-package', ecosystem: 'npm' },
 *     ranges: [{
 *       type: 'SEMVER',
 *       events: [
 *         { introduced: '1.0.0' },
 *         { fixed: '1.0.5' }
 *       ]
 *     }]
 *   }]
 * });
 *
 * // Use the bot engine for workflow automation
 * const bot = new AdvisoryBotEngine();
 * const workflow = bot.generateStalePRWorkflow();
 */

// ============================================================================
// Type Exports
// ============================================================================

export type {
  Ecosystem,
  SeverityLevel,
  Reference,
  Range,
  Affected,
  Credit,
  GitHubDatabaseSpecific,
  Advisory,
  CreateAdvisoryInput,
  UpdateAdvisoryInput,
  AdvisorySearchFilters,
  AdvisoryValidationResult,
  AdvisoryValidationError,
  AdvisoryValidationWarning,
  StagingBranchConfig,
  StalePRConfig,
  AdvisoryBotConfig,
  ValidationRule,
} from './types/advisory.js';

export {
  EcosystemSchema,
  SeverityLevelSchema,
  ReferenceSchema,
  ReferenceTypeSchema,
  RangeSchema,
  RangeTypeSchema,
  AffectedSchema,
  CreditSchema,
  CreditTypeSchema,
  AdvisorySchema,
  CreateAdvisoryInputSchema,
  UpdateAdvisoryInputSchema,
  AdvisorySearchFiltersSchema,
  GitHubDatabaseSpecificSchema,
  GHSA_ID_PATTERN,
  CVE_ID_PATTERN,
  CWE_ID_PATTERN,
} from './types/advisory.js';

// ============================================================================
// GHSA ID Utilities
// ============================================================================

export {
  generateGHSAId,
  validateGHSAId,
  parseGHSAId,
  generateBatchGHSAIds,
  computeDeterministicGHSAId,
  extractGHSAIds,
  GHSAIdGenerator,
} from './utils/ghsa.js';

// ============================================================================
// Validator Exports
// ============================================================================

export {
  AdvisoryValidator,
  validateAdvisory,
  parseAndValidateAdvisory,
} from './validators/advisory-validator.js';

// ============================================================================
// Service Exports
// ============================================================================

export {
  AdvisoryService,
  InMemoryStorageAdapter,
  ValidationError,
} from './services/advisory-service.js';

export type {
  AdvisoryServiceOptions,
  AdvisoryStorageAdapter,
  AdvisoryStats,
  BatchImportResult,
} from './services/advisory-service.js';

// ============================================================================
// Bot Engine Exports
// ============================================================================

export { AdvisoryBotEngine, DEFAULT_BOT_CONFIG } from './services/advisory-bot.js';

export type {
  PullRequestInfo,
  BranchOperationResult,
  StaleCheckResult,
  CurationAction,
} from './services/advisory-bot.js';

// ============================================================================
// Constants
// ============================================================================

/**
 * Supported ecosystems matching GitHub Advisory Database
 */
export const SUPPORTED_ECOSYSTEMS = [
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
] as const;

/**
 * OSV schema version
 */
export const OSV_SCHEMA_VERSION = '1.6.0';

/**
 * Module version
 */
export const VERSION = '1.0.0';
