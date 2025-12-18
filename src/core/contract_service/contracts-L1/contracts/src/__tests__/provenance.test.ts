import { writeFile, unlink, mkdir, rmdir } from 'fs/promises';
import { join, relative } from 'path';
import { tmpdir } from 'os';

import { ProvenanceService, BuildAttestation } from '../services/provenance';

describe('ProvenanceService', () => {
  let service: ProvenanceService;
  let testFilePath: string;
  const SAFE_ROOT = tmpdir();
  let originalSafeRoot: string | undefined;

  beforeEach(async () => {
    originalSafeRoot = process.env.SAFE_ROOT_PATH;
    process.env.SAFE_ROOT_PATH = SAFE_ROOT;

    await mkdir(SAFE_ROOT, { recursive: true });
    service = new ProvenanceService();
    testFilePath = `test-${Date.now()}.txt`;
    await writeFile(join(SAFE_ROOT, testFilePath), 'test content for attestation');
  });

  afterEach(async () => {
    if (originalSafeRoot !== undefined) {
      process.env.SAFE_ROOT_PATH = originalSafeRoot;
    } else {
      delete process.env.SAFE_ROOT_PATH;
    }

    try {
      await unlink(join(SAFE_ROOT, testFilePath));
    } catch {
      // ignore cleanup errors
    }
  });

  describe('generateFileDigest', () => {
    it('should generate correct SHA256 digest', async () => {
      const digest = await service.generateFileDigest(testFilePath);
      expect(digest).toMatch(/^sha256:[a-f0-9]{64}$/);
    });

    it('should reject path traversal attempts', async () => {
      await expect(service.generateFileDigest('../../../etc/passwd')).rejects.toThrow();
    });
  });

  describe('createBuildAttestation', () => {
    it('should create valid attestation with required fields', async () => {
      const builder = { id: 'https://test.builder.com', version: '1.0.0' };
      const attestation = await service.createBuildAttestation(testFilePath, builder);

      expect(attestation).toMatchObject({
        id: expect.stringMatching(/^att_\d+_[a-z0-9]+$/),
        subject: {
          name: expect.stringContaining('test-'),
          digest: expect.stringMatching(/^sha256:[a-f0-9]{64}$/),
          path: testFilePath,
        },
        predicate: {
          type: 'https://slsa.dev/provenance/v1',
          builder,
        },
      });
    });

    it('should reject directories', async () => {
      const dirPath = join(SAFE_ROOT, `dir-${Date.now()}`);
      await mkdir(dirPath);

      const relativeDir = relative(SAFE_ROOT, dirPath);
      await expect(
        service.createBuildAttestation(relativeDir, { id: 'test-builder', version: '1.0.0' })
      ).rejects.toThrow('Subject path must be a file');

      await rmdir(dirPath);
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
      } as unknown as BuildAttestation;

      const isValid = await service.verifyAttestation(invalidAttestation);
      expect(isValid).toBe(false);
    });
  });

  describe('export/import', () => {
    it('should round trip attestation JSON', async () => {
      const builder = { id: 'test-builder', version: '1.0.0' };
      const attestation = await service.createBuildAttestation(testFilePath, builder);

      const exported = service.exportAttestation(attestation);
      const imported = service.importAttestation(exported);

      expect(exported).toContain(attestation.id);
      expect(imported.id).toBe(attestation.id);
      expect(imported.subject.digest).toBe(attestation.subject.digest);
      expect(imported.predicate.type).toBe(attestation.predicate.type);
    });
  });
});
