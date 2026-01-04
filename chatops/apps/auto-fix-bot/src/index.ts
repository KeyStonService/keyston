import express from 'express';
import { Octokit } from '@octokit/rest';
import { createNodeMiddleware } from '@octokit/webhooks';
import { Webhooks } from '@octokit/webhooks';
import { logger } from './utils/logger';
import { config } from './config';
import { NamingFixer } from './fixers/naming';
import { SecurityFixer } from './fixers/security';
import { DependencyFixer } from './fixers/dependency';

const app = express();

// Initialize GitHub App
const webhooks = new Webhooks({
  secret: config.github.webhookSecret,
});

const octokit = new Octokit({
  auth: config.github.token,
});

// Initialize fixers
const namingFixer = new NamingFixer(octokit);
const securityFixer = new SecurityFixer(octokit);
const dependencyFixer = new DependencyFixer(octokit);

// Webhook handlers
webhooks.on('push', async ({ payload }) => {
  logger.info('Received push event', {
    repo: payload.repository.full_name,
    ref: payload.ref,
    commits: payload.commits.length,
  });

  // Check for naming violations in changed files
  for (const commit of payload.commits) {
    const files = [...commit.added, ...commit.modified];
    for (const file of files) {
      if (file.endsWith('.yaml') || file.endsWith('.yml')) {
        await namingFixer.checkAndFix({
          owner: payload.repository.owner.login,
          repo: payload.repository.name,
          path: file,
          ref: payload.after,
        });
      }
    }
  }
});

webhooks.on('pull_request.opened', async ({ payload }) => {
  logger.info('Received pull_request.opened event', {
    repo: payload.repository.full_name,
    pr: payload.pull_request.number,
  });

  // Run all fixers on PR
  const context = {
    owner: payload.repository.owner.login,
    repo: payload.repository.name,
    pullNumber: payload.pull_request.number,
    headRef: payload.pull_request.head.ref,
  };

  await Promise.all([
    namingFixer.checkPR(context),
    securityFixer.checkPR(context),
    dependencyFixer.checkPR(context),
  ]);
});

webhooks.on('check_suite.completed', async ({ payload }) => {
  if (payload.check_suite.conclusion === 'failure') {
    logger.info('Check suite failed, analyzing for auto-fix', {
      repo: payload.repository.full_name,
      checkSuite: payload.check_suite.id,
    });
    // Analyze failed checks and attempt fixes
  }
});

// Health endpoint
app.get('/health', (_req, res) => {
  res.json({ status: 'healthy', version: config.version });
});

// Metrics endpoint
app.get('/metrics', (_req, res) => {
  res.set('Content-Type', 'text/plain');
  res.send('# Auto-fix bot metrics\nautofix_requests_total 0\n');
});

// Webhook middleware
app.use('/webhooks', createNodeMiddleware(webhooks));

// Start server
app.listen(config.port, () => {
  logger.info(`Auto-fix bot started on port ${config.port}`);
});

export { app };
