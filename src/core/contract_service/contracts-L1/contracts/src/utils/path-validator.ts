import { realpath } from 'fs/promises';
import path from 'path';

import { PathValidationError } from '../errors';
export { PathValidationError };

export interface PathValidatorConfig {
  safeRoot?: string;
  allowedAbsolutePrefixes?: string[];
}

export class PathValidator {
  protected readonly config: PathValidatorConfig;

  constructor(config: PathValidatorConfig = {}) {
    this.config = config;
  }

  /**
   * Basic path validation to prevent traversal attacks and ensure containment within safeRoot.
   * Resolves to a canonical path or throws on error.
   */
  async validateAndResolvePath(filePath: string): Promise<string> {
    if (!filePath || typeof filePath !== 'string') {
      throw new PathValidationError('Invalid file path');
    }

    const normalizedInput = path.normalize(filePath);
    if (
      filePath.includes('\0') ||
      filePath.split(path.sep).includes('..') ||
      normalizedInput.includes(`..${path.sep}`) ||
      normalizedInput.startsWith('..')
    ) {
      throw new PathValidationError('Invalid file path');
    }

    const safeRoot = path.resolve(this.config.safeRoot || process.cwd());
    const root = path.parse(normalizedInput).root || '/';
    const relativeToRoot = path.relative(root, normalizedInput);
    const resolvedCandidate = path.isAbsolute(normalizedInput)
      ? path.resolve(safeRoot, relativeToRoot)
      : path.resolve(safeRoot, normalizedInput);

    const canonicalPath = await realpath(resolvedCandidate);

    const allowedPrefixes = this.config.allowedAbsolutePrefixes?.map((p) => path.resolve(p)) || [];
    const isAllowedPrefix = allowedPrefixes.some((prefix) => canonicalPath.startsWith(prefix));

    if (!canonicalPath.startsWith(safeRoot) && !isAllowedPrefix) {
      throw new PathValidationError('Path escapes safe root');
    }

    return canonicalPath;
  }
}
