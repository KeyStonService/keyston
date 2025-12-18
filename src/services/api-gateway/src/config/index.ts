import dotenv from 'dotenv';
import crypto from 'crypto';

dotenv.config();

// Generate a secure random secret for development if not provided
const generateSecureSecret = (): string => {
  return crypto.randomBytes(32).toString('hex');
};

export const config = {
  port: parseInt(process.env.PORT || '8000', 10),
  nodeEnv: process.env.NODE_ENV || 'development',
  jwtSecret: process.env.JWT_SECRET || (process.env.NODE_ENV === 'production' 
    ? (() => { throw new Error('JWT_SECRET is required in production'); })() 
    : generateSecureSecret()),
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '1h',
  apiRateLimit: parseInt(process.env.API_RATE_LIMIT || '100', 10),
  corsOrigin: process.env.CORS_ORIGIN || '*',
  logLevel: process.env.LOG_LEVEL || 'info',
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production'
};
