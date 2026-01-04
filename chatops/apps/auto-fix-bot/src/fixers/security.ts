import { Octokit } from '@octokit/rest';
import { logger } from '../utils/logger';

interface PRContext {
  owner: string;
  repo: string;
  pullNumber: number;
  headRef: string;
}

export class SecurityFixer {
  private octokit: Octokit;

  constructor(octokit: Octokit) {
    this.octokit = octokit;
  }

  async checkPR(context: PRContext): Promise<void> {
    try {
      const { data: files } = await this.octokit.pulls.listFiles({
        owner: context.owner,
        repo: context.repo,
        pull_number: context.pullNumber,
      });

      const issues: Array<{ file: string; issue: string; severity: string }> = [];

      for (const file of files) {
        // Check Dockerfiles
        if (file.filename.includes('Dockerfile')) {
          const dockerIssues = await this.checkDockerfile(context, file.filename);
          issues.push(...dockerIssues);
        }

        // Check GitHub Actions
        if (file.filename.startsWith('.github/workflows/')) {
          const actionIssues = await this.checkGitHubActions(context, file.filename);
          issues.push(...actionIssues);
        }

        // Check for secrets
        if (file.patch) {
          const secretIssues = this.checkForSecrets(file.filename, file.patch);
          issues.push(...secretIssues);
        }
      }

      if (issues.length > 0) {
        await this.commentOnPR(context, issues);
      }
    } catch (error) {
      logger.error('Error in security check', { context, error });
    }
  }

  private async checkDockerfile(
    context: PRContext,
    path: string
  ): Promise<Array<{ file: string; issue: string; severity: string }>> {
    const issues: Array<{ file: string; issue: string; severity: string }> = [];

    try {
      const { data: file } = await this.octokit.repos.getContent({
        owner: context.owner,
        repo: context.repo,
        path,
        ref: context.headRef,
      });

      if ('content' in file) {
        const content = Buffer.from(file.content, 'base64').toString('utf-8');
        const lines = content.split('\n');

        for (let i = 0; i < lines.length; i++) {
          const line = lines[i];

          // Check for root user
          if (line.match(/^USER\s+root/i)) {
            issues.push({
              file: path,
              issue: `Line ${i + 1}: Running as root user`,
              severity: 'high',
            });
          }

          // Check for unpinned base images
          if (line.match(/^FROM\s+\w+:latest/i)) {
            issues.push({
              file: path,
              issue: `Line ${i + 1}: Using :latest tag (unpinned)`,
              severity: 'medium',
            });
          }

          // Check for ADD instead of COPY
          if (line.match(/^ADD\s+(?!https?:)/i)) {
            issues.push({
              file: path,
              issue: `Line ${i + 1}: Using ADD instead of COPY`,
              severity: 'low',
            });
          }
        }
      }
    } catch {
      // File not accessible
    }

    return issues;
  }

  private async checkGitHubActions(
    context: PRContext,
    path: string
  ): Promise<Array<{ file: string; issue: string; severity: string }>> {
    const issues: Array<{ file: string; issue: string; severity: string }> = [];

    try {
      const { data: file } = await this.octokit.repos.getContent({
        owner: context.owner,
        repo: context.repo,
        path,
        ref: context.headRef,
      });

      if ('content' in file) {
        const content = Buffer.from(file.content, 'base64').toString('utf-8');

        // Check for unpinned actions
        const unpinnedPattern = /uses:\s+[\w-]+\/[\w-]+@v\d+/g;
        const matches = content.match(unpinnedPattern);
        if (matches) {
          for (const match of matches) {
            issues.push({
              file: path,
              issue: `Unpinned action: ${match} (use SHA instead)`,
              severity: 'medium',
            });
          }
        }

        // Check for write-all permissions
        if (content.includes('permissions: write-all')) {
          issues.push({
            file: path,
            issue: 'Using write-all permissions (too permissive)',
            severity: 'high',
          });
        }

        // Check for pull_request_target without restrictions
        if (content.includes('pull_request_target') && !content.includes('if:')) {
          issues.push({
            file: path,
            issue: 'pull_request_target without conditional check',
            severity: 'critical',
          });
        }
      }
    } catch {
      // File not accessible
    }

    return issues;
  }

  private checkForSecrets(
    path: string,
    patch: string
  ): Array<{ file: string; issue: string; severity: string }> {
    const issues: Array<{ file: string; issue: string; severity: string }> = [];

    const secretPatterns = [
      { pattern: /(?:api[_-]?key|apikey)\s*[:=]\s*['"][^'"]+['"]/gi, name: 'API Key' },
      { pattern: /(?:secret[_-]?key|secretkey)\s*[:=]\s*['"][^'"]+['"]/gi, name: 'Secret Key' },
      { pattern: /(?:password|passwd|pwd)\s*[:=]\s*['"][^'"]+['"]/gi, name: 'Password' },
      { pattern: /(?:token)\s*[:=]\s*['"][^'"]+['"]/gi, name: 'Token' },
      { pattern: /(?:private[_-]?key)\s*[:=]\s*['"][^'"]+['"]/gi, name: 'Private Key' },
    ];

    for (const { pattern, name } of secretPatterns) {
      if (pattern.test(patch)) {
        issues.push({
          file: path,
          issue: `Potential ${name} detected in diff`,
          severity: 'critical',
        });
      }
    }

    return issues;
  }

  private async commentOnPR(
    context: PRContext,
    issues: Array<{ file: string; issue: string; severity: string }>
  ): Promise<void> {
    const critical = issues.filter((i) => i.severity === 'critical');
    const high = issues.filter((i) => i.severity === 'high');
    const medium = issues.filter((i) => i.severity === 'medium');
    const low = issues.filter((i) => i.severity === 'low');

    const body = `## 🔒 Security Analysis Results

| Severity | Count |
|----------|-------|
| 🔴 Critical | ${critical.length} |
| 🟠 High | ${high.length} |
| 🟡 Medium | ${medium.length} |
| 🔵 Low | ${low.length} |

### Findings

${issues.map((i) => `- **[${i.severity.toUpperCase()}]** \`${i.file}\`: ${i.issue}`).join('\n')}

${critical.length > 0 ? '⚠️ **This PR cannot be merged until critical issues are resolved.**' : ''}`;

    await this.octokit.issues.createComment({
      owner: context.owner,
      repo: context.repo,
      issue_number: context.pullNumber,
      body,
    });
  }
}
