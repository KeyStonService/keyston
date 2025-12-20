import { Router, Request, Response } from 'express';
import type { Router as RouterType } from 'express';
// eslint-disable-next-line import/no-named-as-default
import rateLimit from 'express-rate-limit';

import { AssignmentController } from './controllers/assignment';
import { EscalationController } from './controllers/escalation';
import { ProvenanceController } from './controllers/provenance';
import { SLSAController } from './controllers/slsa';

const router: RouterType = Router();
const provenanceController = new ProvenanceController();
const slsaController = new SLSAController();
const assignmentController = new AssignmentController();
const escalationController = new EscalationController();
const windowMinutesEnv = process.env.SLSA_RATE_LIMIT_WINDOW_MINUTES;
const maxRequestsEnv = process.env.SLSA_RATE_LIMIT_MAX_REQUESTS;
const slsaRateLimitWindowMinutes = (() => {
  const parsed = windowMinutesEnv ? parseInt(windowMinutesEnv, 10) : NaN;
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 15;
})();
const slsaRateLimitMaxRequests = (() => {
  const parsed = maxRequestsEnv ? parseInt(maxRequestsEnv, 10) : NaN;
  return Number.isFinite(parsed) && parsed > 0 ? parsed : 10;
})();
const slsaRateLimiter = rateLimit({
  windowMs: slsaRateLimitWindowMinutes * 60 * 1000,
  max: slsaRateLimitMaxRequests,
  standardHeaders: true,
  legacyHeaders: false,
});

// 健康檢查端點
router.get('/healthz', (_req: Request, res: Response) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'contracts-l1',
  });
});

router.get('/readyz', (_req: Request, res: Response) => {
  res.status(200).json({
    status: 'ready',
    timestamp: new Date().toISOString(),
    checks: {},
  });
});

router.get('/version', (_req: Request, res: Response) => {
  res.json({
    version: process.env.npm_package_version || '1.0.0',
    build: process.env.BUILD_SHA || 'local',
    timestamp: new Date().toISOString(),
  });
});

router.get('/status', (_req: Request, res: Response) => {
  res.json({
    service: 'contracts-l1',
    status: 'running',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    timestamp: new Date().toISOString(),
  });
});

// 溯源認證端點
router.post('/api/v1/provenance/attestations', provenanceController.createAttestation);
router.post('/api/v1/provenance/attest', provenanceController.createAttestation); // Alias for tests
router.post('/api/v1/provenance/verify', provenanceController.verifyAttestation);
router.post('/api/v1/provenance/import', provenanceController.importAttestation);
router.post('/api/v1/provenance/digest', provenanceController.getFileDigest); // POST for tests
router.get('/api/v1/provenance/digest/:filePath(*)', provenanceController.getFileDigest);
router.get('/api/v1/provenance/export/:id', provenanceController.exportAttestation);

// SLSA 認證端點
router.post('/api/v1/slsa/attestations', slsaRateLimiter, slsaController.createAttestation);
router.post('/api/v1/slsa/verify', slsaRateLimiter, slsaController.verifyAttestation);
router.post('/api/v1/slsa/digest', slsaRateLimiter, slsaController.generateDigest);
router.post('/api/v1/slsa/contracts', slsaRateLimiter, slsaController.createContractAttestation);
router.post('/api/v1/slsa/summary', slsaRateLimiter, slsaController.getAttestationSummary);

// 自動分派端點 (Auto-Assignment Endpoints)
router.post('/api/v1/assignment/assign', assignmentController.assignResponsibility);
router.post('/api/v1/assignment/status/:id', assignmentController.updateStatus);
router.get('/api/v1/assignment/status/:id', assignmentController.getAssignmentStatus);
router.get('/api/v1/assignment/workload', assignmentController.getWorkload);
router.post('/api/v1/assignment/reassign/:id', assignmentController.reassign);
router.post('/api/v1/assignment/escalate/:id', assignmentController.escalate);
router.get('/api/v1/assignment/all', assignmentController.getAllAssignments);
router.get('/api/v1/assignment/report', assignmentController.getPerformanceReport);

// 進階升級端點 (Advanced Escalation Endpoints)
router.post(
  '/api/v1/escalation/create',
  escalationController.createEscalation.bind(escalationController)
);
router.get(
  '/api/v1/escalation/:escalationId',
  escalationController.getEscalation.bind(escalationController)
);
router.get(
  '/api/v1/escalation/incident/:incidentId',
  escalationController.getEscalationsByIncident.bind(escalationController)
);
router.post(
  '/api/v1/escalation/:escalationId/status',
  escalationController.updateEscalationStatus.bind(escalationController)
);
router.post(
  '/api/v1/escalation/:escalationId/resolve',
  escalationController.resolveEscalation.bind(escalationController)
);
router.post(
  '/api/v1/escalation/:escalationId/escalate',
  escalationController.escalateFurther.bind(escalationController)
);
router.get(
  '/api/v1/escalation/customer-service/available',
  escalationController.getAvailableCustomerServiceAgents.bind(escalationController)
);
router.get(
  '/api/v1/escalation/statistics',
  escalationController.getEscalationStatistics.bind(escalationController)
);

// 根端點
router.get('/', (_req: Request, res: Response) => {
  res.json({
    service: 'contracts-l1',
    version: '1.0.0',
    description:
      'SynergyMesh Contracts L1 - Core contract management service with build provenance',
    endpoints: {
      health: '/healthz',
      ready: '/readyz',
      version: '/version',
      status: '/status',
      provenance: {
        createAttestation: 'POST /api/v1/provenance/attestations',
        verifyAttestation: 'POST /api/v1/provenance/verify',
        importAttestation: 'POST /api/v1/provenance/import',
        getFileDigest: 'GET /api/v1/provenance/digest/{filePath}',
        exportAttestation: 'GET /api/v1/provenance/export/{id}',
      },
      slsa: {
        createAttestation: 'POST /api/v1/slsa/attestations',
        verifyAttestation: 'POST /api/v1/slsa/verify',
        generateDigest: 'POST /api/v1/slsa/digest',
        contractAttestation: 'POST /api/v1/slsa/contracts',
        summary: 'POST /api/v1/slsa/summary',
      },
      assignment: {
        assign: 'POST /api/v1/assignment/assign',
        updateStatus: 'POST /api/v1/assignment/status/{id}',
        getStatus: 'GET /api/v1/assignment/status/{id}',
        getWorkload: 'GET /api/v1/assignment/workload',
        reassign: 'POST /api/v1/assignment/reassign/{id}',
        escalate: 'POST /api/v1/assignment/escalate/{id}',
        getAll: 'GET /api/v1/assignment/all',
        getReport: 'GET /api/v1/assignment/report',
      },
      escalation: {
        create: 'POST /api/v1/escalation/create',
        get: 'GET /api/v1/escalation/{escalationId}',
        getByIncident: 'GET /api/v1/escalation/incident/{incidentId}',
        updateStatus: 'POST /api/v1/escalation/{escalationId}/status',
        resolve: 'POST /api/v1/escalation/{escalationId}/resolve',
        escalateFurther: 'POST /api/v1/escalation/{escalationId}/escalate',
        getAvailableAgents: 'GET /api/v1/escalation/customer-service/available',
        getStatistics: 'GET /api/v1/escalation/statistics',
      },
    },
  });
});

export default router;
