/**
 * @fileoverview API route definitions for the Contracts L1 service.
 *
 * This module defines all HTTP endpoints for the contracts service, organized
 * into the following categories:
 *
 * ## Health & Status Endpoints
 * - `/healthz` - Kubernetes liveness probe
 * - `/readyz` - Kubernetes readiness probe
 * - `/version` - Service version information
 * - `/status` - Detailed service status and metrics
 *
 * ## Provenance API (`/api/v1/provenance/*`)
 * Build attestation and verification endpoints for software supply chain security.
 *
 * ## SLSA API (`/api/v1/slsa/*`)
 * Supply-chain Levels for Software Artifacts (SLSA) compliance endpoints.
 *
 * ## Assignment API (`/api/v1/assignment/*`)
 * Auto-assignment system for incident/task responsibility management.
 *
 * ## Escalation API (`/api/v1/escalation/*`)
 * Advanced escalation management for incidents requiring higher-level attention.
 *
 * @module routes
 * @see {@link https://slsa.dev/} SLSA Framework
 */

import { randomUUID } from 'crypto';

import { Router, Request, Response } from 'express';
import type { Router as RouterType } from 'express';
import rateLimit, { type RateLimitRequestHandler } from 'express-rate-limit';
import { AssignmentController } from './controllers/assignment';
import { EscalationController } from './controllers/escalation';
import { ProvenanceController } from './controllers/provenance';
import { SLSAController } from './controllers/slsa';
import { ErrorCode } from './errors';

/**
 * Factory function to create a rate limiter middleware with isolated state.
 * This allows tests to create independent rate limiter instances.
 *
 * Rate limiter configuration: limits each IP to 100 requests per 15-minute window.
 *
 * Rationale: These limits are intended to balance normal user activity with protection
 * against abuse (e.g., brute-force or denial-of-service attacks). Adjust `max` and
 * `windowMs` below as needed for your deployment or traffic patterns.
 *
 * @returns A configured rate limiter middleware instance
 */
export function createRateLimiter(): RateLimitRequestHandler {
  return rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 100,
    standardHeaders: true,
    legacyHeaders: false,
    handler: (req: Request, res: Response /*, next: NextFunction*/) => {
      const traceId = req.traceId || randomUUID();
      res.status(429).json({
        error: {
          code: ErrorCode.RATE_LIMIT,
          message: 'Too many requests, please try again later.',
          status: 429,
          traceId,
          timestamp: new Date().toISOString(),
        },
      });
    },
  });
}

/** Express router instance for all API routes */
const router: RouterType = Router();

/**
 * Rate limiter middleware: limits each IP to 100 requests per 15-minute window.
 * Uses the shared rate limiter instance for production.
 */
const limiter = createRateLimiter();

/** Controller instances */
const provenanceController = new ProvenanceController();
const slsaController = new SLSAController();
const assignmentController = new AssignmentController();
const escalationController = new EscalationController();

/* =============================================================================
 * HEALTH CHECK ENDPOINTS
 * Kubernetes-compatible health and readiness probes
 * ============================================================================= */

/**
 * @api {get} /healthz Liveness Probe
 * @apiName GetHealth
 * @apiGroup Health
 * @apiVersion 1.0.0
 *
 * @apiDescription Kubernetes liveness probe endpoint. Always returns HTTP 200 status.
 * Used by orchestrators to detect and restart unhealthy containers.
 *
 *
 * @apiSuccess {String} status Always "healthy"
 * @apiSuccess {String} timestamp ISO 8601 timestamp
 * @apiSuccess {String} service Service identifier
 *
 * @apiSuccessExample {json} Success-Response:
 *     HTTP/1.1 200 OK
 *     {
 *       "status": "healthy",
 *       "timestamp": "2025-12-01T10:00:00.000Z",
 *       "service": "contracts-l1"
 *     }
 */
router.get('/healthz', (_req: Request, res: Response) => {
  res.status(200).json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'contracts-l1',
  });
});

