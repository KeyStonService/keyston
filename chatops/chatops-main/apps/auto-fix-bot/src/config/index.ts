export const config = {
  version: process.env.APP_VERSION || '1.0.0',
  port: parseInt(process.env.PORT || '3001', 10),
  logLevel: process.env.LOG_LEVEL || 'info',

  github: {
    token: process.env.GITHUB_TOKEN || '',
    webhookSecret: process.env.GITHUB_WEBHOOK_SECRET || '',
    appId: process.env.GITHUB_APP_ID || '',
  },

  naming: {
    pattern: '^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\\d+\\.\\d+\\.\\d+(-[A-Za-z0-9]+)?$',
    autoFix: process.env.NAMING_AUTO_FIX === 'true',
    createPR: process.env.NAMING_CREATE_PR !== 'false',
  },

  allowlist: {
    path: process.env.ALLOWLIST_PATH || '.config/auto-fix/allowlist.yaml',
  },

  detectors: {
    path: process.env.DETECTORS_PATH || '.config/auto-fix/detectors.yaml',
  },
} as const;
