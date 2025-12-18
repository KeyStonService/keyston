/**
 * Advisory Database Service
 *
 * Core service for managing security advisories
 * Implements CRUD operations with validation
 *
 * @module services/advisory-service
 * @author SynergyMesh Team
 * @license MIT
 */

import {
  Advisory,
  AdvisorySchema,
  CreateAdvisoryInput,
  UpdateAdvisoryInput,
  AdvisorySearchFilters,
  AdvisoryValidationResult,
  Ecosystem,
} from '../types/advisory.js';
import { validateGHSAId, GHSAIdGenerator } from '../utils/ghsa.js';
import { AdvisoryValidator } from '../validators/advisory-validator.js';

/**
 * Advisory service options
 */
export interface AdvisoryServiceOptions {
  validateOnCreate?: boolean;
  validateOnUpdate?: boolean;
  autoGenerateId?: boolean;
  storageAdapter?: AdvisoryStorageAdapter;
}

/**
 * Storage adapter interface for persistence
 */
export interface AdvisoryStorageAdapter {
  get(id: string): Promise<Advisory | null>;
  list(filters: AdvisorySearchFilters): Promise<{ advisories: Advisory[]; total: number }>;
  create(advisory: Advisory): Promise<Advisory>;
  update(id: string, advisory: Advisory): Promise<Advisory>;
  delete(id: string): Promise<boolean>;
  exists(id: string): Promise<boolean>;
}

/**
 * In-memory storage adapter for testing and development
 */
export class InMemoryStorageAdapter implements AdvisoryStorageAdapter {
  private _store: Map<string, Advisory> = new Map();

  async get(id: string): Promise<Advisory | null> {
    return this._store.get(id) || null;
  }

  async list(filters: AdvisorySearchFilters): Promise<{ advisories: Advisory[]; total: number }> {
    let advisories = Array.from(this._store.values());

    // Apply filters
    if (filters.ecosystem) {
      advisories = advisories.filter((a) =>
        a.affected.some((af) => af.package.ecosystem === filters.ecosystem)
      );
    }

    if (filters.severity) {
      advisories = advisories.filter((a) => a.database_specific?.severity === filters.severity);
    }

    if (filters.package) {
      const pkgName = filters.package.toLowerCase();
      advisories = advisories.filter((a) =>
        a.affected.some((af) => af.package.name.toLowerCase().includes(pkgName))
      );
    }

    if (filters.cve_id) {
      advisories = advisories.filter((a) => a.aliases?.includes(filters.cve_id!) ?? false);
    }

    if (filters.cwe_id) {
      advisories = advisories.filter(
        (a) => a.database_specific?.cwe_ids?.includes(filters.cwe_id!) ?? false
      );
    }

    if (filters.github_reviewed !== undefined) {
      advisories = advisories.filter(
        (a) => a.database_specific?.github_reviewed === filters.github_reviewed
      );
    }

    if (filters.modified_after) {
      const afterDate = new Date(filters.modified_after);
      advisories = advisories.filter((a) => new Date(a.modified) >= afterDate);
    }

    if (filters.modified_before) {
      const beforeDate = new Date(filters.modified_before);
      advisories = advisories.filter((a) => new Date(a.modified) <= beforeDate);
    }

    // Sort by modified date descending
    advisories.sort((a, b) => new Date(b.modified).getTime() - new Date(a.modified).getTime());

    const total = advisories.length;

    // Apply pagination
    const offset = filters.offset || 0;
    const limit = filters.limit || 20;
    advisories = advisories.slice(offset, offset + limit);

    return { advisories, total };
  }

  async create(advisory: Advisory): Promise<Advisory> {
    this._store.set(advisory.id, advisory);
    return advisory;
  }

  async update(id: string, advisory: Advisory): Promise<Advisory> {
    this._store.set(id, advisory);
    return advisory;
  }

  async delete(id: string): Promise<boolean> {
    return this._store.delete(id);
  }

  async exists(id: string): Promise<boolean> {
    return this._store.has(id);
  }

  // Additional helper methods for in-memory storage
  clear(): void {
    this._store.clear();
  }

  get size(): number {
    return this._store.size;
  }
}

/**
 * Advisory Database Service
 *
 * Main service class for managing security advisories
 */
export class AdvisoryService {
  private _validator: AdvisoryValidator;
  private _storage: AdvisoryStorageAdapter;
  private _idGenerator: GHSAIdGenerator;
  private _options: Required<AdvisoryServiceOptions>;