/**
 * @api {get} /readyz Readiness Probe
 * @apiName GetReady
 * @apiGroup Health
 * @apiVersion 1.0.0
 *
 * @apiDescription Kubernetes readiness probe endpoint. Returns 200 when the service
 * is ready to accept traffic. This simplified implementation always returns 200 and does not
 * currently check actual readiness status or dependencies. To be enhanced in the future.
 *
 * @apiSuccess {String} status Always "ready"
 * @apiSuccess {String} timestamp ISO 8601 timestamp
 * @apiSuccess {Object} checks Dependency health check results (empty if no deps)
 */
router.get('/readyz', (_req: Request, res: Response) => {
  res.status(200).json({
    status: 'ready',
    timestamp: new Date().toISOString(),
    checks: {},
  });
});

/**
 * @api {get} /version Version Information
 * @apiName GetVersion
 * @apiGroup Health
 * @apiVersion 1.0.0
 *
 * @apiDescription Returns service version and build information for debugging
 * and deployment verification.
 *
 * @apiSuccess {String} version Semantic version from package.json
 * @apiSuccess {String} build Git SHA or "local" for dev builds
 * @apiSuccess {String} timestamp Current server time
 */
router.get('/version', (_req: Request, res: Response) => {
  res.json({
    version: process.env.npm_package_version || '1.0.0',
    build: process.env.BUILD_SHA || 'local',
    timestamp: new Date().toISOString(),
  });
});

/**
 * @api {get} /status Service Status
 * @apiName GetStatus
 * @apiGroup Health
 * @apiVersion 1.0.0
 *
 * @apiDescription Detailed service status including uptime and memory usage.
 * Useful for monitoring and debugging.
 *
 * @apiSuccess {String} service Service identifier
 * @apiSuccess {String} status Current status ("running")
 * @apiSuccess {Number} uptime Process uptime in seconds
 * @apiSuccess {Object} memory Memory usage statistics (rss, heapTotal, heapUsed, external)
 * @apiSuccess {String} timestamp Current server time
 */
router.get('/status', (_req: Request, res: Response) => {
  res.json({
    service: 'contracts-l1',
    status: 'running',
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    timestamp: new Date().toISOString(),
  });
});

/* =============================================================================
 * PROVENANCE API ENDPOINTS
 * Build attestation and verification for software supply chain security
 * ============================================================================= */

/**
 * @api {post} /api/v1/provenance/attestations Create Build Attestation
 * @apiName CreateAttestation
 * @apiGroup Provenance
 * @apiVersion 1.0.0
 *
 * @apiDescription Creates a cryptographic attestation for a build artifact,
 * recording its provenance (origin, builder, build environment).
 *
 * @apiBody {String} filePath Path to the file to attest
 * @apiBody {String} builder Identifier of the build system/tool
 * @apiBody {Object} [metadata] Additional metadata about the build
 *
 * @apiSuccess {Object} attestation The created attestation object
 * @apiError {Object} error Error details with code and message
 */
router.post('/api/v1/provenance/attestations', limiter, provenanceController.createAttestation);
router.post('/api/v1/provenance/attest', limiter, provenanceController.createAttestation); // Alias for tests

/**
 * @api {post} /api/v1/provenance/verify Verify Attestation
 * @apiName VerifyAttestation
 * @apiGroup Provenance
 * @apiVersion 1.0.0
 *
 * @apiDescription Verifies the validity of a build attestation, checking
 * cryptographic signatures and attestation integrity.
 *
 * @apiBody {Object} attestation The attestation object to verify
 *
 * @apiSuccess {Boolean} valid Whether the attestation is valid
 * @apiSuccess {String} attestationId ID of the verified attestation
 */
router.post('/api/v1/provenance/verify', limiter, provenanceController.verifyAttestation);

/**
 * @api {post} /api/v1/provenance/import Import Attestation
 * @apiName ImportAttestation
 * @apiGroup Provenance
 * @apiVersion 1.0.0
 *
 * @apiDescription Imports an externally created attestation into the system.
 *
 * @apiBody {String} attestationJson JSON string of the attestation to import
 */
