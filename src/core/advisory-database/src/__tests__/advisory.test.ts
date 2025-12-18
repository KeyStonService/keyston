/**
 * Advisory Database Module Tests
 *
 * @module __tests__/advisory.test
 */

import {
  generateGHSAId,
  validateGHSAId,
  parseGHSAId,
  generateBatchGHSAIds,
  extractGHSAIds,
  GHSAIdGenerator,
} from '../utils/ghsa.js';

import {
  AdvisoryValidator,
} from '../validators/advisory-validator.js';

import {
  AdvisoryService,
  InMemoryStorageAdapter,
  ValidationError,
} from '../services/advisory-service.js';

import {
  AdvisoryBotEngine,
  PullRequestInfo,
} from '../services/advisory-bot.js';

import {
  Advisory,
  GHSA_ID_PATTERN,
} from '../types/advisory.js';

// ============================================================================
// GHSA ID Tests
// ============================================================================

describe('GHSA ID Utilities', () => {
  describe('generateGHSAId', () => {
    it('should generate valid GHSA ID format', () => {
      const id = generateGHSAId();
      expect(id).toMatch(GHSA_ID_PATTERN);
    });

    it('should generate unique IDs', () => {
      const ids = new Set<string>();
      for (let i = 0; i < 100; i++) {
        ids.add(generateGHSAId());
      }
      expect(ids.size).toBe(100);
    });

    it('should start with GHSA prefix', () => {
      const id = generateGHSAId();
      expect(id).toMatch(/^GHSA-/);
    });

    it('should have three segments of four characters', () => {
      const id = generateGHSAId();
      const parts = id.split('-');
      expect(parts).toHaveLength(4);
      expect(parts[0]).toBe('GHSA');
      expect(parts[1]).toHaveLength(4);
      expect(parts[2]).toHaveLength(4);
      expect(parts[3]).toHaveLength(4);
    });
  });

  describe('validateGHSAId', () => {
    it('should validate correct GHSA IDs', () => {
      expect(validateGHSAId('GHSA-c3gv-9cxf-6f57')).toBe(true);
      expect(validateGHSAId('GHSA-2222-3333-4444')).toBe(true);
    });

    it('should reject invalid GHSA IDs', () => {
      expect(validateGHSAId('GHSA-invalid')).toBe(false);
      expect(validateGHSAId('CVE-2024-1234')).toBe(false);
      expect(validateGHSAId('ghsa-c3gv-9cxf-6f57')).toBe(false); // lowercase
      expect(validateGHSAId('GHSA-AAAA-BBBB-CCCC')).toBe(false); // invalid chars
      expect(validateGHSAId('')).toBe(false);
    });
  });

  describe('parseGHSAId', () => {
    it('should parse valid GHSA IDs', () => {
      const parsed = parseGHSAId('GHSA-c3gv-9cxf-6f57');
      expect(parsed).toEqual({
        prefix: 'GHSA',
        segment1: 'c3gv',
        segment2: '9cxf',
        segment3: '6f57',
      });
    });

    it('should return null for invalid IDs', () => {
      expect(parseGHSAId('invalid')).toBeNull();
    });
  });

  describe('generateBatchGHSAIds', () => {
    it('should generate specified number of unique IDs', () => {
      const ids = generateBatchGHSAIds(10);
      expect(ids).toHaveLength(10);
      expect(new Set(ids).size).toBe(10);
    });

    it('should avoid existing IDs', () => {
      const existing = new Set(['GHSA-2222-3333-4444']);
      const ids = generateBatchGHSAIds(5, existing);
      expect(ids).not.toContain('GHSA-2222-3333-4444');
    });
  });

  describe('extractGHSAIds', () => {
    it('should extract GHSA IDs from text', () => {
      const text = 'See GHSA-c3gv-9cxf-6f57 and also GHSA-x2p5-qgf7-r8m4';
      const ids = extractGHSAIds(text);
      expect(ids).toHaveLength(2);
      expect(ids).toContain('GHSA-c3gv-9cxf-6f57');
      expect(ids).toContain('GHSA-x2p5-qgf7-r8m4');
    });

    it('should return empty array for text without GHSA IDs', () => {
      const ids = extractGHSAIds('No GHSA IDs here');
      expect(ids).toHaveLength(0);
    });

    it('should deduplicate found IDs', () => {
      const text = 'GHSA-c3gv-9cxf-6f57 is mentioned twice: GHSA-c3gv-9cxf-6f57';
      const ids = extractGHSAIds(text);
      expect(ids).toHaveLength(1);
    });
  });

  describe('GHSAIdGenerator class', () => {
    it('should generate unique IDs across multiple calls', () => {
      const generator = new GHSAIdGenerator();
      const id1 = generator.generate();
      const id2 = generator.generate();
      expect(id1).not.toBe(id2);
      expect(generator.count).toBe(2);
    });

    it('should track generated IDs', () => {
      const generator = new GHSAIdGenerator();
      const id = generator.generate();
      expect(generator.hasGenerated(id)).toBe(true);
    });

    it('should allow registering external IDs', () => {
      const generator = new GHSAIdGenerator();
      generator.register('GHSA-c3gv-9cxf-6f57');
      expect(generator.count).toBe(1);
    });

    it('should clear registered IDs', () => {
      const generator = new GHSAIdGenerator();
      generator.generate();
      generator.clear();
      expect(generator.count).toBe(0);
    });
  });
});

