import { Octokit } from '@octokit/rest';
import * as yaml from 'js-yaml';
import { logger } from '../utils/logger';
import { config } from '../config';

interface FileContext {
  owner: string;
  repo: string;
  path: string;
  ref: string;
}

interface PRContext {
  owner: string;
  repo: string;
  pullNumber: number;
  headRef: string;
}

export class NamingFixer {
  private octokit: Octokit;
  private pattern: RegExp;

  constructor(octokit: Octokit) {
    this.octokit = octokit;
    this.pattern = new RegExp(config.naming.pattern);
  }

  async checkAndFix(context: FileContext): Promise<void> {
    try {
      const { data: file } = await this.octokit.repos.getContent({
        owner: context.owner,
        repo: context.repo,
        path: context.path,
        ref: context.ref,
      });

      if ('content' in file) {
        const content = Buffer.from(file.content, 'base64').toString('utf-8');
        const doc = yaml.load(content) as Record<string, unknown>;

        if (doc && typeof doc === 'object' && 'metadata' in doc) {
          const metadata = doc.metadata as { name?: string };
          if (metadata.name && !this.pattern.test(metadata.name)) {
            logger.warn('Naming violation detected', {
              file: context.path,
              name: metadata.name,
              pattern: config.naming.pattern,
            });

            if (config.naming.autoFix) {
              await this.suggestFix(context, metadata.name);
            }
          }
        }
      }
    } catch (error) {
      logger.error('Error checking file', { context, error });
    }
  }

  async checkPR(context: PRContext): Promise<void> {
    try {
      const { data: files } = await this.octokit.pulls.listFiles({
        owner: context.owner,
        repo: context.repo,
        pull_number: context.pullNumber,
      });

      const violations: Array<{ file: string; name: string; suggested: string }> = [];

      for (const file of files) {
        if (file.filename.endsWith('.yaml') || file.filename.endsWith('.yml')) {
          const violation = await this.checkFileContent(context, file.filename);
          if (violation) {
            violations.push(violation);
          }
        }
      }

      if (violations.length > 0) {
        await this.commentOnPR(context, violations);
      }
    } catch (error) {
      logger.error('Error checking PR', { context, error });
    }
  }

  private async checkFileContent(
    context: PRContext,
    path: string
  ): Promise<{ file: string; name: string; suggested: string } | null> {
    try {
      const { data: file } = await this.octokit.repos.getContent({
        owner: context.owner,
        repo: context.repo,
        path,
        ref: context.headRef,
      });

      if ('content' in file) {
        const content = Buffer.from(file.content, 'base64').toString('utf-8');
        const doc = yaml.load(content) as Record<string, unknown>;

        if (doc && typeof doc === 'object' && 'metadata' in doc) {
          const metadata = doc.metadata as { name?: string };
          if (metadata.name && !this.pattern.test(metadata.name)) {
            return {
              file: path,
              name: metadata.name,
              suggested: this.suggestName(metadata.name),
            };
          }
        }
      }
    } catch {
      // File not found or other error
    }
    return null;
  }

  private suggestName(currentName: string): string {
    // Extract components and suggest a compliant name
    const parts = currentName.split('-');
    const env = ['dev', 'staging', 'prod'].includes(parts[0]) ? parts[0] : 'dev';
    const appName = parts.slice(env === parts[0] ? 1 : 0).join('-').replace(/[^a-z0-9-]/g, '');
    return `${env}-${appName}-deploy-v1.0.0`;
  }

  private async suggestFix(context: FileContext, name: string): Promise<void> {
    const suggested = this.suggestName(name);
    logger.info('Suggesting fix', { original: name, suggested });

    if (config.naming.createPR) {
      // Create a fix PR
      await this.createFixPR(context, name, suggested);
    }
  }

  private async createFixPR(context: FileContext, original: string, suggested: string): Promise<void> {
    logger.info('Would create PR to fix naming', {
      file: context.path,
      original,
      suggested,
    });
    // Implementation for creating a fix PR
  }

  private async commentOnPR(
    context: PRContext,
    violations: Array<{ file: string; name: string; suggested: string }>
  ): Promise<void> {
    const body = `## 🏷️ Naming Convention Violations Detected

The following resources do not comply with the naming convention:

| File | Current Name | Suggested Name |
|------|--------------|----------------|
${violations.map((v) => `| \`${v.file}\` | \`${v.name}\` | \`${v.suggested}\` |`).join('\n')}

**Expected pattern:** \`${config.naming.pattern}\`

Please update the resource names to comply with the naming convention.`;

    await this.octokit.issues.createComment({
      owner: context.owner,
      repo: context.repo,
      issue_number: context.pullNumber,
      body,
    });
  }
}
