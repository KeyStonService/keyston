import { realpath } from 'fs/promises';
import { tmpdir } from 'os';
import * as path from 'path';

/**
 * Configuration for path validation
 */
export interface PathValidatorConfig {
  safeRoot: string;
  allowedAbsolutePrefixes: string[];
}

/**
 * Custom error for path validation failures
 */
export class PathValidationError extends Error {
  constructor(
    message: string,
    public readonly code?: string
  ) {
    super(message);
    this.name = 'PathValidationError';
    Object.setPrototypeOf(this, PathValidationError.prototype);
  }
}

/**
 * PathValidator - Handles secure path validation with symlink protection
 *
 * This class provides utilities for validating file paths to prevent
 * directory traversal and symlink bypass attacks.
 */
export class PathValidator {
  private readonly config: PathValidatorConfig;

  constructor(config?: Partial<PathValidatorConfig>) {
    const defaultSafeRoot = path.resolve(process.cwd(), 'safefiles');
    const defaultAllowedPrefixes =
      process.env.NODE_ENV === 'test'
        ? [tmpdir(), process.cwd()]
        : [process.cwd(), defaultSafeRoot];

    this.config = {
      safeRoot: config?.safeRoot || defaultSafeRoot,
      allowedAbsolutePrefixes: config?.allowedAbsolutePrefixes || defaultAllowedPrefixes,
    };
  }

  /**
   * Validate and resolve a file path with symlink protection
   *
   * @param filePath - The path to validate (absolute or relative)
   * @returns The canonicalized absolute path
   * @throws {PathValidationError} If the path is invalid or outside allowed directories
   * @throws {Error} If the file does not exist. ENOENT errors are re-thrown as-is, preserving their original error type and code.
   */
  async validateAndResolvePath(filePath: string): Promise<string> {
    return path.isAbsolute(filePath)
      ? await this._validateAbsolutePath(filePath)
      : await this._validateRelativePath(filePath);
  }

  /**
   * Resolve a path to its canonical form, handling symlinks
   *
   * @param targetPath - Path to resolve
   * @returns Canonical path
   * @throws Original error if path resolution fails
   */
  private async _resolveCanonicalPath(targetPath: string): Promise<string> {
    try {
      return await realpath(path.normalize(targetPath));
    } catch (error) {
      // Re-throw ENOENT errors as-is for proper handling by callers
      const nodeError = error as NodeJS.ErrnoException;
      if (nodeError.code === 'ENOENT') {
        throw error;
      }
      throw new PathValidationError(
        `Unable to resolve path: ${error instanceof Error ? error.message : String(error)}`,
        'PATH_RESOLUTION_FAILED'
      );
    }
  }

  /**
   * Get canonical forms of allowed prefixes
   *
   * @returns Array of canonical prefix paths
   */
  private async _getCanonicalPrefixes(): Promise<string[]> {
    return await Promise.all(
      this.config.allowedAbsolutePrefixes.map(async (prefix) => {
        try {
          return await realpath(prefix);
        } catch (error) {
          // If realpath fails (e.g., directory doesn't exist), throw a validation error
          throw new PathValidationError(
            `Allowed prefix does not exist or cannot be resolved: ${prefix} (${error instanceof Error ? error.message : String(error)})`,
            'ALLOWED_PREFIX_INVALID'
          );
        }
      })
    );
  }

  /**
   * Check if a path is within allowed directories
   *
   * @param resolvedPath - Canonical path to check
   * @param allowedPrefixes - List of allowed canonical prefixes
   * @returns true if path is allowed
   */
  private _isPathAllowed(resolvedPath: string, allowedPrefixes: string[]): boolean {
    return allowedPrefixes.some(
      (prefix) => resolvedPath.startsWith(prefix + path.sep) || resolvedPath === prefix
    );
  }

  /**
   * Validate and resolve an absolute path with symlink protection
   *
   * @param absolutePath - Absolute path to validate
   * @returns Canonical absolute path
   * @throws {PathValidationError} If path is outside allowed directories
   */
  private async _validateAbsolutePath(absolutePath: string): Promise<string> {
    const resolvedPath = await this._resolveCanonicalPath(absolutePath);
    const canonicalPrefixes = await this._getCanonicalPrefixes();

    if (!this._isPathAllowed(resolvedPath, canonicalPrefixes)) {
      throw new PathValidationError(
        'Absolute paths must be within allowed directories',
        'PATH_OUTSIDE_ALLOWED_DIRS'
      );
    }

    return resolvedPath;
  }

  /**
   * Validate and resolve a relative path with symlink protection
   *
   * @param relativePath - Relative path to validate
   * @returns Canonical absolute path
   * @throws {PathValidationError} If path is outside safe root
   */
  private async _validateRelativePath(relativePath: string): Promise<string> {
    const resolvedPath = await this._resolveCanonicalPath(
      path.resolve(this.config.safeRoot, relativePath)
    );

    let canonicalSafeRoot: string;
    try {
      canonicalSafeRoot = await realpath(this.config.safeRoot);
    } catch {
      // If SAFE_ROOT doesn't exist yet, refuse to validate paths
      throw new PathValidationError(
        'Safe root directory does not exist or cannot be resolved; cannot validate relative paths securely',
        'SAFE_ROOT_NOT_RESOLVABLE'
      );
    }

    if (
      !(resolvedPath === canonicalSafeRoot || resolvedPath.startsWith(canonicalSafeRoot + path.sep))
    ) {
      throw new PathValidationError(
        'Access outside of allowed directory is not permitted',
        'PATH_OUTSIDE_SAFE_ROOT'
      );
    }

    return resolvedPath;
  }

  /**
   * Get the safe root directory
   */
  getSafeRoot(): string {
    return this.config.safeRoot;
  }

  /**
   * Get the allowed absolute prefixes
   */
  getAllowedPrefixes(): string[] {
    return [...this.config.allowedAbsolutePrefixes];
  }
}