// ============================================================================
// Advisory Validator Tests
// ============================================================================

describe('AdvisoryValidator', () => {
  const createValidAdvisory = (): Advisory => ({
    schema_version: '1.6.0',
    id: 'GHSA-c3gv-9cxf-6f57',
    modified: '2024-01-15T10:00:00Z',
    summary: 'SQL Injection vulnerability in example-package',
    affected: [
      {
        package: {
          name: 'example-package',
          ecosystem: 'npm',
        },
        ranges: [
          {
            type: 'SEMVER',
            events: [
              { introduced: '1.0.0' },
              { fixed: '1.0.5' },
            ],
          },
        ],
      },
    ],
  });

  describe('validate', () => {
    it('should validate a correct advisory', () => {
      const validator = new AdvisoryValidator();
      const result = validator.validate(createValidAdvisory());
      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should detect invalid GHSA ID', () => {
      const validator = new AdvisoryValidator();
      const advisory = createValidAdvisory();
      advisory.id = 'invalid-id';
      const result = validator.validate(advisory);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.code === 'STRUCTURE_001')).toBe(true);
    });

    it('should detect missing summary', () => {
      const validator = new AdvisoryValidator();
      const advisory = createValidAdvisory();
      advisory.summary = '';
      const result = validator.validate(advisory);
      expect(result.valid).toBe(false);
    });

    it('should detect missing affected packages', () => {
      const validator = new AdvisoryValidator();
      const advisory = createValidAdvisory();
      advisory.affected = [];
      const result = validator.validate(advisory);
      expect(result.valid).toBe(false);
    });

    it('should validate CWE ID format', () => {
      const validator = new AdvisoryValidator();
      const advisory = createValidAdvisory();
      advisory.database_specific = {
        cwe_ids: ['CWE-89', 'CWE-79'],
      };
      const result = validator.validate(advisory);
      expect(result.errors.filter(e => e.code === 'CONTENT_003')).toHaveLength(0);
    });

    it('should detect invalid CWE ID format', () => {
      const validator = new AdvisoryValidator();
      const advisory = createValidAdvisory();
      advisory.database_specific = {
        cwe_ids: ['INVALID-CWE'],
      };
      const result = validator.validate(advisory);
      expect(result.valid).toBe(false);
      expect(result.errors.some(e => e.code === 'CONTENT_003')).toBe(true);
    });
  });

  describe('isValid', () => {
    it('should return true for valid advisory', () => {
      const validator = new AdvisoryValidator();
      expect(validator.isValid(createValidAdvisory())).toBe(true);
    });

    it('should return false for invalid advisory', () => {
      const validator = new AdvisoryValidator();
      const advisory = createValidAdvisory();
      advisory.id = 'invalid';
      expect(validator.isValid(advisory)).toBe(false);
    });
  });

  describe('custom rules', () => {
    it('should allow adding custom rules', () => {
      const validator = new AdvisoryValidator();
      validator.addRule({
        id: 'CUSTOM_001',
        name: 'Custom rule',
        severity: 'error',
        validate: () => 'Custom error',
      });
      const result = validator.validate(createValidAdvisory());
      expect(result.errors.some(e => e.code === 'CUSTOM_001')).toBe(true);
    });

    it('should allow removing rules', () => {
      const validator = new AdvisoryValidator();
      validator.removeRule('STRUCTURE_001');
      const advisory = createValidAdvisory();
      advisory.id = 'invalid';
      const result = validator.validate(advisory);
      expect(result.errors.filter(e => e.code === 'STRUCTURE_001')).toHaveLength(0);
    });
  });
});

