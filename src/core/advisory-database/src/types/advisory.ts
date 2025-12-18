/**
 * Advisory Database Type Definitions
 *
 * Open Source Vulnerability (OSV) format compatible types
 * Based on: https://ossf.github.io/osv-schema/
 *
 * @module types/advisory
 * @author SynergyMesh Team
 * @license MIT
 */

import { z } from 'zod';

// ============================================================================
// Supported Ecosystems (matching GitHub Advisory Database)
// ============================================================================

/**
 * Supported package ecosystems
 * These match the ecosystems supported by GitHub Advisory Database
 */
export const EcosystemSchema = z.enum([
  'actions', // GitHub Actions
  'composer', // PHP Composer (packagist.org)
  'erlang', // Erlang (hex.pm)
  'go', // Go modules (pkg.go.dev)
  'maven', // Java Maven (repo.maven.apache.org)
  'npm', // Node.js (npmjs.com)
  'nuget', // .NET NuGet (nuget.org)
  'other', // Other ecosystems
  'pip', // Python (pypi.org)
  'pub', // Dart/Flutter (pub.dev)
  'rubygems', // Ruby (rubygems.org)
  'rust', // Rust Cargo (crates.io)
  'swift', // Swift packages
]);

export type Ecosystem = z.infer<typeof EcosystemSchema>;

// ============================================================================
// GHSA ID Format
// ============================================================================

/**
 * GHSA ID validation pattern
 * Format: GHSA-xxxx-xxxx-xxxx where x is from set: 23456789cfghjmpqrvwx
 */
export const GHSA_ID_PATTERN =
  /^GHSA-[23456789cfghjmpqrvwx]{4}-[23456789cfghjmpqrvwx]{4}-[23456789cfghjmpqrvwx]{4}$/;

/**
 * CVE ID validation pattern
 * Format: CVE-YYYY-NNNNN+
 */
export const CVE_ID_PATTERN = /^CVE-\d{4}-\d{4,}$/;

/**
 * CWE ID validation pattern
 * Format: CWE-NNN+
 */
export const CWE_ID_PATTERN = /^CWE-\d+$/;

// ============================================================================
// Severity Schemas
// ============================================================================

/**
 * CVSS 3.x vector schema
 */
