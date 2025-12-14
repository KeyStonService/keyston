import { createHash, randomUUID } from 'crypto';
import { readFile, stat, realpath } from 'fs/promises';
import { tmpdir } from 'os';
import * as path from 'path';

import { PathValidator } from '../utils/path-validator';
import { SelfHealingPathValidator } from '../utils/self-healing-path-validator';
import { pathValidationEvents, PathValidationEventType } from '../events/path-validation-events';

import { SLSAAttestationService, SLSAProvenance, BuildMetadata } from './attestation';

// Define a safe root directory for allowed file operations
// In test environment, this can be overridden to use tmpdir
const SAFE_ROOT =
  process.env.NODE_ENV === 'test'
    ? path.resolve(process.cwd()) // Allow access to cwd and subdirectories in test
    : path.resolve(process.cwd(), 'safefiles');

/**
 * Checks if a path is within the allowed root directory.
 */
function isPathContained(targetPath: string, rootPath: string): boolean {
  const relative = path.relative(rootPath, targetPath);
  return !relative.startsWith('..') && !path.isAbsolute(relative);
}

/**
 * Checks if a path is within the system temp directory in test mode.
 */
function isInTestTmpDir(targetPath: string, systemTmpDir: string): boolean {
  return (
    process.env.NODE_ENV === 'test' &&
    (targetPath === systemTmpDir || targetPath.startsWith(systemTmpDir + path.sep))
  );
}

/**
 * Resolves a file path based on whether it's absolute and in test environment.
 */
function resolveFilePath(filePath: string, safeRoot: string, systemTmpDir: string): string {
  if (!path.isAbsolute(filePath)) {
    return path.resolve(safeRoot, filePath);
  }

  if (isInTestTmpDir(filePath, systemTmpDir)) {
    return path.resolve(systemTmpDir, path.relative(systemTmpDir, filePath));
  }

  return path.resolve(safeRoot, path.relative('/', filePath));
}

/**
 * Validates and normalizes a file path with self-healing capabilities.
 * 
 * This function now integrates event-driven structure completion:
 * - Emits events on validation failures
 * - Triggers fallback recovery mechanisms
 * - Supports DAG-based structure reconstruction
 * - Maintains structural snapshots for recovery
 *
 * @param filePath - The file path to validate (can be relative or absolute)
 * @param safeRoot - Optional safe root directory override (primarily for testing)
 * @returns The validated and normalized absolute path
 * @throws Error if the path attempts to escape SAFE_ROOT or is invalid
 */
async function validateAndNormalizePath(
  filePath: string,
  safeRoot: string = SAFE_ROOT
): Promise<string> {
  if (!filePath || typeof filePath !== 'string') {
    throw new Error('Invalid file path: Path must be a non-empty string');
  }

  // Reject null bytes which can be used for path traversal exploits
  if (filePath.includes('\0')) {
    throw new Error('Invalid file path: Null bytes are not permitted.');
  }

  // Check for directory traversal in path segments BEFORE normalization
  // This prevents path.normalize() from resolving .. segments before we can check them
  // Split on both forward and backward slashes to catch all path separator variants
  const segments = filePath.split(/[/\\]/);
  if (segments.some(segment => segment === '..')) {
    throw new Error('Invalid file path: Directory traversal is not permitted.');
  }

  const systemTmpDir = tmpdir();
  const resolvedPath = resolveFilePath(filePath, safeRoot, systemTmpDir);

  try {
    const canonicalPath = await realpath(resolvedPath);

    // Verify canonical path is within allowed boundaries
    if (isInTestTmpDir(canonicalPath, systemTmpDir)) {
      return canonicalPath;
    }

    if (!isPathContained(canonicalPath, safeRoot)) {
      throw new Error('Invalid file path: Access outside of allowed directory is not permitted');
    }

    return canonicalPath;
  } catch (error) {
    // Fallback for non-existent file: Event-driven structure completion mechanism
    // This triggers the self-healing system to attempt structure recovery
    pathValidationEvents.emitFallbackTriggered({
      filePath,
      resolvedPath,
      safeRoot,
      error: error instanceof Error ? error.message : String(error),
      errorCode: (error as any).code,
    });

    const normalizedPath = path.normalize(resolvedPath);

    if (isInTestTmpDir(normalizedPath, systemTmpDir)) {
      if (!isPathContained(normalizedPath, systemTmpDir)) {
        throw new Error('Invalid file path: Access outside of allowed directory is not permitted');
      }
      throw error;
    }

    if (!isPathContained(normalizedPath, safeRoot)) {
      throw new Error('Invalid file path: Access outside of allowed directory is not permitted');
    }

    throw error;
  }
}

export interface BuildAttestation {
  id: string;
  timestamp: string;
  subject: {
    name: string;
    digest: string;
    path?: string;
  };
  predicate: {
    type: string;
    builder: BuilderInfo;
    recipe: RecipeInfo;
    metadata: MetadataInfo;
    materials?: Material[];
  };
  signature?: string;
  // 添加 SLSA 認證支援
  slsaProvenance?: SLSAProvenance;
}

export interface BuilderInfo {
  id: string;
  version: string;
  builderDependencies?: Dependency[];
}

export interface RecipeInfo {
  type: string;
  definedInMaterial?: string;
  entryPoint?: string;
  arguments?: Record<string, unknown>;
  environment?: Record<string, unknown>;
}

export interface MetadataInfo {
  buildStartedOn: string;
  buildFinishedOn: string;
  completeness: {
    parameters: boolean;
    environment: boolean;
    materials: boolean;
  };
  reproducible: boolean;
  buildInvocationId?: string;
}