router.post('/api/v1/provenance/import', limiter, provenanceController.importAttestation);
router.post('/api/v1/provenance/digest', limiter, provenanceController.getFileDigest); // POST for tests

/**
 * @api {get} /api/v1/provenance/digest/:filePath Get File Digest
 * @apiName GetFileDigest
 * @apiGroup Provenance
 * @apiVersion 1.0.0
 *
 * @apiDescription Generates cryptographic digest (hash) for a file.
 *
 * @apiParam {String} filePath URL-encoded path to the file
 *
 * @apiSuccess {String} filePath The file path
 * @apiSuccess {String} digest SHA-256 hash of the file contents
 */
router.get('/api/v1/provenance/digest/:filePath(*)', provenanceController.getFileDigest);

/**
 * @api {get} /api/v1/provenance/export/:id Export Attestation
 * @apiName ExportAttestation
 * @apiGroup Provenance
 * @apiVersion 1.0.0
 *
 * @apiDescription Exports an attestation in a portable format for external verification.
 *
 * @apiParam {String} id Attestation identifier
 */
router.get('/api/v1/provenance/export/:id', provenanceController.exportAttestation);

/* =============================================================================
 * SLSA API ENDPOINTS
 * Supply-chain Levels for Software Artifacts compliance
 * ============================================================================= */

/**
 * @api {post} /api/v1/slsa/attestations Create SLSA Attestation
 * @apiName CreateSLSAAttestation
 * @apiGroup SLSA
 * @apiVersion 1.0.0
 *
 * @apiDescription Creates an SLSA-compliant build attestation following the
 * in-toto attestation framework.
 */
router.post('/api/v1/slsa/attestations', limiter, slsaController.createAttestation);

/** @api {post} /api/v1/slsa/verify Verify SLSA Attestation */
router.post('/api/v1/slsa/verify', limiter, slsaController.verifyAttestation);

/** @api {post} /api/v1/slsa/digest Generate SLSA Digest */
router.post('/api/v1/slsa/digest', limiter, slsaController.generateDigest);

/** @api {post} /api/v1/slsa/contracts Create Contract Attestation */
router.post('/api/v1/slsa/contracts', limiter, slsaController.createContractAttestation);

/** @api {post} /api/v1/slsa/summary Get Attestation Summary */
router.post('/api/v1/slsa/summary', limiter, slsaController.getAttestationSummary);

/* =============================================================================
 * ASSIGNMENT API ENDPOINTS
 * Auto-assignment system for incident and task responsibility management
 * ============================================================================= */

/**
 * @api {post} /api/v1/assignment/assign Create Assignment
 * @apiName AssignResponsibility
 * @apiGroup Assignment
 * @apiVersion 1.0.0
 *
 * @apiDescription Automatically assigns responsibility for an incident based on
 * type, priority, affected files, and team workload.
 *
 * @apiBody {String="FRONTEND_ERROR","BACKEND_API","DATABASE_ISSUE","PERFORMANCE","SECURITY","INFRASTRUCTURE"} type Incident type
 * @apiBody {String="CRITICAL","HIGH","MEDIUM","LOW"} priority Incident priority
 * @apiBody {String} description Incident description
 * @apiBody {String[]} [affectedFiles] List of affected file paths
 * @apiBody {String} [errorMessage] Error message if applicable
 *
 * @apiSuccess {Object} assignment Created assignment details
 * @apiSuccess {Object} incident The incident that was created
 */
router.post('/api/v1/assignment/assign', limiter, assignmentController.assignResponsibility);

/**
 * @api {post} /api/v1/assignment/status/:id Update Assignment Status
 * @apiName UpdateAssignmentStatus
 * @apiGroup Assignment
 * @apiVersion 1.0.0
 *
 * @apiParam {String} id Assignment identifier
 * @apiBody {String="ASSIGNED","ACKNOWLEDGED","IN_PROGRESS","ESCALATED","RESOLVED"} status New status
 */
