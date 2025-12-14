import request from 'supertest';
import express from 'express';
import routes from '../routes';
import { loggingMiddleware } from '../middleware/logging';
import { errorMiddleware } from '../middleware/error';
import { writeFile, unlink } from 'fs/promises';
import { join } from 'path';
import { tmpdir } from 'os';

// Create standalone test application
const createTestApp = () => {
  const app = express();
  app.use(express.json());
  app.use(loggingMiddleware);
  app.use(routes);
  app.use(errorMiddleware);
  return app;
};

describe('SLSA API Endpoints', () => {
  let testFilePath: string;
  let app: express.Application;

  beforeEach(async () => {
    app = createTestApp();
    testFilePath = join(tmpdir(), `test-slsa-${Date.now()}.txt`);
    await writeFile(testFilePath, 'test content for SLSA testing');
  });

  afterEach(async () => {
    try {
      await unlink(testFilePath);
    } catch {
      // Ignore cleanup errors
    }
  });

  describe('POST /api/v1/slsa/attestations', () => {
    it('should create SLSA attestation for valid file path', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/attestations')
        .send({
          subjectPath: testFilePath,
          builder: {
            id: 'https://github.com/synergymesh/builder',
            version: '1.0.0'
          }
        });

      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toMatchObject({
        provenance: expect.any(Object),
        attestationId: expect.any(String),
        subjects: 1,
        buildType: expect.any(String)
      });
      expect(response.body.message).toContain('successfully');
    });

    it('should create SLSA attestation from digest and name', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/attestations')
        .send({
          subjectDigest: 'sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
          subjectName: 'test-artifact.tar.gz',
          builder: {
            id: 'https://github.com/synergymesh/builder',
            version: '2.0.0'
          }
        });

      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data.subjects).toBe(1);
    });

    it('should return 400 for missing required fields', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/attestations')
        .send({
          builder: {
            id: 'test-builder',
            version: '1.0.0'
          }
        });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBeDefined();
    });

    it('should return 400 for missing builder', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/attestations')
        .send({
          subjectPath: testFilePath
        });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/v1/slsa/verify', () => {
    it('should verify valid SLSA provenance', async () => {
      // First create a provenance
      const createResponse = await request(app)
        .post('/api/v1/slsa/attestations')
        .send({
          subjectPath: testFilePath,
          builder: {
            id: 'test-builder',
            version: '1.0.0'
          }
        });

      const { provenance } = createResponse.body.data;

      // Then verify it
      const verifyResponse = await request(app)
        .post('/api/v1/slsa/verify')
        .send({ provenance });

      expect(verifyResponse.status).toBe(200);
      expect(verifyResponse.body.success).toBe(true);
      expect(verifyResponse.body.data).toMatchObject({
        valid: expect.any(Boolean),
        timestamp: expect.any(String),
        provenanceType: expect.any(String)
      });
    });

    it('should handle invalid provenance structure', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/verify')
        .send({
          provenance: {
            invalid: 'structure'
          }
        });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.valid).toBe(false);
    });

    it('should return 400 for missing provenance', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/verify')
        .send({});

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/v1/slsa/digest', () => {
    it('should generate digest for content', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/digest')
        .send({
          content: 'Hello, World!'
        });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toMatchObject({
        subject: 'user-content',
        digest: expect.any(Object),
        sha256: expect.stringMatching(/^[a-f0-9]{64}$/),
        algorithm: 'sha256',
        timestamp: expect.any(String)
      });
    });

    it('should return consistent digest for same content', async () => {
      const content = 'Consistent test content';

      const response1 = await request(app)
        .post('/api/v1/slsa/digest')
        .send({ content });

      const response2 = await request(app)
        .post('/api/v1/slsa/digest')
        .send({ content });

      expect(response1.body.data.sha256).toBe(response2.body.data.sha256);
    });

    it('should return 400 for missing content', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/digest')
        .send({});

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/v1/slsa/contracts', () => {
    it('should create contract attestation', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/contracts')
        .send({
          contractName: 'TestContract',
          contractVersion: '1.0.0',
          deployerAddress: '0x1234567890abcdef',
          contractCode: 'contract TestContract { function test() public pure returns (bool) { return true; } }',
          deploymentTxHash: '0xabcdef1234567890'
        });

      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toMatchObject({
        provenance: expect.any(Object),
        contractAttestation: {
          contractName: 'TestContract',
          contractVersion: '1.0.0',
          deployerAddress: '0x1234567890abcdef',
          deploymentTxHash: '0xabcdef1234567890',
          codeHash: expect.stringMatching(/^[a-f0-9]{64}$/),
          attestationId: expect.any(String)
        }
      });
    });

    it('should create contract attestation with minimal fields', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/contracts')
        .send({
          contractName: 'MinimalContract',
          contractCode: 'contract Minimal {}'
        });

      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data.contractAttestation.contractName).toBe('MinimalContract');
    });

    it('should return 400 for missing contract name', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/contracts')
        .send({
          contractCode: 'contract Test {}'
        });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });

    it('should return 400 for missing contract code', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/contracts')
        .send({
          contractName: 'TestContract'
        });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/v1/slsa/summary', () => {
    it('should return summary for valid provenance', async () => {
      // First create a provenance
      const createResponse = await request(app)
        .post('/api/v1/slsa/attestations')
        .send({
          subjectPath: testFilePath,
          builder: {
            id: 'test-builder',
            version: '1.0.0'
          }
        });

      const { provenance } = createResponse.body.data;

      // Get summary
      const summaryResponse = await request(app)
        .post('/api/v1/slsa/summary')
        .send({ provenance });

      expect(summaryResponse.status).toBe(200);
      expect(summaryResponse.body.success).toBe(true);
      expect(summaryResponse.body.data).toMatchObject({
        valid: expect.any(Boolean),
        type: expect.any(String),
        subjects: expect.any(Number),
        subjectNames: expect.any(Array),
        buildType: expect.any(String),
        builder: expect.any(String),
        timestamp: expect.any(String),
        invocationId: expect.any(String)
      });
    });

    it('should return 400 for missing provenance', async () => {
      const response = await request(app)
        .post('/api/v1/slsa/summary')
        .send({});

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });
});