export const CvssVectorSchema = z.object({
  vectorString: z.string(),
  baseScore: z.number().min(0).max(10),
  baseSeverity: z.enum(['NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
});

/**
 * CVSS 4.0 vector schema
 */
export const Cvss4VectorSchema = z.object({
  vectorString: z.string(),
  baseScore: z.number().min(0).max(10),
  baseSeverity: z.enum(['NONE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']),
});

/**
 * Severity level schema
 */
export const SeverityLevelSchema = z.enum(['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']);

export type SeverityLevel = z.infer<typeof SeverityLevelSchema>;

// ============================================================================
// Reference Schema
// ============================================================================

/**
 * Reference types matching OSV spec
 */
export const ReferenceTypeSchema = z.enum([
  'ADVISORY',
  'ARTICLE',
  'DETECTION',
  'DISCUSSION',
  'EVIDENCE',
  'FIX',
  'GIT',
  'INTRODUCED',
  'PACKAGE',
  'REPORT',
  'WEB',
]);

/**
 * Reference schema for external links
 */
export const ReferenceSchema = z.object({
  type: ReferenceTypeSchema,
  url: z.string().url(),
});

export type Reference = z.infer<typeof ReferenceSchema>;

// ============================================================================
// Affected Package Schema
// ============================================================================

/**
 * Event type for version ranges
 */
export const EventTypeSchema = z.enum(['introduced', 'fixed', 'last_affected', 'limit']);

/**
 * Range event schema
 */
export const RangeEventSchema = z.object({
  introduced: z.string().optional(),
  fixed: z.string().optional(),
  last_affected: z.string().optional(),
  limit: z.string().optional(),
});

/**
 * Range type for version ranges
 */
export const RangeTypeSchema = z.enum(['SEMVER', 'ECOSYSTEM', 'GIT']);

/**
 * Database-specific range info (GitHub specific)
 */
export const RangeDatabaseSpecificSchema = z
  .object({
    last_known_affected_version_range: z.string().optional(),
  })
  .passthrough();

/**
 * Version range schema
 */
export const RangeSchema = z.object({
  type: RangeTypeSchema,
  repo: z.string().optional(),
  events: z.array(RangeEventSchema),
  database_specific: RangeDatabaseSpecificSchema.optional(),
});

export type Range = z.infer<typeof RangeSchema>;

/**
 * Package identifier schema
 */
export const PackageSchema = z.object({
  name: z.string(),
  ecosystem: EcosystemSchema,
  purl: z.string().optional(),
});

/**
 * Affected database-specific info
 */
export const AffectedDatabaseSpecificSchema = z
  .object({
    source: z.string().optional(),
  })
  .passthrough();

/**
 * Affected package schema
 */
export const AffectedSchema = z.object({
  package: PackageSchema,
  severity: z
    .array(
      z.object({
        type: z.enum(['CVSS_V2', 'CVSS_V3', 'CVSS_V4']),
        score: z.string(),
      })
    )
    .optional(),
  ranges: z.array(RangeSchema).optional(),
  versions: z.array(z.string()).optional(),
  ecosystem_specific: z.record(z.unknown()).optional(),
  database_specific: AffectedDatabaseSpecificSchema.optional(),
});

export type Affected = z.infer<typeof AffectedSchema>;

// ============================================================================
// Credit Schema
// ============================================================================

/**
 * Credit type schema
 */
export const CreditTypeSchema = z.enum([
  'FINDER',
  'REPORTER',
  'ANALYST',
  'COORDINATOR',
  'REMEDIATION_DEVELOPER',
  'REMEDIATION_REVIEWER',
  'REMEDIATION_VERIFIER',
  'TOOL',
  'SPONSOR',
  'OTHER',
]);

/**
 * Credit schema for vulnerability credits
 */
export const CreditSchema = z.object({
  name: z.string(),
  contact: z.array(z.string()).optional(),
  type: CreditTypeSchema.optional(),
});

export type Credit = z.infer<typeof CreditSchema>;

// ============================================================================
// Database Specific Schema (GitHub)
// ============================================================================

/**
 * GitHub-specific database fields
 */
export const GitHubDatabaseSpecificSchema = z.object({
  severity: SeverityLevelSchema.optional(),
  cwe_ids: z.array(z.string().regex(CWE_ID_PATTERN)).optional(),
  github_reviewed: z.boolean().optional(),
  github_reviewed_at: z.string().datetime().optional(),
  nvd_published_at: z.string().datetime().optional(),
});

export type GitHubDatabaseSpecific = z.infer<typeof GitHubDatabaseSpecificSchema>;

// ============================================================================
// Main Advisory Schema (OSV Format)
// ============================================================================

/**
 * Complete OSV-format advisory schema
 */
export const AdvisorySchema = z.object({
  // OSV Standard Fields
  schema_version: z.string().default('1.6.0'),
  id: z.string().regex(GHSA_ID_PATTERN),
  modified: z.string().datetime(),
  published: z.string().datetime().optional(),
  withdrawn: z.string().datetime().optional(),
  aliases: z.array(z.string()).optional(),
  related: z.array(z.string()).optional(),
  summary: z.string(),
  details: z.string().optional(),
  severity: z
    .array(
      z.object({
        type: z.enum(['CVSS_V2', 'CVSS_V3', 'CVSS_V4']),
        score: z.string(),
      })
    )
    .optional(),
  affected: z.array(AffectedSchema),
  references: z.array(ReferenceSchema).optional(),
  credits: z.array(CreditSchema).optional(),
  database_specific: GitHubDatabaseSpecificSchema.optional(),
});

export type Advisory = z.infer<typeof AdvisorySchema>;

// ============================================================================
// Advisory Input/Output Types
// ============================================================================

/**
 * Input for creating new advisory
 */
export const CreateAdvisoryInputSchema = AdvisorySchema.omit({
  id: true,
  modified: true,
  schema_version: true,
});

export type CreateAdvisoryInput = z.infer<typeof CreateAdvisoryInputSchema>;

/**
 * Input for updating advisory
 */
export const UpdateAdvisoryInputSchema = AdvisorySchema.partial().omit({
  id: true,
  schema_version: true,
});

export type UpdateAdvisoryInput = z.infer<typeof UpdateAdvisoryInputSchema>;

/**
 * Advisory search filters
 */
export const AdvisorySearchFiltersSchema = z.object({
  ecosystem: EcosystemSchema.optional(),
  severity: SeverityLevelSchema.optional(),
  package: z.string().optional(),
  cve_id: z.string().optional(),
  cwe_id: z.string().optional(),
  github_reviewed: z.boolean().optional(),
  modified_after: z.string().datetime().optional(),
  modified_before: z.string().datetime().optional(),
  limit: z.number().min(1).max(100).optional().default(20),
  offset: z.number().min(0).optional().default(0),
});

export type AdvisorySearchFilters = z.input<typeof AdvisorySearchFiltersSchema>;

/**
 * Advisory validation result
 */
export interface AdvisoryValidationResult {
  valid: boolean;
  errors: AdvisoryValidationError[];
  warnings: AdvisoryValidationWarning[];
}

export interface AdvisoryValidationError {
  path: string;
  code: string;
  message: string;
}

export interface AdvisoryValidationWarning {
  path: string;
  code: string;
  message: string;
  suggestion?: string;
}

// ============================================================================
// Bot Configuration Types
// ============================================================================

/**
 * Staging branch configuration
 */
export interface StagingBranchConfig {
  baseBranch: string;
  branchPattern: string;
  autoCleanup: boolean;
  cleanupDelayDays: number;
}

/**
 * Stale PR configuration
 */
export interface StalePRConfig {
  enabled: boolean;
  staleDays: number;
  closeDays: number;
  staleLabel: string;
  exemptLabels: string[];
  staleMessage: string;
  closeMessage: string;
}

/**
 * Advisory bot configuration
 */
export interface AdvisoryBotConfig {
  stagingBranch: StagingBranchConfig;
  stalePR: StalePRConfig;
  curationTeam: string[];
  supportedEcosystems: Ecosystem[];
  validationRules: ValidationRule[];
}

export interface ValidationRule {
  id: string;
  name: string;
  severity: 'error' | 'warning';
  enabled: boolean;
  validate: (advisory: Advisory) => boolean;
  message: string;
}
