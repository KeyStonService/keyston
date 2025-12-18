import request from 'supertest';
import express from 'express';
import routes from '../routes';
import { loggingMiddleware } from '../middleware/logging';
import { errorMiddleware } from '../middleware/error';
import { writeFile, unlink, mkdir } from 'fs/promises';
import { join, resolve } from 'path';

// 創建測試用的獨立應用
const createTestApp = () => {
  const app = express();
  app.use(express.json());
  app.use(loggingMiddleware);
  app.use(routes);
  app.use(errorMiddleware);
  return app;
};

describe('Provenance API Endpoints', () => {
  let testFilePath: string;
  let app: express.Application;
  const SAFE_ROOT = resolve(process.cwd(), 'safefiles');

  beforeEach(async () => {
    app = createTestApp();
    // Ensure safe directory exists
    await mkdir(SAFE_ROOT, { recursive: true });
    testFilePath = `test-api-${Date.now()}.txt`;
    await writeFile(join(SAFE_ROOT, testFilePath), 'test content for API testing');
  });

  afterEach(async () => {
    try {
      await unlink(join(SAFE_ROOT, testFilePath));
    } catch {
      // Ignore cleanup errors
    }
  });

  describe('POST /api/v1/provenance/attestations', () => {
    it('should create attestation for valid file', async () => {
      const response = await request(app)
        .post('/api/v1/provenance/attestations')
        .send({
          filePath: testFilePath,
          builder: {
            id: 'https://github.com/synergymesh/builder',
            version: '1.0.0',
          },
        });

      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data).toMatchObject({
        id: expect.stringMatching(/^att_\d+_[a-z0-9]+$/),
        subject: {
          name: expect.stringContaining('test-api-'),
          digest: expect.stringMatching(/^sha256:[a-f0-9]{64}$/),
          path: testFilePath,
        },
        predicate: {
          type: 'https://slsa.dev/provenance/v1',
          builder: {
            id: 'https://github.com/synergymesh/builder',
            version: '1.0.0',
          },
        },
      });
    });

    it('should return 400 for missing filePath', async () => {
      const response = await request(app)
        .post('/api/v1/provenance/attestations')
        .send({
          builder: {
            id: 'test-builder',
            version: '1.0.0',
          },
        });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('filePath');
    });

    it('should return 400 for missing builder', async () => {
      const app = createTestApp();
      const response = await request(app).post('/api/v1/provenance/attestations').send({
        filePath: testFilePath,
      });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('builder');
    });

    it('should return 404 for non-existent file', async () => {
      const response = await request(app)
        .post('/api/v1/provenance/attestations')
        .send({
          filePath: '/non/existent/file.txt',
          builder: {
            id: 'test-builder',
            version: '1.0.0',
          },
        });

      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/v1/provenance/verify', () => {
    it('should verify valid attestation', async () => {
      // First create an attestation
      const createResponse = await request(app)
        .post('/api/v1/provenance/attestations')
        .send({
          filePath: testFilePath,
          builder: {
            id: 'test-builder',
            version: '1.0.0',
          },
        });

      const attestation = createResponse.body.data;

      // Then verify it
      const verifyResponse = await request(app)
        .post('/api/v1/provenance/verify')
        .send({ attestation });

      expect(verifyResponse.status).toBe(200);
      expect(verifyResponse.body.success).toBe(true);
      expect(verifyResponse.body.data.valid).toBe(true);
    });

    it('should reject invalid attestation', async () => {
      const response = await request(app)
        .post('/api/v1/provenance/verify')
        .send({
          attestation: {
            id: 'invalid',
            invalid: 'structure',
          },
        });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.valid).toBe(false);
    });

    it('should return 400 for missing attestation', async () => {
      const response = await request(app).post('/api/v1/provenance/verify').send({});

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('attestation');
    });
  });

  describe('POST /api/v1/provenance/digest', () => {
    it('should calculate file digest', async () => {
      // Encode file path for URL
      const encodedPath = encodeURIComponent(testFilePath);
      const response = await request(app).get(`/api/v1/provenance/digest/${encodedPath}`);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.digest).toMatch(/^sha256:[a-f0-9]{64}$/);
      expect(response.body.data.filePath).toBe(testFilePath);
    });

    it('should return 400 for missing filePath', async () => {
      const response = await request(app).get('/api/v1/provenance/digest/');

      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('filePath');
    });

    it('should return 404 for non-existent file', async () => {
      const encodedPath = encodeURIComponent('/non/existent/file.txt');
      const response = await request(app).get(`/api/v1/provenance/digest/${encodedPath}`);

      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/v1/provenance/import', () => {
    it('should import valid attestation JSON', async () => {
      // First create an attestation
      const createResponse = await request(app)
        .post('/api/v1/provenance/attestations')
        .send({
          filePath: testFilePath,
          builder: {
            id: 'test-builder',
            version: '1.0.0',
          },
        });

      const attestation = createResponse.body.data;
      const exportedJson = JSON.stringify(attestation, null, 2);

      // Import it
      const importResponse = await request(app).post('/api/v1/provenance/import').send({
        attestationJson: exportedJson,
      });

      expect(importResponse.status).toBe(200);
      expect(importResponse.body.success).toBe(true);
      expect(importResponse.body.data).toEqual(attestation);
    });

    it('should return 400 for invalid JSON', async () => {
      const response = await request(app).post('/api/v1/provenance/import').send({
        attestationJson: 'invalid json',
      });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });

    it('should return 400 for missing attestationJson', async () => {
      const response = await request(app).post('/api/v1/provenance/import').send({});

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toContain('attestationJson');
    });
  });

  describe('GET /api/v1/provenance/export/:id', () => {
    it('should return formatted message for any ID', async () => {
      const response = await request(app).get('/api/v1/provenance/export/test-123');

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.message).toContain('test-123');
      expect(response.body.data.format).toBe('json');
    });
  });
});
