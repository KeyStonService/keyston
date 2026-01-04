import { Octokit } from '@octokit/rest';
import { logger } from '../utils/logger';

interface PRContext {
  owner: string;
  repo: string;
  pullNumber: number;
  headRef: string;
}

export class DependencyFixer {
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

      const dependencyFiles = files.filter(
        (f) =>
          f.filename === 'package.json' ||
          f.filename === 'package-lock.json' ||
          f.filename === 'go.mod' ||
          f.filename === 'go.sum' ||
          f.filename === 'requirements.txt' ||
          f.filename === 'Pipfile.lock'
      );

      if (dependencyFiles.length > 0) {
        await this.analyzeDependencyChanges(context, dependencyFiles);
      }
    } catch (error) {
      logger.error('Error in dependency check', { context, error });
    }
  }

  private async analyzeDependencyChanges(
    context: PRContext,
    files: Array<{ filename: string; patch?: string }>
  ): Promise<void> {
    const changes: Array<{
      file: string;
      added: string[];
      removed: string[];
      updated: string[];
    }> = [];

    for (const file of files) {
      if (file.patch) {
        const analysis = this.parsePatch(file.filename, file.patch);
        if (analysis.added.length > 0 || analysis.removed.length > 0 || analysis.updated.length > 0) {
          changes.push({ file: file.filename, ...analysis });
        }
      }
    }

    if (changes.length > 0) {
      await this.commentOnPR(context, changes);
    }
  }

  private parsePatch(
    filename: string,
    patch: string
  ): { added: string[]; removed: string[]; updated: string[] } {
    const added: string[] = [];
    const removed: string[] = [];
    const updated: string[] = [];

    const lines = patch.split('\n');

    if (filename === 'package.json') {
      for (const line of lines) {
        const depMatch = line.match(/^([+-])\s*"([@\w/-]+)":\s*"([^"]+)"/);
        if (depMatch) {
          const [, sign, name, version] = depMatch;
          if (sign === '+') {
            added.push(`${name}@${version}`);
          } else {
            removed.push(`${name}@${version}`);
          }
        }
      }
    } else if (filename === 'go.mod') {
      for (const line of lines) {
        const depMatch = line.match(/^([+-])\s+([\w./]+)\s+(v[\d.]+)/);
        if (depMatch) {
          const [, sign, name, version] = depMatch;
          if (sign === '+') {
            added.push(`${name}@${version}`);
          } else {
            removed.push(`${name}@${version}`);
          }
        }
      }
    } else if (filename === 'requirements.txt') {
      for (const line of lines) {
        const depMatch = line.match(/^([+-])([\w-]+)==([\d.]+)/);
        if (depMatch) {
          const [, sign, name, version] = depMatch;
          if (sign === '+') {
            added.push(`${name}==${version}`);
          } else {
            removed.push(`${name}==${version}`);
          }
        }
      }
    }

    // Detect updates (same package in both added and removed)
    const addedNames = new Set(added.map((d) => d.split(/[@==]/)[0]));
    const removedNames = new Set(removed.map((d) => d.split(/[@==]/)[0]));

    for (const name of addedNames) {
      if (removedNames.has(name)) {
        const addedDep = added.find((d) => d.startsWith(name));
        const removedDep = removed.find((d) => d.startsWith(name));
        if (addedDep && removedDep) {
          updated.push(`${removedDep} → ${addedDep}`);
        }
      }
    }

    return { added, removed, updated };
  }

  private async commentOnPR(
    context: PRContext,
    changes: Array<{
      file: string;
      added: string[];
      removed: string[];
      updated: string[];
    }>
  ): Promise<void> {
    let body = `## 📦 Dependency Changes Detected\n\n`;

    for (const change of changes) {
      body += `### \`${change.file}\`\n\n`;

      if (change.updated.length > 0) {
        body += `**Updated:**\n`;
        for (const dep of change.updated) {
          body += `- 🔄 ${dep}\n`;
        }
        body += '\n';
      }

      if (change.added.length > 0) {
        body += `**Added:**\n`;
        for (const dep of change.added) {
          if (!change.updated.some((u) => u.includes(dep))) {
            body += `- ➕ ${dep}\n`;
          }
        }
        body += '\n';
      }

      if (change.removed.length > 0) {
        body += `**Removed:**\n`;
        for (const dep of change.removed) {
          if (!change.updated.some((u) => u.includes(dep))) {
            body += `- ➖ ${dep}\n`;
          }
        }
        body += '\n';
      }
    }

    body += `\n> 💡 Run security scans to check for vulnerabilities in new dependencies.`;

    await this.octokit.issues.createComment({
      owner: context.owner,
      repo: context.repo,
      issue_number: context.pullNumber,
      body,
    });
  }
}
