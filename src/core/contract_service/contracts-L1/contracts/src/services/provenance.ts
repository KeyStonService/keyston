import { createHash, randomUUID } from 'crypto';
import { readFile, stat, realpath } from 'fs/promises';
import path from 'path';

import sanitize from 'sanitize-filename';

import { PathValidationError } from '../errors';

import { SLSAAttestationService, SLSAProvenance, BuildMetadata } from './attestation';

const getSafeRoot = (): string =>
  path.resolve(process.env.SAFE_ROOT_PATH ?? path.resolve(process.cwd(), 'safefiles'));

const assertPathValid = (filePath: string): void => {
  if (!filePath || typeof filePath !== 'string') {
    throw new PathValidationError('Invalid file path: Path must be a non-empty string');
  }

  // Disallow null bytes which can truncate paths at the OS level.
  if (filePath.includes('\0')) {
    throw new PathValidationError('Invalid file path');
  }

  // Reject absolute paths; all user input must be relative to the safe root.
  if (path.isAbsolute(filePath)) {
    throw new PathValidationError('Invalid file path');
  }

  const hasDirectorySeparators = filePath.includes('/') || filePath.includes(path.sep);
  if (!hasDirectorySeparators) {
    // Treat as a simple filename; sanitize and require that it does not change.
    const sanitized = sanitize(filePath);
    if (sanitized !== filePath || !sanitized) {
      throw new PathValidationError('Invalid file path');
    }
    return;
  }

  // For multi-component paths, perform basic syntactic validation and forbid traversal segments and duplicate separators.
  const segments = filePath.split(/[\\/]+/);
  if (segments.includes('..') || filePath.includes('//') || filePath.includes('\\\\')) {
    throw new PathValidationError('Invalid file path');
  }
};

async function resolveSafePath(userInputPath: string): Promise<string> {
  assertPathValid(userInputPath);

  const safeRoot = getSafeRoot();
  const normalizedInput = path.normalize(userInputPath);

  // Canonicalize the safe root directory for robust prefix checking.
  const canonicalSafeRoot = await realpath(safeRoot);
  const canonicalSafeRootWithSep =
    canonicalSafeRoot.endsWith(path.sep) ? canonicalSafeRoot : canonicalSafeRoot + path.sep;

  // Always resolve user input relative to the canonical safe root.
  const resolvedCandidate = path.resolve(canonicalSafeRootWithSep, normalizedInput);

  // Canonicalize the candidate to resolve any symlinks.
  const canonicalPath = await realpath(resolvedCandidate);

  // Ensure the canonical path is strictly within the canonical safe root.
  const rel = path.relative(canonicalSafeRoot, canonicalPath);
  if (rel.startsWith('..') || path.isAbsolute(rel)) {
    throw new PathValidationError('Invalid file path');
  }
  // Defense-in-depth: ensure prefix match on directory boundary.
  const canonicalPathWithSep =
    canonicalPath.endsWith(path.sep) ? canonicalPath : canonicalPath + path.sep;
  if (!canonicalPathWithSep.startsWith(canonicalSafeRootWithSep)) {
    throw new PathValidationError('Invalid file path');
  }


  return canonicalPath;
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

  constructor() {
    this.slsaService = new SLSAAttestationService();
  }

  /**
   * 生成文件的 SHA256 摘要
   * Validates the file path to prevent path traversal attacks.
   */
  async generateFileDigest(filePath: string): Promise<string> {
    const validatedPath = await resolveSafePath(filePath);
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
    const validatedPath = await resolveSafePath(subjectPath);
    const stats = await stat(validatedPath);
    if (!stats.isFile()) {
      throw new Error(`Subject path must be a file: ${subjectPath}`);
    }

    const content = await readFile(validatedPath);
    const relativePath = path.relative(process.cwd(), validatedPath);
    const subjectName =
      relativePath === '' ? validatedPath : relativePath || path.basename(validatedPath);
    const subject = this.slsaService.createSubjectFromContent(subjectName, content);

    // 生成格式為 att_timestamp_hash 的 ID
    const timestamp = Date.now();
    const hash = createHash('sha256')
      .update(`${timestamp}${validatedPath}`)
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
        name: subjectName,
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