// ============================================================================
// Advisory Service Tests
// ============================================================================

describe('AdvisoryService', () => {
  let service: AdvisoryService;

  beforeEach(() => {
    service = new AdvisoryService();
  });

  describe('create', () => {
    it('should create a new advisory', async () => {
      const { advisory } = await service.create({
        summary: 'Test vulnerability',
        affected: [
          {
            package: { name: 'test-package', ecosystem: 'npm' },
            ranges: [{
              type: 'SEMVER',
              events: [{ introduced: '1.0.0' }, { fixed: '1.0.1' }],
            }],
          },
        ],
      });

      expect(advisory.id).toMatch(GHSA_ID_PATTERN);
      expect(advisory.summary).toBe('Test vulnerability');
      expect(advisory.modified).toBeDefined();
    });

    it('should auto-generate ID', async () => {
      const { advisory } = await service.create({
        summary: 'Test vulnerability',
        affected: [{
          package: { name: 'test-package', ecosystem: 'npm' },
          ranges: [{
            type: 'SEMVER',
            events: [{ introduced: '1.0.0' }],
          }],
        }],
      });

      expect(advisory.id).toMatch(GHSA_ID_PATTERN);
    });

    it('should throw validation error for invalid input', async () => {
      await expect(service.create({
        summary: '',  // Empty summary
        affected: [{
          package: { name: 'test', ecosystem: 'npm' },
          ranges: [{
            type: 'SEMVER',
            events: [{ introduced: '1.0.0' }],
          }],
        }],
      })).rejects.toThrow(ValidationError);
    });
  });

  describe('get', () => {
    it('should retrieve created advisory', async () => {
      const { advisory } = await service.create({
        summary: 'Test vulnerability',
        affected: [{
          package: { name: 'test', ecosystem: 'npm' },
          ranges: [{
            type: 'SEMVER',
            events: [{ introduced: '1.0.0' }],
          }],
        }],
      });

      const retrieved = await service.get(advisory.id);
      expect(retrieved).toEqual(advisory);
    });

    it('should return null for non-existent advisory', async () => {
      const result = await service.get('GHSA-c3gv-9cxf-6f57');
      expect(result).toBeNull();
    });

    it('should throw for invalid ID format', async () => {
      await expect(service.get('invalid-id')).rejects.toThrow('Invalid GHSA ID format');
    });
  });

  describe('update', () => {
    it('should update existing advisory', async () => {
      const { advisory } = await service.create({
        summary: 'Original summary',
        affected: [{
          package: { name: 'test', ecosystem: 'npm' },
          ranges: [{
            type: 'SEMVER',
            events: [{ introduced: '1.0.0' }],
          }],
        }],
      });

      const { advisory: updated } = await service.update(advisory.id, {
        summary: 'Updated summary',
      });

      expect(updated.summary).toBe('Updated summary');
      expect(updated.id).toBe(advisory.id);
    });

    it('should throw for non-existent advisory', async () => {
      await expect(service.update('GHSA-c3gv-9cxf-6f57', {
        summary: 'Update',
      })).rejects.toThrow('Advisory not found');
    });
  });

  describe('delete', () => {
    it('should delete existing advisory', async () => {
      const { advisory } = await service.create({
        summary: 'To be deleted',
        affected: [{
          package: { name: 'test', ecosystem: 'npm' },
          ranges: [{
            type: 'SEMVER',
            events: [{ introduced: '1.0.0' }],
          }],
        }],
      });

      const deleted = await service.delete(advisory.id);
      expect(deleted).toBe(true);

      const retrieved = await service.get(advisory.id);
      expect(retrieved).toBeNull();
    });
  });

  describe('list', () => {
    it('should list all advisories', async () => {
      await service.create({
        summary: 'Advisory 1',
        affected: [{
          package: { name: 'pkg1', ecosystem: 'npm' },
          ranges: [{ type: 'SEMVER', events: [{ introduced: '1.0.0' }] }],
        }],
      });

      await service.create({
        summary: 'Advisory 2',
        affected: [{
          package: { name: 'pkg2', ecosystem: 'pip' },
          ranges: [{ type: 'SEMVER', events: [{ introduced: '1.0.0' }] }],
        }],
      });

      const { advisories, total } = await service.list();
      expect(total).toBe(2);
      expect(advisories).toHaveLength(2);
    });

    it('should filter by ecosystem', async () => {
      await service.create({
        summary: 'NPM Advisory',
        affected: [{
          package: { name: 'pkg1', ecosystem: 'npm' },
          ranges: [{ type: 'SEMVER', events: [{ introduced: '1.0.0' }] }],
        }],
      });

      await service.create({
        summary: 'PIP Advisory',
        affected: [{
          package: { name: 'pkg2', ecosystem: 'pip' },
          ranges: [{ type: 'SEMVER', events: [{ introduced: '1.0.0' }] }],
        }],
      });

      const { advisories } = await service.list({ ecosystem: 'npm' });
      expect(advisories).toHaveLength(1);
      expect(advisories[0].summary).toBe('NPM Advisory');
    });
  });

  describe('searchByPackage', () => {
    it('should find advisories by package name', async () => {
      await service.create({
        summary: 'Lodash vulnerability',
        affected: [{
          package: { name: 'lodash', ecosystem: 'npm' },
          ranges: [{ type: 'SEMVER', events: [{ introduced: '1.0.0' }] }],
        }],
      });

      const results = await service.searchByPackage('lodash');
      expect(results).toHaveLength(1);
      expect(results[0].affected[0].package.name).toBe('lodash');
    });
  });

  describe('getStats', () => {
    it('should return correct statistics', async () => {
      await service.create({
        summary: 'Critical vuln',
        affected: [{
          package: { name: 'pkg1', ecosystem: 'npm' },
          ranges: [{ type: 'SEMVER', events: [{ introduced: '1.0.0' }] }],
        }],
        database_specific: { severity: 'CRITICAL' },
      });

      await service.create({
        summary: 'High vuln',
        affected: [{
          package: { name: 'pkg2', ecosystem: 'pip' },
          ranges: [{ type: 'SEMVER', events: [{ introduced: '1.0.0' }] }],
        }],
        database_specific: { severity: 'HIGH', github_reviewed: true },
      });

      const stats = await service.getStats();
      expect(stats.total).toBe(2);
      expect(stats.bySeverity.CRITICAL).toBe(1);
      expect(stats.bySeverity.HIGH).toBe(1);
      expect(stats.reviewed).toBe(1);
      expect(stats.unreviewed).toBe(1);
    });
  });
});