  constructor(options: AdvisoryServiceOptions = {}) {
    this._options = {
      validateOnCreate: options.validateOnCreate ?? true,
      validateOnUpdate: options.validateOnUpdate ?? true,
      autoGenerateId: options.autoGenerateId ?? true,
      storageAdapter: options.storageAdapter ?? new InMemoryStorageAdapter(),
    };

    this._validator = new AdvisoryValidator();
    this._storage = this._options.storageAdapter;
    this._idGenerator = new GHSAIdGenerator();
  }

  /**
   * Get an advisory by ID
   *
   * @param id - GHSA ID of the advisory
   * @returns Advisory or null if not found
   */
  async get(id: string): Promise<Advisory | null> {
    if (!validateGHSAId(id)) {
      throw new Error(`Invalid GHSA ID format: ${id}`);
    }
    return this._storage.get(id);
  }

  /**
   * List advisories with optional filters
   *
   * @param filters - Search filters
   * @returns Paginated list of advisories
   */
  async list(filters: AdvisorySearchFilters = {}): Promise<{
    advisories: Advisory[];
    total: number;
    offset: number;
    limit: number;
  }> {
    const { advisories, total } = await this._storage.list(filters);
    return {
      advisories,
      total,
      offset: filters.offset || 0,
      limit: filters.limit || 20,
    };
  }

  /**
   * Create a new advisory
   *
   * @param input - Advisory data (without ID and modified timestamp)
   * @returns Created advisory
   */
  async create(input: CreateAdvisoryInput): Promise<{
    advisory: Advisory;
    validation: AdvisoryValidationResult;
  }> {
    // Generate ID if auto-generation is enabled
    const id = this._options.autoGenerateId
      ? this._idGenerator.generate()
      : (input as unknown as Advisory).id;

    if (!id) {
      throw new Error('Advisory ID is required when autoGenerateId is disabled');
    }

    // Check for duplicate
    if (await this._storage.exists(id)) {
      throw new Error(`Advisory with ID ${id} already exists`);
    }

    // Build advisory object
    const advisory: Advisory = {
      ...input,
      id,
      schema_version: '1.6.0',
      modified: new Date().toISOString(),
      published: input.published || new Date().toISOString(),
    };

    // Validate if enabled
    let validation: AdvisoryValidationResult = {
      valid: true,
      errors: [],
      warnings: [],
    };

    if (this._options.validateOnCreate) {
      validation = this._validator.validate(advisory);
      if (!validation.valid) {
        throw new ValidationError('Advisory validation failed', validation);
      }
    }

    // Store the advisory
    const created = await this._storage.create(advisory);
    return { advisory: created, validation };
  }

  /**
   * Update an existing advisory
   *
   * @param id - GHSA ID of the advisory to update
   * @param input - Update data
   * @returns Updated advisory
   */
  async update(
    id: string,
    input: UpdateAdvisoryInput
  ): Promise<{
    advisory: Advisory;
    validation: AdvisoryValidationResult;
  }> {
    if (!validateGHSAId(id)) {
      throw new Error(`Invalid GHSA ID format: ${id}`);
    }

    const existing = await this._storage.get(id);
    if (!existing) {
      throw new Error(`Advisory not found: ${id}`);
    }

    // Merge updates with existing data
    const updated: Advisory = {
      ...existing,
      ...input,
      id, // Preserve original ID
      schema_version: existing.schema_version, // Preserve schema version
      modified: new Date().toISOString(), // Update modified timestamp
    };

    // Validate if enabled
    let validation: AdvisoryValidationResult = {
      valid: true,
      errors: [],
      warnings: [],
    };

    if (this._options.validateOnUpdate) {
      validation = this._validator.validate(updated);
      if (!validation.valid) {
        throw new ValidationError('Advisory validation failed', validation);
      }
    }

    // Store the update
    const stored = await this._storage.update(id, updated);
    return { advisory: stored, validation };
  }

  /**
   * Delete an advisory
   *
   * @param id - GHSA ID of the advisory to delete
   * @returns True if deleted, false if not found
   */
  async delete(id: string): Promise<boolean> {
    if (!validateGHSAId(id)) {
      throw new Error(`Invalid GHSA ID format: ${id}`);
    }
    return this._storage.delete(id);
  }

