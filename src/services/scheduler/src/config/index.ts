import dotenv from 'dotenv';

dotenv.config();

export const config = {
  redisHost: process.env.REDIS_HOST || 'localhost',
  redisPort: parseInt(process.env.REDIS_PORT || '6379', 10),
  redisPassword: process.env.REDIS_PASSWORD,
  maxConcurrentJobs: parseInt(process.env.MAX_CONCURRENT_JOBS || '10', 10),
  jobTimeout: parseInt(process.env.JOB_TIMEOUT || '300000', 10), // 5 minutes
  historyRetentionDays: parseInt(process.env.HISTORY_RETENTION_DAYS || '90', 10),
  nodeEnv: process.env.NODE_ENV || 'development'
};
