export const config = {
  appName: process.env.APP_NAME || 'my-app',
  version: process.env.APP_VERSION || '1.0.0',
  environment: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '3000', 10),
  logLevel: process.env.LOG_LEVEL || 'info',

  // Naming convention settings
  naming: {
    pattern: '^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\\d+\\.\\d+\\.\\d+(-[A-Za-z0-9]+)?$',
    environments: ['dev', 'staging', 'prod'],
    resourceTypes: ['deploy', 'svc', 'ing', 'cm', 'secret'],
  },

  // Metrics settings
  metrics: {
    enabled: process.env.METRICS_ENABLED !== 'false',
    prefix: 'myapp_',
  },
} as const;

export type Config = typeof config;