  /**
   * Check if an advisory exists
   *
   * @param id - GHSA ID to check
   * @returns True if exists
   */
  async exists(id: string): Promise<boolean> {
    if (!validateGHSAId(id)) {
      return false;
    }
    return this._storage.exists(id);
  }

  /**
   * Validate an advisory without storing
   *
   * @param advisory - Advisory to validate
   * @returns Validation result
   */
  validate(advisory: Advisory): AdvisoryValidationResult {
    return this._validator.validate(advisory);
  }

  /**
   * Search advisories by CVE ID
   *
   * @param cveId - CVE ID to search for
   * @returns Matching advisories
   */
  async searchByCVE(cveId: string): Promise<Advisory[]> {
    const { advisories } = await this.list({ cve_id: cveId, limit: 100 });
    return advisories;
  }

  /**
   * Search advisories by package name
   *
   * @param packageName - Package name to search
   * @param ecosystem - Optional ecosystem filter
   * @returns Matching advisories
   */
  async searchByPackage(packageName: string, ecosystem?: Ecosystem): Promise<Advisory[]> {
    const { advisories } = await this.list({
      package: packageName,
      ecosystem,
      limit: 100,
    });
    return advisories;
  }

  /**
   * Get statistics about advisories
   *
   * @returns Statistics object
   */
  async getStats(): Promise<AdvisoryStats> {
    const { advisories, total } = await this.list({ limit: 10000 });

    const stats: AdvisoryStats = {
      total,
      byEcosystem: {},
      bySeverity: { CRITICAL: 0, HIGH: 0, MEDIUM: 0, LOW: 0 },
      reviewed: 0,
      unreviewed: 0,
      lastUpdated: null,
    };

    for (const advisory of advisories) {
      // Count by ecosystem
      for (const affected of advisory.affected) {
        const eco = affected.package.ecosystem;
        stats.byEcosystem[eco] = (stats.byEcosystem[eco] || 0) + 1;
      }

      // Count by severity
      const severity = advisory.database_specific?.severity;
      if (severity && severity in stats.bySeverity) {
        stats.bySeverity[severity]++;
      }

      // Count reviewed status
      if (advisory.database_specific?.github_reviewed) {
        stats.reviewed++;
      } else {
        stats.unreviewed++;
      }

      // Track last updated
      const modified = new Date(advisory.modified);
      if (!stats.lastUpdated || modified > stats.lastUpdated) {
        stats.lastUpdated = modified;
      }
    }

    return stats;
  }

  /**
   * Import advisories from OSV format
   *
   * @param data - Array of advisory data
   * @returns Import results
   */
  async importBatch(data: unknown[]): Promise<BatchImportResult> {
    const results: BatchImportResult = {
      total: data.length,
      success: 0,
      failed: 0,
      errors: [],
    };

    for (let i = 0; i < data.length; i++) {
      try {
        const parsed = AdvisorySchema.safeParse(data[i]);
        if (parsed.success) {
          await this._storage.create(parsed.data);
          results.success++;
        } else {
          results.failed++;
          results.errors.push({
            index: i,
            message: parsed.error.message,
          });
        }
      } catch (error) {
        results.failed++;
        results.errors.push({
          index: i,
          message: error instanceof Error ? error.message : 'Unknown error',
        });
      }
    }

    return results;
  }

  /**
   * Export all advisories in OSV format
   *
   * @returns Array of advisories
   */
  async exportAll(): Promise<Advisory[]> {
    const { advisories } = await this.list({ limit: 100000 });
    return advisories;
  }

  /**
   * Get the validator instance for custom rule management
   */
  get validator(): AdvisoryValidator {
    return this._validator;
  }
}

/**
 * Statistics about advisories
 */
export interface AdvisoryStats {
  total: number;
  byEcosystem: Record<string, number>;
  bySeverity: Record<string, number>;
  reviewed: number;
  unreviewed: number;
  lastUpdated: Date | null;
}

/**
 * Batch import result
 */
export interface BatchImportResult {
  total: number;
  success: number;
  failed: number;
  errors: Array<{ index: number; message: string }>;
}

/**
 * Custom validation error with details
 */
export class ValidationError extends Error {
  constructor(
    message: string,
    public readonly validation: AdvisoryValidationResult
  ) {
    super(message);
    this.name = 'ValidationError';
  }
}

export default AdvisoryService;