describe('Health Check Endpoints', () => {
  let app: express.Application;

  beforeEach(() => {
    app = createTestApp();
  });

  describe('GET /healthz', () => {
    it('should return healthy status', async () => {
      const response = await request(app).get('/healthz');

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        status: 'healthy',
        timestamp: expect.any(String),
        service: 'contracts-l1'
      });
    });
  });

  describe('GET /readyz', () => {
    it('should return ready status', async () => {
      const response = await request(app).get('/readyz');

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        status: 'ready',
        timestamp: expect.any(String),
        checks: expect.any(Object)
      });
    });
  });

  describe('GET /version', () => {
    it('should return version info', async () => {
      const response = await request(app).get('/version');

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        version: expect.any(String),
        build: expect.any(String),
        timestamp: expect.any(String)
      });
    });
  });

  describe('GET /status', () => {
    it('should return status info', async () => {
      const response = await request(app).get('/status');

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        service: 'contracts-l1',
        status: 'running',
        uptime: expect.any(Number),
        memory: expect.any(Object),
        timestamp: expect.any(String)
      });
    });
  });

  describe('GET /', () => {
    it('should return service info with endpoints', async () => {
      const response = await request(app).get('/');

      expect(response.status).toBe(200);
      expect(response.body).toMatchObject({
        service: 'contracts-l1',
        version: '1.0.0',
        description: expect.any(String),
        endpoints: {
          health: '/healthz',
          ready: '/readyz',
          version: '/version',
          status: '/status',
          provenance: expect.any(Object),
          slsa: expect.any(Object),
          assignment: expect.any(Object),
          escalation: expect.any(Object)
        }
      });
    });
  });
});