// ============================================================================
// Advisory Bot Engine Tests
// ============================================================================

describe('AdvisoryBotEngine', () => {
  let bot: AdvisoryBotEngine;

  beforeEach(() => {
    bot = new AdvisoryBotEngine();
  });

  describe('configuration', () => {
    it('should have default configuration', () => {
      expect(bot.config.stalePR.enabled).toBe(true);
      expect(bot.config.stalePR.staleDays).toBe(15);
      expect(bot.config.stagingBranch.baseBranch).toBe('main');
    });

    it('should allow custom configuration', () => {
      const customBot = new AdvisoryBotEngine({
        stalePR: { enabled: false, staleDays: 30, closeDays: 30, staleLabel: 'Custom', exemptLabels: [], staleMessage: '', closeMessage: '' },
      });
      expect(customBot.config.stalePR.enabled).toBe(false);
      expect(customBot.config.stalePR.staleDays).toBe(30);
    });
  });

  describe('generateStagingBranchName', () => {
    it('should generate correct branch name', () => {
      const pr: PullRequestInfo = {
        number: 123,
        author: 'testuser',
        title: 'Fix vulnerability',
        baseBranch: 'main',
        headBranch: 'testuser/fix-vuln',
        files: ['advisories/GHSA-xxxx.json'],
        labels: [],
        createdAt: new Date(),
        updatedAt: new Date(),
        state: 'open',
      };

      const branchName = bot.generateStagingBranchName(pr);
      expect(branchName).toBe('testuser/advisory-improvement-123');
    });
  });

  describe('shouldCreateStagingBranch', () => {
    it('should return true for PRs with advisory changes to main', () => {
      const pr: PullRequestInfo = {
        number: 1,
        author: 'user',
        title: 'Update advisory',
        baseBranch: 'main',
        headBranch: 'user/update',
        files: ['advisories/GHSA-xxxx.json'],
        labels: [],
        createdAt: new Date(),
        updatedAt: new Date(),
        state: 'open',
      };

      expect(bot.shouldCreateStagingBranch(pr)).toBe(true);
    });

    it('should return false for non-main base branch', () => {
      const pr: PullRequestInfo = {
        number: 1,
        author: 'user',
        title: 'Update',
        baseBranch: 'develop',
        headBranch: 'user/update',
        files: ['advisories/GHSA-xxxx.json'],
        labels: [],
        createdAt: new Date(),
        updatedAt: new Date(),
        state: 'open',
      };

      expect(bot.shouldCreateStagingBranch(pr)).toBe(false);
    });

    it('should return false for non-advisory changes', () => {
      const pr: PullRequestInfo = {
        number: 1,
        author: 'user',
        title: 'Update docs',
        baseBranch: 'main',
        headBranch: 'user/docs',
        files: ['docs/README.md'],
        labels: [],
        createdAt: new Date(),
        updatedAt: new Date(),
        state: 'open',
      };

      expect(bot.shouldCreateStagingBranch(pr)).toBe(false);
    });
  });

  describe('checkStaleStatus', () => {
    it('should detect stale PRs', () => {
      const pr: PullRequestInfo = {
        number: 1,
        author: 'user',
        title: 'Old PR',
        baseBranch: 'main',
        headBranch: 'user/old',
        files: [],
        labels: [],
        createdAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000), // 20 days ago
        updatedAt: new Date(Date.now() - 20 * 24 * 60 * 60 * 1000),
        state: 'open',
      };

      const status = bot.checkStaleStatus(pr);
      expect(status.isStale).toBe(true);
      expect(status.daysSinceActivity).toBeGreaterThanOrEqual(20);
    });

    it('should detect PRs that should be closed', () => {
      const pr: PullRequestInfo = {
        number: 1,
        author: 'user',
        title: 'Very old PR',
        baseBranch: 'main',
        headBranch: 'user/very-old',
        files: [],
        labels: [],
        createdAt: new Date(Date.now() - 35 * 24 * 60 * 60 * 1000), // 35 days ago
        updatedAt: new Date(Date.now() - 35 * 24 * 60 * 60 * 1000),
        state: 'open',
      };

      const status = bot.checkStaleStatus(pr);
      expect(status.shouldClose).toBe(true);
    });

    it('should exempt PRs with Keep label', () => {
      const pr: PullRequestInfo = {
        number: 1,
        author: 'user',
        title: 'Important PR',
        baseBranch: 'main',
        headBranch: 'user/important',
        files: [],
        labels: ['Keep'],
        createdAt: new Date(Date.now() - 100 * 24 * 60 * 60 * 1000),
        updatedAt: new Date(Date.now() - 100 * 24 * 60 * 60 * 1000),
        state: 'open',
      };

      const status = bot.checkStaleStatus(pr);
      expect(status.isStale).toBe(false);
      expect(status.exemptReason).toContain('Keep');
    });
  });

  describe('isEcosystemSupported', () => {
    it('should return true for supported ecosystems', () => {
      expect(bot.isEcosystemSupported('npm')).toBe(true);
      expect(bot.isEcosystemSupported('pip')).toBe(true);
      expect(bot.isEcosystemSupported('maven')).toBe(true);
    });

    it('should return true for actions ecosystem', () => {
      expect(bot.isEcosystemSupported('actions')).toBe(true);
    });
  });

  describe('workflow generation', () => {
    it('should generate stale PR workflow', () => {
      const workflow = bot.generateStalePRWorkflow();
      expect(workflow).toContain('name: Close stale PRs');
      expect(workflow).toContain('actions/stale@v9.0.0');
      expect(workflow).toContain('days-before-pr-stale: 15');
    });

    it('should generate staging branch workflow', () => {
      const workflow = bot.generateStagingBranchWorkflow();
      expect(workflow).toContain('name: Create PR staging branch');
      expect(workflow).toContain('pull_request_target');
      expect(workflow).toContain('advisories/**');
    });

    it('should generate cleanup workflow', () => {
      const workflow = bot.generateCleanupWorkflow();
      expect(workflow).toContain('name: Delete PR staging and head branches');
      expect(workflow).toContain('advisory-improvement');
    });
  });
});

