import express, { Express } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import { config } from './config';
import { logger } from './config/logger';
import { swaggerDocument } from './config/swagger';
import { errorHandler } from './middleware/error-handler';
import { rateLimiter } from './middleware/rate-limiter';
import { authRouter } from './routes/auth';
import { systemRouter } from './routes/system';
import { resourcesRouter } from './routes/resources';
import { tasksRouter } from './routes/tasks';
import { metricsRouter } from './routes/metrics';

const app: Express = express();

// Middleware
app.use(helmet());
app.use(cors({
  origin: config.corsOrigin,
  credentials: true
}));
app.use(compression());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(morgan('combined', {
  stream: { write: (message) => logger.info(message.trim()) }
}));

// Rate limiting
app.use('/api', rateLimiter);

// Health check (no auth required)
app.get('/health', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    version: '1.0.0'
  });
});

// API Routes
app.use('/api/v1/auth', authRouter);
app.use('/api/v1/system', systemRouter);
app.use('/api/v1/resources', resourcesRouter);
app.use('/api/v1/tasks', tasksRouter);
app.use('/api/v1/metrics', metricsRouter);

// API Documentation - OpenAPI JSON
app.get('/api/docs', (req, res) => {
  res.json(swaggerDocument);
});

// Swagger UI - Interactive API Documentation
app.get('/api/docs/ui', (req, res) => {
  res.send(`
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>API Documentation - Unmanned Island System</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css" 
        integrity="sha384-+/kNgP7D4ej/z9J/jvKNxMYHmBdJJuE1FhK9bxL6zJNFJfnXpCMh7v7kHrUb+0kJ" 
        crossorigin="anonymous">
  <style>
    body { margin: 0; padding: 0; }
    .swagger-ui .topbar { display: none; }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js" 
          integrity="sha384-GkWCaW0Wjc3gqzhyJMJe/HhxGiVNm2A7vL4nYYZ7F0CfGbEmqH5JT5j2F0nJrJvT" 
          crossorigin="anonymous"></script>
  <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-standalone-preset.js" 
          integrity="sha384-qQPAGDgBXaEhdKBBDxZpXvYgKQPnJqg+8c2NqXxv5Z3Wj7qJbKgFwGQN2J0GvGmJ" 
          crossorigin="anonymous"></script>
  <script>
    window.onload = function() {
      const ui = SwaggerUIBundle({
        url: '/api/docs',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: 'StandaloneLayout'
      });
      window.ui = ui;
    };
  </script>
</body>
</html>
  `);
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Cannot ${req.method} ${req.path}`
  });
});

// Error handler (must be last)
app.use(errorHandler);

// Start server
const port = config.port;
app.listen(port, () => {
  logger.info(`🚀 API Gateway started on port ${port}`);
  logger.info(`📚 API Documentation: http://localhost:${port}/api/docs`);
  logger.info(`🏥 Health Check: http://localhost:${port}/health`);
});

export default app;
