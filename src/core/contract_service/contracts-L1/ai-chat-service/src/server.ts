/**
 * AI 聊天服務伺服器 - 無人機應用
 * AI Chat Service Server for Drone Applications
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import pino from 'pino';
import { config } from 'dotenv';
import { ChatController } from './controllers/chat-controller.js';

// Load environment variables
config();

const logger = pino({ level: process.env.LOG_LEVEL || 'info' });
const app = express();
const port = process.env.PORT || 8100;

// Initialize controller
const chatController = new ChatController();

// Middleware
app.use(helmet());
app.use(cors({
  origin: process.env.CORS_ORIGIN || '*',
  methods: ['GET', 'POST', 'OPTIONS'],
  credentials: true,
}));
app.use(express.json({ limit: '10mb' }));

// Request logging middleware
app.use((req, res, next) => {
  const start = Date.now();
  const traceId = req.headers['x-trace-id'] || `trace-${Date.now()}`;

  res.on('finish', () => {
    const duration = Date.now() - start;
    logger.info({
      traceId,
      method: req.method,
      path: req.path,
      status: res.statusCode,
      durationMs: duration,
    }, 'Request completed');
  });

  next();
});

// Health check endpoints
app.get('/health', (_req, res) => {
  res.json({ 
    status: 'ok', 
    service: 'ai-chat-service',
    timestamp: new Date().toISOString(),
  });
});

app.get('/health/live', (_req, res) => {
  res.json({ alive: true });
});

app.get('/health/ready', async (req, res) => {
  await chatController.status(req, res);
});

// API routes
app.post('/api/v1/chat', (req, res) => chatController.chat(req, res));
app.post('/api/v1/chat/stream', (req, res) => {
  req.body.stream = true;
  chatController.chat(req, res);
});
app.post('/api/v1/commands', (req, res) => chatController.droneCommand(req, res));
app.get('/api/v1/model', (req, res) => chatController.modelInfo(req, res));
app.get('/api/v1/status', (req, res) => chatController.status(req, res));

// Start server (before error handler so routes are registered first)
const server = app.listen(port, () => {
  logger.info({
    port,
    env: process.env.NODE_ENV || 'development',
    model: process.env.AI_MODEL || 'gpt-4-turbo-preview',
  }, 'AI Chat Service started');
});

// Error handling middleware (must be after all routes)
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error({ err, path: req.path }, 'Unhandled error');
  
  if (!res.headersSent) {
    res.status(500).json({
      error: 'Internal server error',
      message: process.env.NODE_ENV === 'development' ? err.message : 'An error occurred',
    });
  }
  
  next(err);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM received, shutting down gracefully');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  logger.info('SIGINT received, shutting down gracefully');
  server.close(() => {
    logger.info('Server closed');
    process.exit(0);
  });
});

export default app;