// ============================================================================
// InMemoryStorageAdapter Tests
// ============================================================================

describe('InMemoryStorageAdapter', () => {
  let storage: InMemoryStorageAdapter;

  const createTestAdvisory = (id: string): Advisory => ({
    schema_version: '1.6.0',
    id,
    modified: new Date().toISOString(),
    summary: `Test advisory ${id}`,
    affected: [{
      package: { name: 'test', ecosystem: 'npm' },
    }],
  });

  beforeEach(() => {
    storage = new InMemoryStorageAdapter();
  });

  it('should store and retrieve advisories', async () => {
    const advisory = createTestAdvisory('GHSA-c3gv-9cxf-6f57');
    await storage.create(advisory);
    const retrieved = await storage.get('GHSA-c3gv-9cxf-6f57');
    expect(retrieved).toEqual(advisory);
  });

  it('should return null for non-existent advisory', async () => {
    const result = await storage.get('GHSA-xxxx-xxxx-xxxx');
    expect(result).toBeNull();
  });

  it('should delete advisories', async () => {
    const advisory = createTestAdvisory('GHSA-c3gv-9cxf-6f57');
    await storage.create(advisory);
    const deleted = await storage.delete('GHSA-c3gv-9cxf-6f57');
    expect(deleted).toBe(true);
    expect(await storage.exists('GHSA-c3gv-9cxf-6f57')).toBe(false);
  });

  it('should check existence', async () => {
    const advisory = createTestAdvisory('GHSA-c3gv-9cxf-6f57');
    expect(await storage.exists('GHSA-c3gv-9cxf-6f57')).toBe(false);
    await storage.create(advisory);
    expect(await storage.exists('GHSA-c3gv-9cxf-6f57')).toBe(true);
  });

  it('should list with pagination', async () => {
    // Create 25 unique advisories with proper GHSA IDs
    for (let i = 0; i < 25; i++) {
      // Generate unique valid GHSA IDs using the generateGHSAId function
      const id = generateGHSAId();
      await storage.create(createTestAdvisory(id));
    }

    const page1 = await storage.list({ limit: 10, offset: 0 });
    expect(page1.advisories).toHaveLength(10);
    expect(page1.total).toBe(25);

    const page2 = await storage.list({ limit: 10, offset: 10 });
    expect(page2.advisories).toHaveLength(10);
  });

  it('should clear all data', () => {
    storage.clear();
    expect(storage.size).toBe(0);
  });
});
