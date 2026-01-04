import request from 'supertest';
import { app } from '../src/index';

describe('My App API', () => {
  describe('GET /health', () => {
    it('should return healthy status', async () => {
      const response = await request(app).get('/health');
      expect(response.status).toBe(200);
      expect(response.body.status).toBe('healthy');
      expect(response.body).toHaveProperty('version');
      expect(response.body).toHaveProperty('timestamp');
    });
  });

  describe('GET /ready', () => {
    it('should return ready status with checks', async () => {
      const response = await request(app).get('/ready');
      expect(response.status).toBe(200);
      expect(response.body.status).toBe('ready');
      expect(response.body.checks).toHaveProperty('database');
      expect(response.body.checks).toHaveProperty('cache');
    });
  });

  describe('GET /metrics', () => {
    it('should return Prometheus metrics', async () => {
      const response = await request(app).get('/metrics');
      expect(response.status).toBe(200);
      expect(response.headers['content-type']).toContain('text/plain');
      expect(response.text).toContain('myapp_');
    });
  });

  describe('GET /api/v1/info', () => {
    it('should return application info', async () => {
      const response = await request(app).get('/api/v1/info');
      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('name');
      expect(response.body).toHaveProperty('version');
      expect(response.body).toHaveProperty('namingConvention');
      expect(response.body.namingConvention.compliant).toBe(true);
    });
  });
});

describe('Naming Convention', () => {
  const pattern = /^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\d+\.\d+\.\d+(-[A-Za-z0-9]+)?$/;

  it('should validate correct naming patterns', () => {
    const validNames = [
      'dev-my-app-deploy-v1.0.0',
      'staging-api-gateway-svc-v2.1.0',
      'prod-config-cm-v1.0.0-abc123',
      'dev-auth-secret-v1.2.3',
      'prod-web-ing-v3.0.0',
    ];

    validNames.forEach((name) => {
      expect(pattern.test(name)).toBe(true);
    });
  });

  it('should reject invalid naming patterns', () => {
    const invalidNames = [
      'myapp-deploy',
      'dev-MyApp-deploy-v1.0.0',
      'test-app-deploy-v1.0.0',
      'dev-app-deployment-v1.0.0',
      'dev-app-deploy-1.0.0',
    ];

    invalidNames.forEach((name) => {
      expect(pattern.test(name)).toBe(false);
    });
  });
});
