import express, { Request, Response, NextFunction } from 'express';
import { collectDefaultMetrics, register, Counter, Histogram } from 'prom-client';
import { logger } from './utils/logger';
import { config } from './config';

const app = express();

// Prometheus metrics
collectDefaultMetrics({ prefix: 'myapp_' });

const httpRequestsTotal = new Counter({
  name: 'myapp_http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'path', 'status'],
});

const httpRequestDuration = new Histogram({
  name: 'myapp_http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'path', 'status'],
  buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
});

// Middleware
app.use(express.json());

// Request logging and metrics
app.use((req: Request, res: Response, next: NextFunction) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const labels = {
      method: req.method,
      path: req.route?.path || req.path,
      status: res.statusCode.toString(),
    };

    httpRequestsTotal.inc(labels);
    httpRequestDuration.observe(labels, duration);

    logger.info('Request completed', {
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration: `${duration}s`,
    });
  });

  next();
});

// Health check endpoint
app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    version: config.version,
    timestamp: new Date().toISOString(),
  });
});

// Readiness check
app.get('/ready', (_req: Request, res: Response) => {
  res.json({
    status: 'ready',
    checks: {
      database: true,
      cache: true,
    },
  });
});

// Metrics endpoint
app.get('/metrics', async (_req: Request, res: Response) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

// API routes
app.get('/api/v1/info', (_req: Request, res: Response) => {
  res.json({
    name: config.appName,
    version: config.version,
    environment: config.environment,
    namingConvention: {
      pattern: '^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\\d+\\.\\d+\\.\\d+(-[A-Za-z0-9]+)?$',
      compliant: true,
    },
  });
});

// Error handler
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  logger.error('Unhandled error', { error: err.message, stack: err.stack });
  res.status(500).json({
    error: 'Internal Server Error',
    message: config.environment === 'development' ? err.message : undefined,
  });
});

// Start server
const server = app.listen(config.port, () => {
  logger.info(`Server started on port ${config.port}`, {
    environment: config.environment,
    version: config.version,
  });
});

// Graceful shutdown
const shutdown = (signal: string) => {
  logger.info(`Received ${signal}, shutting down gracefully`);
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });

  // Force shutdown after 30 seconds
  setTimeout(() => {
    logger.error('Forced shutdown after timeout');
    process.exit(1);
  }, 30000);
};

process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

export { app };
