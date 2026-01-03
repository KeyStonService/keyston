import winston from 'winston';
import { config } from '../config';

const { combine, timestamp, json, errors, printf } = winston.format;

// Custom format for development
const devFormat = printf(({ level, message, timestamp, ...meta }) => {
  const metaStr = Object.keys(meta).length ? JSON.stringify(meta) : '';
  return `${timestamp} [${level.toUpperCase()}] ${message} ${metaStr}`;
});

export const logger = winston.createLogger({
  level: config.logLevel,
  format: combine(
    errors({ stack: true }),
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    config.environment === 'development' ? devFormat : json()
  ),
  defaultMeta: {
    service: config.appName,
    version: config.version,
    environment: config.environment,
  },
  transports: [
    new winston.transports.Console({
      stderrLevels: ['error'],
    }),
  ],
});

// Add file transport in production
if (config.environment === 'production') {
  logger.add(
    new winston.transports.File({
      filename: '/var/log/app/error.log',
      level: 'error',
      maxsize: 10485760, // 10MB
      maxFiles: 5,
    })
  );
  logger.add(
    new winston.transports.File({
      filename: '/var/log/app/combined.log',
      maxsize: 10485760,
      maxFiles: 5,
    })
  );
}
