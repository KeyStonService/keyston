import { createHash, randomUUID } from 'crypto';
import { readFile, stat } from 'fs/promises';
import { tmpdir } from 'os';
import * as path from 'path';

import { SLSAAttestationService, SLSAProvenance, BuildMetadata } from './attestation';
import { PathValidator } from '../utils/path-validator';

// Define a safe root directory for allowed file operations
// In test environment, this can be overridden to use tmpdir
const SAFE_ROOT =
  process.env.NODE_ENV === 'test'
    ? path.resolve(process.cwd()) // Allow access to cwd and subdirectories in test
    : path.resolve(process.cwd(), 'safefiles');

/**
 * Validates and normalizes a file path to prevent path traversal attacks.
 * Ensures the resolved path is within the SAFE_ROOT directory or is an absolute path
 * within allowed system directories (for testing only).
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

  // Handle absolute paths: only allow in test environment for tmpdir
  let resolvedPath: string;
  const systemTmpDir = tmpdir();
  if (path.isAbsolute(filePath)) {
    if (process.env.NODE_ENV === 'test' && filePath.startsWith(systemTmpDir)) {
      // In test environment, allow absolute paths to system temp directory
      resolvedPath = filePath;
    } else {
      // For production, reject absolute paths or resolve them relative to safeRoot
      resolvedPath = path.resolve(safeRoot, path.relative('/', filePath));
    }
  } else {
    // Resolve relative paths against safeRoot
    resolvedPath = path.resolve(safeRoot, filePath);
  }

  try {
    // Use realpath to resolve symbolic links and get the canonical path
    const canonicalPath = await realpath(resolvedPath);

    // In test environment, allow temp directory paths
    if (process.env.NODE_ENV === 'test' && canonicalPath.startsWith(systemTmpDir)) {
      return canonicalPath;
    }

    // Ensure the canonical path is within safeRoot using robust relative check
    const relative = path.relative(safeRoot, canonicalPath);
    if (relative.startsWith('..') || path.isAbsolute(relative)) {
      throw new Error('Invalid file path: Access outside of allowed directory is not permitted');
    }

    return canonicalPath;
  } catch (error) {
    // If realpath fails (e.g., file doesn't exist), validate the normalized path
    const normalizedPath = path.normalize(resolvedPath);

    // In test environment, allow temp directory paths even if file doesn't exist yet
    // This allows tests to validate paths before files are created
    if (process.env.NODE_ENV === 'test' && normalizedPath.startsWith(systemTmpDir)) {
      // Re-throw the original error (e.g., ENOENT) after validating the path is allowed
      throw error;
    }

    // Ensure the normalized path is within safeRoot using robust relative check
    const relative = path.relative(safeRoot, normalizedPath);
    if (relative.startsWith('..') || path.isAbsolute(relative)) {
      throw new Error('Invalid file path: Access outside of allowed directory is not permitted');
    }

    // Re-throw the original error if it's a file system error (e.g., ENOENT)
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
  private readonly pathValidator: PathValidator;

  constructor(pathValidator?: PathValidator) {
    this.slsaService = new SLSAAttestationService();
    this.pathValidator = pathValidator || new PathValidator();
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

    const content = await readFile(resolvedPath);
    const subject = this.slsaService.createSubjectFromContent(
      path.relative(process.cwd(), resolvedPath),
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
