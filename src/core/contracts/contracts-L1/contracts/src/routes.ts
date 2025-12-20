import { Router, Request, Response } from 'express';
import type { Router as RouterType } from 'express';
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

// Generic API rate limiter for expensive endpoints
const apiLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
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
router.post('/api/v1/provenance/attestations', apiLimiter, provenanceController.createAttestation);
router.post('/api/v1/provenance/attest', apiLimiter, provenanceController.createAttestation); // Alias for tests
router.post('/api/v1/provenance/verify', apiLimiter, provenanceController.verifyAttestation);
router.post('/api/v1/provenance/import', apiLimiter, provenanceController.importAttestation);
router.post('/api/v1/provenance/digest', apiLimiter, provenanceController.getFileDigest); // POST for tests
router.get('/api/v1/provenance/digest/:filePath(*)', apiLimiter, provenanceController.getFileDigest);
router.get('/api/v1/provenance/export/:id', apiLimiter, provenanceController.exportAttestation);

// SLSA 認證端點
router.post('/api/v1/slsa/attestations', apiLimiter, slsaController.createAttestation);
router.post('/api/v1/slsa/verify', apiLimiter, slsaController.verifyAttestation);
router.post('/api/v1/slsa/digest', apiLimiter, slsaController.generateDigest);
router.post('/api/v1/slsa/contracts', apiLimiter, slsaController.createContractAttestation);
router.post('/api/v1/slsa/summary', apiLimiter, slsaController.getAttestationSummary);

// 自動分派端點 (Auto-Assignment Endpoints)
router.post('/api/v1/assignment/assign', apiLimiter, assignmentController.assignResponsibility);
router.post('/api/v1/assignment/status/:id', apiLimiter, assignmentController.updateStatus);
router.get('/api/v1/assignment/status/:id', apiLimiter, assignmentController.getAssignmentStatus);
router.get('/api/v1/assignment/workload', apiLimiter, assignmentController.getWorkload);
router.post('/api/v1/assignment/reassign/:id', apiLimiter, assignmentController.reassign);
router.post('/api/v1/assignment/escalate/:id', apiLimiter, assignmentController.escalate);
router.get('/api/v1/assignment/all', apiLimiter, assignmentController.getAllAssignments);
router.get('/api/v1/assignment/report', apiLimiter, assignmentController.getPerformanceReport);

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
