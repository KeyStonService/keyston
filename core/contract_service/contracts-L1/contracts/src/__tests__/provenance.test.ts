import { ProvenanceService } from '../services/provenance';
import { writeFile, unlink } from 'fs/promises';
import { join } from 'path';
import { tmpdir } from 'os';

describe('ProvenanceService', () => {
  let service: ProvenanceService;
  let testFilePath: string;

  beforeEach(async () => {
    service = new ProvenanceService();
    testFilePath = join(tmpdir(), `test-${Date.now()}.txt`);
    await writeFile(testFilePath, 'test content for attestation');
  });

  afterEach(async () => {
    try {
      await unlink(testFilePath);
    } catch {
      // Ignore cleanup errors
    }
  });

  describe('generateFileDigest', () => {
    it('should generate correct SHA256 digest', async () => {
      const digest = await service.generateFileDigest(testFilePath);
      expect(digest).toMatch(/^sha256:[a-f0-9]{64}$/);
    });

    it('should throw error for non-existent file', async () => {
      await expect(service.generateFileDigest('/non/existent/file'))
        .rejects.toThrow(/ENOENT/);
    });
  });

  describe('createBuildAttestation', () => {
    it('should create valid attestation with required fields', async () => {
      const builder = {
        id: 'https://test.builder.com',
        version: '1.0.0'
      };

      const attestation = await service.createBuildAttestation(testFilePath, builder);

      expect(attestation).toMatchObject({
        id: expect.stringMatching(/^att_\d+_[a-z0-9]+$/),
        timestamp: expect.any(String),
        subject: {
          name: expect.stringContaining('test-'),
          digest: expect.stringMatching(/^sha256:[a-f0-9]{64}$/),
          path: testFilePath
        },
        predicate: {
          type: 'https://slsa.dev/provenance/v1',
          builder,
          recipe: expect.objectContaining({
            type: 'https://github.com/synergymesh/build'
          }),
          metadata: expect.objectContaining({
            completeness: {
              parameters: true,
              environment: true,
              materials: true
            }
          })
        }
      });
    });

    it('should include custom metadata when provided', async () => {
      const builder = { id: 'test-builder', version: '1.0.0' };
      const metadata = {
        reproducible: true,
        buildInvocationId: 'test-build-123'
      };

      const attestation = await service.createBuildAttestation(testFilePath, builder, metadata);

      expect(attestation.predicate.metadata.reproducible).toBe(true);
      expect(attestation.predicate.metadata.buildInvocationId).toBe('test-build-123');
    });

    it('should reject directories', async () => {
      await expect(service.createBuildAttestation(tmpdir(), {
        id: 'test-builder',
        version: '1.0.0'
      })).rejects.toThrow('Subject path must be a file');
    });
  });

  describe('verifyAttestation', () => {
    it('should verify valid attestation', async () => {
      const builder = { id: 'test-builder', version: '1.0.0' };
      const attestation = await service.createBuildAttestation(testFilePath, builder);

      const isValid = await service.verifyAttestation(attestation);
      expect(isValid).toBe(true);
    });

    it('should reject attestation with invalid structure', async () => {
      const invalidAttestation = {
        id: 'test',
        // Missing required fields
      } as unknown as Attestation;

      const isValid = await service.verifyAttestation(invalidAttestation);
      expect(isValid).toBe(false);
    });

    it('should verify attestation without file path', async () => {
      const attestation = {
        id: 'test-123',
        timestamp: new Date().toISOString(),
        subject: {
          name: 'test-artifact',
          digest: 'sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
        },
        predicate: {
          type: 'https://slsa.dev/provenance/v1',
          builder: { id: 'test', version: '1.0.0' },
          recipe: { type: 'test' },
          metadata: {
            buildStartedOn: new Date().toISOString(),
            buildFinishedOn: new Date().toISOString(),
            completeness: { parameters: true, environment: true, materials: true },
            reproducible: false
          }
        }
      };

      const isValid = await service.verifyAttestation(attestation);
      expect(isValid).toBe(true);
    });
  });

  describe('exportAttestation', () => {
    it('should export attestation as formatted JSON', async () => {
      const builder = { id: 'test-builder', version: '1.0.0' };
      const attestation = await service.createBuildAttestation(testFilePath, builder);

      const exported = service.exportAttestation(attestation);
      const parsed = JSON.parse(exported);

      expect(parsed).toEqual(attestation);
      expect(exported).toContain('\n'); // Check formatting
    });
  });

  describe('importAttestation', () => {
    it('should import valid attestation JSON', async () => {
      const builder = { id: 'test-builder', version: '1.0.0' };
      const originalAttestation = await service.createBuildAttestation(testFilePath, builder);
      const exported = service.exportAttestation(originalAttestation);

      const imported = service.importAttestation(exported);
      expect(imported).toEqual(originalAttestation);
    });

    it('should reject invalid JSON', () => {
      expect(() => service.importAttestation('invalid json'))
        .toThrow();
    });

    it('should reject JSON without required fields', () => {
      const invalidJson = JSON.stringify({ invalid: 'data' });
      expect(() => service.importAttestation(invalidJson))
        .toThrow('Invalid attestation format');
    });
  });
});