export interface Material {
  uri: string;
  digest: Record<string, string>;
}

export interface Dependency {
  uri: string;
  digest: Record<string, string>;
  name?: string;
  version?: string;
}

export class ProvenanceService {
  private readonly slsaService: SLSAAttestationService;
  private readonly pathValidator: PathValidator | SelfHealingPathValidator;
  private readonly selfHealingEnabled: boolean;

  constructor(pathValidator?: PathValidator | SelfHealingPathValidator, enableSelfHealing = true) {
    this.slsaService = new SLSAAttestationService();
    this.selfHealingEnabled = enableSelfHealing;
    
    // Use self-healing validator by default if enabled
    if (enableSelfHealing && !pathValidator) {
      this.pathValidator = new SelfHealingPathValidator({
        safeRoot: SAFE_ROOT,
        enableAutoRecovery: true,
        enableSnapshotting: true,
        dagEnabled: true,
      });
    } else {
      this.pathValidator = pathValidator || new PathValidator();
    }
  }

  /**
   * 生成文件的 SHA256 摘要
   * Validates the file path to prevent path traversal attacks.
   */
  async generateFileDigest(filePath: string): Promise<string> {
    const validatedPath = await validateAndNormalizePath(filePath);
    const content = await readFile(validatedPath);
    const hash = createHash('sha256');
    hash.update(content);
    return `sha256:${hash.digest('hex')}`;
  }

  /**
   * 創建構建認證 - 使用 SLSA 格式
   * Validates the file path to prevent path traversal attacks.
   */
  async createBuildAttestation(
    subjectPath: string,
    builder: BuilderInfo,
    metadata: Partial<MetadataInfo> = {}
  ): Promise<BuildAttestation> {
    // Use validateAndNormalizePath to resolve symlinks and validate path security
    const validatedPath = await validateAndNormalizePath(subjectPath);

    const stats = await stat(validatedPath);
    if (!stats.isFile()) {
      throw new Error(`Subject path must be a file: ${subjectPath}`);
    }

    const content = await readFile(validatedPath);
    const subject = this.slsaService.createSubjectFromContent(
      path.relative(process.cwd(), validatedPath),
      content
    );

    // 生成格式為 att_timestamp_hash 的 ID
    const timestamp = Date.now();
    const hash = createHash('sha256')
      .update(`${timestamp}${subjectPath}`)
      .digest('hex')
      .substring(0, 8);
    const attestationId = `att_${timestamp}_${hash}`;

    const buildInvocationId = metadata.buildInvocationId || randomUUID();
    const startedOn = metadata.buildStartedOn || new Date().toISOString();
    const finishedOn = metadata.buildFinishedOn || new Date().toISOString();

    const buildMetadata: BuildMetadata = {
      buildType: 'https://synergymesh.dev/contracts/build/v1',
      invocationId: buildInvocationId,
      startedOn,
      finishedOn,
      builder: {
        id: builder.id,
        version: {
          builderVersion: builder.version,
          nodeVersion: process.version,
        },
      },
      externalParameters: {
        entryPoint: 'npm run build',
        environment: process.env.NODE_ENV || 'production',
      },
      dependencies: builder.builderDependencies?.map((dep) => ({
        uri: dep.uri,
        digest: dep.digest,
        name: dep.name,
      })),
    };

    const slsaProvenance = await this.slsaService.createProvenance([subject], buildMetadata);

    // 轉換為既有的 BuildAttestation 格式以保持相容性
    return {
      id: attestationId,
      timestamp: startedOn,
      subject: {
        name: subject.name,
        digest: `sha256:${subject.digest.sha256}`,
        path: subjectPath,
      },
      predicate: {
        type: slsaProvenance.predicateType,
        builder,
        recipe: {
          type: 'https://github.com/synergymesh/build',
          definedInMaterial: 'package.json',
          entryPoint: 'npm run build',
          arguments: buildMetadata.externalParameters || {},
          environment: {
            NODE_ENV: process.env.NODE_ENV || 'production',
            NODE_VERSION: process.version,
          },
        },
        metadata: {
          buildStartedOn: startedOn,
          buildFinishedOn: finishedOn,
          completeness: {
            parameters: true,
            environment: true,
            materials: true,
          },
          reproducible: metadata.reproducible !== undefined ? metadata.reproducible : false,
          buildInvocationId,
        },
      },
      // 附加 SLSA 認證資料
      slsaProvenance,
    };
  }

  /**
   * 驗證認證的完整性
   * Validates file paths to prevent path traversal attacks.
   */
  async verifyAttestation(attestation: BuildAttestation): Promise<boolean> {
    try {
      // 基本結構驗證
      if (
        !attestation.id ||
        !attestation.timestamp ||
        !attestation.subject ||
        !attestation.predicate
      ) {
        return false;
      }

      // 如果有文件路徑，驗證摘要
      // Note: generateFileDigest now performs path validation internally
      if (attestation.subject.path) {
        const currentDigest = await this.generateFileDigest(attestation.subject.path);
        return currentDigest === attestation.subject.digest;
      }

      return true;
    } catch {
      return false;
    }
  }

  /**
   * 導出認證為 JSON 格式
   */
  exportAttestation(attestation: BuildAttestation): string {
    return JSON.stringify(attestation, null, 2);
  }

  /**
   * 從 JSON 導入認證
   */
  importAttestation(jsonData: string): BuildAttestation {
    const attestation = JSON.parse(jsonData);

    // 基本驗證
    if (!attestation.id || !attestation.predicate) {
      throw new Error('Invalid attestation format');
    }

    return attestation;
  }
}
