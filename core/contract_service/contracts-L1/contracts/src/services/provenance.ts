import { createHash, randomUUID } from 'crypto';
import { readFile, stat } from 'fs/promises';
import { tmpdir } from 'os';
import { relative, resolve, sep } from 'path';

import { SLSAAttestationService, SLSAProvenance, BuildMetadata } from './attestation';

// Define safe root directories for file operations to prevent path traversal attacks
const SAFE_ROOT = resolve(process.cwd());
const TEMP_ROOT = resolve(tmpdir());

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
  private slsaService: SLSAAttestationService;
  // Define the root directory for allowed files. Change as needed for your project needs
  // Use a fixed absolute path or environment variable for SAFE_ROOT
  private static readonly SAFE_ROOT = process.env.SAFE_ROOT_PATH
    ? resolve(process.env.SAFE_ROOT_PATH)
    : resolve(__dirname, '../../safefiles');

  constructor() {
    this.slsaService = new SLSAAttestationService();
  }

  /**
   * Validate that a file path is safe to access
   * to prevent directory traversal attacks
   */
  private validatePath(filePath: string): string {
    const resolvedPath = resolve(filePath);

    // Normalize paths for case-insensitive comparison on Windows
    const normalizedResolved = resolvedPath.toLowerCase();
    const normalizedSafeRoot = SAFE_ROOT.toLowerCase();
    const normalizedTempRoot = TEMP_ROOT.toLowerCase();
    const normalizedSep = sep.toLowerCase();

    // Check if the resolved path is within allowed directories
    // This prevents both relative path traversal (../) and absolute path attacks
    const isWithinSafeRoot =
      normalizedResolved.startsWith(normalizedSafeRoot + normalizedSep) ||
      normalizedResolved === normalizedSafeRoot;
    const isWithinTempRoot =
      normalizedResolved.startsWith(normalizedTempRoot + normalizedSep) ||
      normalizedResolved === normalizedTempRoot;

    if (!isWithinSafeRoot && !isWithinTempRoot) {
      throw new Error(
        `Path traversal detected: ${filePath} attempts to access files outside the safe directory`
      );
    }

    return resolvedPath;
  }

  /**
   * 生成文件的 SHA256 摘要
   */
  async generateFileDigest(filePath: string): Promise<string> {
    const validatedPath = this.validatePath(filePath);
    const content = await readFile(validatedPath);
    const hash = createHash('sha256');
    hash.update(content);
    return `sha256:${hash.digest('hex')}`;
  }

  /**
   * 創建構建認證 - 使用 SLSA 格式
   */
  async createBuildAttestation(
    subjectPath: string,
    builder: BuilderInfo,
    metadata: Partial<MetadataInfo> = {}
  ): Promise<BuildAttestation> {
    // Validate path to prevent directory traversal attacks
    const validatedPath = this.validatePath(subjectPath);

    const stats = await stat(validatedPath);
    if (!stats.isFile()) {
      throw new Error(`Subject path must be a file: ${subjectPath}`);
    }

    const content = await readFile(validatedPath);
    const subject = this.slsaService.createSubjectFromContent(
      relative(process.cwd(), validatedPath),
      content
    );

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
        name: subject.name,
        digest: `sha256:${subject.digest.sha256}`,
        path: validatedPath,
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
