/**
 * Auto-Assignment System Tests
 */

import request from 'supertest';
import express, { Application } from 'express';
import helmet from 'helmet';
import cors from 'cors';
import routes from '../routes';

describe('Auto-Assignment System', () => {
  let app: Application;

  beforeAll(() => {
    app = express();
    app.use(helmet());
    app.use(cors());
    app.use(express.json());
    app.use('/', routes);
  });

  describe('POST /api/v1/assignment/assign', () => {
    it('should create assignment for BACKEND_API incident', async () => {
      const incident = {
        type: 'BACKEND_API',
        priority: 'HIGH',
        description: 'API endpoint returning 500 errors',
        errorMessage: 'Internal Server Error in /api/users',
        affectedFiles: ['src/api/users.ts'],
      };

      const response = await request(app).post('/api/v1/assignment/assign').send(incident);

      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data.assignment).toBeDefined();
      expect(response.body.data.assignment.primaryOwner).toBeDefined();
      expect(response.body.data.assignment.status).toBe('ASSIGNED');
      expect(response.body.data.assignment.slaTarget).toBeDefined();
      expect(response.body.data.assignment.slaTarget.responseTime).toBe(15);
      expect(response.body.data.assignment.slaTarget.resolutionTime).toBe(240);
    });

    it('should create assignment for CRITICAL priority incident', async () => {
      const incident = {
        type: 'SECURITY',
        priority: 'CRITICAL',
        description: 'Security breach detected',
        errorMessage: 'Unauthorized access attempt',
      };

      const response = await request(app).post('/api/v1/assignment/assign').send(incident);

      expect(response.status).toBe(201);
      expect(response.body.success).toBe(true);
      expect(response.body.data.assignment.slaTarget.responseTime).toBe(5);
      expect(response.body.data.assignment.slaTarget.resolutionTime).toBe(60);
    });

    it('should assign to appropriate team based on problem type', async () => {
      const incident = {
        type: 'FRONTEND_ERROR',
        priority: 'MEDIUM',
        description: 'React component rendering issue',
        affectedFiles: ['src/components/UserProfile.tsx'],
      };

      const response = await request(app).post('/api/v1/assignment/assign').send(incident);

      expect(response.status).toBe(201);
      expect(response.body.data.assignment.primaryOwner.specialties).toContain('react');
    });

    it('should include secondary owner when available', async () => {
      const incident = {
        type: 'DATABASE_ISSUE',
        priority: 'HIGH',
        description: 'Database connection timeout',
        errorMessage: 'Connection pool exhausted',
      };

      const response = await request(app).post('/api/v1/assignment/assign').send(incident);

      expect(response.status).toBe(201);
      expect(response.body.data.assignment.secondaryOwner).toBeDefined();
    });

    it('should return 400 for invalid problem type', async () => {
      const incident = {
        type: 'INVALID_TYPE',
        priority: 'HIGH',
        description: 'Test incident',
      };

      const response = await request(app).post('/api/v1/assignment/assign').send(incident);

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
      expect(response.body.error).toBe('Validation error');
    });

    it('should return 400 for missing required fields', async () => {
      const response = await request(app).post('/api/v1/assignment/assign').send({
        type: 'BACKEND_API',
        // missing priority and description
      });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/v1/assignment/status/:id', () => {
    it('should get assignment status', async () => {
      // First create an assignment
      const incident = {
        type: 'PERFORMANCE',
        priority: 'MEDIUM',
        description: 'Slow API response times',
      };

      const createResponse = await request(app).post('/api/v1/assignment/assign').send(incident);

      const assignmentId = createResponse.body.data.assignment.id;

      // Then get its status
      const response = await request(app).get(`/api/v1/assignment/status/${assignmentId}`);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.id).toBe(assignmentId);
      expect(response.body.data.status).toBe('ASSIGNED');
    });

    it('should return 404 for non-existent assignment', async () => {
      const response = await request(app).get('/api/v1/assignment/status/non-existent-id');

      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/v1/assignment/status/:id', () => {
    it('should update assignment status to ACKNOWLEDGED', async () => {
      // Create assignment
      const incident = {
        type: 'INFRASTRUCTURE',
        priority: 'LOW',
        description: 'Server disk space warning',
      };

      const createResponse = await request(app).post('/api/v1/assignment/assign').send(incident);

      const assignmentId = createResponse.body.data.assignment.id;

      // Update status
      const response = await request(app)
        .post(`/api/v1/assignment/status/${assignmentId}`)
        .send({ status: 'ACKNOWLEDGED' });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.status).toBe('ACKNOWLEDGED');
      expect(response.body.data.acknowledgedAt).toBeDefined();
    });

    it('should update assignment status to IN_PROGRESS', async () => {
      const incident = {
        type: 'BACKEND_API',
        priority: 'HIGH',
        description: 'API endpoint not responding',
      };

      const createResponse = await request(app).post('/api/v1/assignment/assign').send(incident);

      const assignmentId = createResponse.body.data.assignment.id;

      const response = await request(app)
        .post(`/api/v1/assignment/status/${assignmentId}`)
        .send({ status: 'IN_PROGRESS' });

      expect(response.status).toBe(200);
      expect(response.body.data.status).toBe('IN_PROGRESS');
      expect(response.body.data.startedAt).toBeDefined();
    });

    it('should update assignment status to RESOLVED', async () => {
      const incident = {
        type: 'FRONTEND_ERROR',
        priority: 'MEDIUM',
        description: 'Button click not working',
      };

      const createResponse = await request(app).post('/api/v1/assignment/assign').send(incident);

      const assignmentId = createResponse.body.data.assignment.id;

      const response = await request(app)
        .post(`/api/v1/assignment/status/${assignmentId}`)
        .send({ status: 'RESOLVED' });

      expect(response.status).toBe(200);
      expect(response.body.data.status).toBe('RESOLVED');
      expect(response.body.data.resolvedAt).toBeDefined();
    });

    it('should return 400 for invalid status', async () => {
      const incident = {
        type: 'BACKEND_API',
        priority: 'HIGH',
        description: 'Test incident',
      };

      const createResponse = await request(app).post('/api/v1/assignment/assign').send(incident);

      const assignmentId = createResponse.body.data.assignment.id;

      const response = await request(app)
        .post(`/api/v1/assignment/status/${assignmentId}`)
        .send({ status: 'INVALID_STATUS' });

      expect(response.status).toBe(400);
      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/v1/assignment/workload', () => {
    it('should return workload statistics', async () => {
      const response = await request(app).get('/api/v1/assignment/workload');

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data)).toBe(true);
    });
  });

  describe('POST /api/v1/assignment/reassign/:id', () => {
    it('should reassign to different team member', async () => {
      // Create assignment
      const incident = {
        type: 'BACKEND_API',
        priority: 'MEDIUM',
        description: 'API performance issue',
      };

      const createResponse = await request(app).post('/api/v1/assignment/assign').send(incident);

      const assignmentId = createResponse.body.data.assignment.id;
      const originalOwnerId = createResponse.body.data.assignment.primaryOwner.id;

      // Reassign to eva.wu
      const response = await request(app)
        .post(`/api/v1/assignment/reassign/${assignmentId}`)
        .send({ newOwnerId: 'eva.wu' });

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.primaryOwner.id).toBe('eva.wu');
      expect(response.body.data.primaryOwner.id).not.toBe(originalOwnerId);
      expect(response.body.data.status).toBe('ASSIGNED');
    });

    it('should return 404 for invalid member ID', async () => {
      const incident = {
        type: 'BACKEND_API',
        priority: 'MEDIUM',
        description: 'Test incident',
      };

      const createResponse = await request(app).post('/api/v1/assignment/assign').send(incident);

      const assignmentId = createResponse.body.data.assignment.id;

      const response = await request(app)
        .post(`/api/v1/assignment/reassign/${assignmentId}`)
        .send({ newOwnerId: 'non-existent-member' });

      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
    });
  });

  describe('POST /api/v1/assignment/escalate/:id', () => {
    it('should escalate assignment', async () => {
      const incident = {
        type: 'SECURITY',
        priority: 'HIGH',
        description: 'Potential security vulnerability',
      };

      const createResponse = await request(app).post('/api/v1/assignment/assign').send(incident);

      const assignmentId = createResponse.body.data.assignment.id;

      const response = await request(app).post(`/api/v1/assignment/escalate/${assignmentId}`);

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.status).toBe('ESCALATED');
      expect(response.body.message).toContain('escalated successfully');
    });

    it('should return 404 for non-existent assignment', async () => {
      const response = await request(app).post('/api/v1/assignment/escalate/non-existent-id');

      expect(response.status).toBe(404);
      expect(response.body.success).toBe(false);
    });
  });

  describe('GET /api/v1/assignment/all', () => {
    it('should return all assignments', async () => {
      const response = await request(app).get('/api/v1/assignment/all');

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(Array.isArray(response.body.data)).toBe(true);
      expect(response.body.count).toBeDefined();
      expect(response.body.count).toBeGreaterThan(0);
    });
  });

  describe('GET /api/v1/assignment/report', () => {
    it('should return performance report', async () => {
      const response = await request(app).get('/api/v1/assignment/report');

      expect(response.status).toBe(200);
      expect(response.body.success).toBe(true);
      expect(response.body.data.totalAssignments).toBeDefined();
      expect(response.body.data.resolved).toBeDefined();
      expect(response.body.data.averageResponseTime).toBeDefined();
      expect(response.body.data.averageResolutionTime).toBeDefined();
      expect(response.body.data.slaCompliance).toBeDefined();
    });
  });

  describe('Integration Tests', () => {
    it('should handle complete assignment lifecycle', async () => {
      // 1. Create assignment
      const incident = {
        type: 'BACKEND_API',
        priority: 'HIGH',
        description: 'Complete lifecycle test',
        errorMessage: 'Test error',
      };

      const createResponse = await request(app).post('/api/v1/assignment/assign').send(incident);

      expect(createResponse.status).toBe(201);
      const assignmentId = createResponse.body.data.assignment.id;

      // 2. Acknowledge
      const acknowledgeResponse = await request(app)
        .post(`/api/v1/assignment/status/${assignmentId}`)
        .send({ status: 'ACKNOWLEDGED' });

      expect(acknowledgeResponse.status).toBe(200);
      expect(acknowledgeResponse.body.data.status).toBe('ACKNOWLEDGED');

      // 3. Start progress
      const progressResponse = await request(app)
        .post(`/api/v1/assignment/status/${assignmentId}`)
        .send({ status: 'IN_PROGRESS' });

      expect(progressResponse.status).toBe(200);
      expect(progressResponse.body.data.status).toBe('IN_PROGRESS');

      // 4. Resolve
      const resolveResponse = await request(app)
        .post(`/api/v1/assignment/status/${assignmentId}`)
        .send({ status: 'RESOLVED' });

      expect(resolveResponse.status).toBe(200);
      expect(resolveResponse.body.data.status).toBe('RESOLVED');

      // 5. Verify final state
      const finalResponse = await request(app).get(`/api/v1/assignment/status/${assignmentId}`);

      expect(finalResponse.status).toBe(200);
      expect(finalResponse.body.data.acknowledgedAt).toBeDefined();
      expect(finalResponse.body.data.startedAt).toBeDefined();
      expect(finalResponse.body.data.resolvedAt).toBeDefined();
    });

    it('should handle multiple concurrent assignments', async () => {
      const incidents = [
        { type: 'FRONTEND_ERROR', priority: 'HIGH', description: 'Issue 1' },
        { type: 'BACKEND_API', priority: 'MEDIUM', description: 'Issue 2' },
        { type: 'DATABASE_ISSUE', priority: 'LOW', description: 'Issue 3' },
      ];

      const responses = await Promise.all(
        incidents.map((incident) => request(app).post('/api/v1/assignment/assign').send(incident))
      );

      responses.forEach((response) => {
        expect(response.status).toBe(201);
        expect(response.body.success).toBe(true);
      });

      // Verify all assignments exist
      const allResponse = await request(app).get('/api/v1/assignment/all');

      expect(allResponse.body.count).toBeGreaterThanOrEqual(3);
    });
  });
});
