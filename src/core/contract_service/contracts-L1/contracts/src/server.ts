import cors from 'cors';
import express, { Application } from 'express';
import helmet from 'helmet';

// eslint-disable-next-line import/no-named-as-default
import config from './config';
import { errorMiddleware, notFoundMiddleware } from './middleware/error';
// eslint-disable-next-line import/no-named-as-default, import/no-named-as-default-member
import loggingMiddleware from './middleware/logging';
import routes from './routes';

const app: Application = express();

app.use(helmet());
app.use(cors());
// eslint-disable-next-line import/no-named-as-default-member
app.use(express.json());

app.use(loggingMiddleware);
app.use('/', routes);
app.use(notFoundMiddleware);
app.use(errorMiddleware);

// Only start server if not in test environment
if (process.env.NODE_ENV !== 'test') {
  const server = app.listen(config.PORT, () => {
    console.log(`${config.SERVICE_NAME} running on port ${config.PORT}`);
    console.log(`Environment: ${config.NODE_ENV}`);
    console.log(`Log level: ${config.LOG_LEVEL}`);
    console.log('Build Provenance Service enabled');
  });

  process.on('SIGTERM', () => {
    console.log('SIGTERM received, shutting down...');
    const shutdownTimeout = setTimeout(() => {
      console.error('Shutdown timed out, forcing exit.');
      process.exit(1);
    }, 10000); // 10 seconds
    server.close((err?: Error) => {
      clearTimeout(shutdownTimeout);
      if (err) {
        console.error('Error during server shutdown:', err);
        process.exit(1);
      } else {
        process.exit(0);
      }
    });
  });
}