router.post('/api/v1/assignment/status/:id', limiter, assignmentController.updateStatus);

/** @api {get} /api/v1/assignment/status/:id Get Assignment Status */
router.get('/api/v1/assignment/status/:id', assignmentController.getAssignmentStatus);

/** @api {get} /api/v1/assignment/workload Get Team Workload Statistics */
router.get('/api/v1/assignment/workload', assignmentController.getWorkload);

/** @api {post} /api/v1/assignment/reassign/:id Reassign to Different Owner */
router.post('/api/v1/assignment/reassign/:id', limiter, assignmentController.reassign);

/** @api {post} /api/v1/assignment/escalate/:id Escalate Assignment */
router.post('/api/v1/assignment/escalate/:id', limiter, assignmentController.escalate);

/** @api {get} /api/v1/assignment/all Get All Assignments */
router.get('/api/v1/assignment/all', assignmentController.getAllAssignments);

/** @api {get} /api/v1/assignment/report Get Performance Report */
router.get('/api/v1/assignment/report', assignmentController.getPerformanceReport);

/* =============================================================================
 * ESCALATION API ENDPOINTS
 * Advanced escalation management for incidents requiring higher-level attention
 * ============================================================================= */

/**
 * @api {post} /api/v1/escalation/create Create Escalation
 * @apiName CreateEscalation
 * @apiGroup Escalation
 * @apiVersion 1.0.0
 *
 * @apiDescription Creates a new escalation request for an incident that
 * requires additional attention or higher-level intervention.
 */
router.post(
  '/api/v1/escalation/create',
  limiter,
  escalationController.createEscalation.bind(escalationController)
);

/** @api {get} /api/v1/escalation/:escalationId Get Escalation Details */
router.get(
  '/api/v1/escalation/:escalationId',
  escalationController.getEscalation.bind(escalationController)
);

/** @api {get} /api/v1/escalation/incident/:incidentId Get Escalations by Incident */
router.get(
  '/api/v1/escalation/incident/:incidentId',
  escalationController.getEscalationsByIncident.bind(escalationController)
);

/** @api {post} /api/v1/escalation/:escalationId/status Update Escalation Status */
router.post(
  '/api/v1/escalation/:escalationId/status',
  limiter,
  escalationController.updateEscalationStatus.bind(escalationController)
);

/** @api {post} /api/v1/escalation/:escalationId/resolve Resolve Escalation */
router.post(
  '/api/v1/escalation/:escalationId/resolve',
  limiter,
  escalationController.resolveEscalation.bind(escalationController)
);

/** @api {post} /api/v1/escalation/:escalationId/escalate Escalate Further */
router.post(
  '/api/v1/escalation/:escalationId/escalate',
  limiter,
  escalationController.escalateFurther.bind(escalationController)
);

/** @api {get} /api/v1/escalation/customer-service/available Get Available CS Agents */
router.get(
  '/api/v1/escalation/customer-service/available',
  escalationController.getAvailableCustomerServiceAgents.bind(escalationController)
);

/** @api {get} /api/v1/escalation/statistics Get Escalation Statistics */
router.get(
  '/api/v1/escalation/statistics',
  escalationController.getEscalationStatistics.bind(escalationController)
);

/* =============================================================================
 * ROOT ENDPOINT
 * API discovery and documentation
 * ============================================================================= */

/**
 * @api {get} / API Root & Discovery
 * @apiName GetRoot
 * @apiGroup Root
 * @apiVersion 1.0.0
 *
 * @apiDescription Returns service information and a complete list of available
 * endpoints for API discovery. Useful for client initialization and documentation.
 *
 * @apiSuccess {String} service Service identifier
 * @apiSuccess {String} version Service version
 * @apiSuccess {String} description Service description
 * @apiSuccess {Object} endpoints Map of all available API endpoints by category
 */
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
