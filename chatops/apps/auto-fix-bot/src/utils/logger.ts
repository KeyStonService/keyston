import winston from 'winston';

const { combine, timestamp, json, printf } = winston.format;

const devFormat = printf(({ level, message, timestamp, ...meta }) => {
  const metaStr = Object.keys(meta).length ? JSON.stringify(meta) : '';
  return `${timestamp} [${level.toUpperCase()}] ${message} ${metaStr}`;
});

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: combine(
    timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }),
    process.env.NODE_ENV === 'development' ? devFormat : json()
  ),
  defaultMeta: {
    service: 'auto-fix-bot',
    version: process.env.APP_VERSION || '1.0.0',
  },
  transports: [new winston.transports.Console()],
});
