import { randomUUID, createHash } from 'crypto';

import { z } from 'zod';

// SLSA Provenance Schema
const SLSAProvenanceSchema = z.object({
  _type: z.literal('https://in-toto.io/Statement/v1'),
  subject: z.array(
    z.object({
      name: z.string(),
      digest: z.record(z.string()),
    })
  ),
  predicateType: z.literal('https://slsa.dev/provenance/v1'),
  predicate: z.object({
    buildDefinition: z.object({
      buildType: z.string(),
      externalParameters: z.record(z.any()),
      internalParameters: z.record(z.any()).optional(),
      resolvedDependencies: z
        .array(
          z.object({
            uri: z.string(),
            digest: z.record(z.string()).optional(),
            name: z.string().optional(),
          })
        )
        .optional(),
    }),
    runDetails: z.object({
      builder: z.object({
        id: z.string(),
        builderDependencies: z
          .array(
            z.object({
              uri: z.string(),
              digest: z.record(z.string()).optional(),
            })
          )
          .optional(),
        version: z.record(z.string()).optional(),
      }),
      metadata: z.object({
        invocationId: z.string(),
        startedOn: z.string().datetime(),
        finishedOn: z.string().datetime().optional(),
      }),
      byproducts: z
        .array(
          z.object({
            name: z.string().optional(),
            uri: z.string().optional(),
            digest: z.record(z.string()).optional(),
          })
        )
        .optional(),
    }),
  }),
});

export type SLSAProvenance = z.infer<typeof SLSAProvenanceSchema>;

export interface AttestationSubject {
  name: string;
  digest: Record<string, string>;
}

export interface BuildMetadata {
  buildType: string;
  invocationId: string;
  startedOn: string;
  finishedOn?: string;
  builder: {
    id: string;
    version?: Record<string, string>;
  };
  externalParameters?: Record<string, unknown>;
  dependencies?: Array<{
    uri: string;
    digest?: Record<string, string>;
    name?: string;
  }>;
}

export class SLSAAttestationService {
  /**
   * Generate SHA256 digest for a given input
   */
  private generateDigest(input: string | Buffer): string {
    return createHash('sha256').update(input).digest('hex');
  }

  /**
   * Create SLSA provenance attestation
   */
  public async createProvenance(
    subjects: AttestationSubject[],
    metadata: BuildMetadata
  ): Promise<SLSAProvenance> {
    const provenance: SLSAProvenance = {
      _type: 'https://in-toto.io/Statement/v1',
      subject: subjects,
      predicateType: 'https://slsa.dev/provenance/v1',
      predicate: {
        buildDefinition: {
          buildType: metadata.buildType,
          externalParameters: metadata.externalParameters || {},
          internalParameters: {},
          resolvedDependencies: metadata.dependencies,
        },
        runDetails: {
          builder: {
            id: metadata.builder.id,
            version: metadata.builder.version,
          },
          metadata: {
            invocationId: metadata.invocationId,
            startedOn: metadata.startedOn,
            finishedOn: metadata.finishedOn,
          },
        },
      },
    };

    // Validate the provenance against schema
    return SLSAProvenanceSchema.parse(provenance);
  }

  /**
   * Create attestation subject from file content
   */
  public createSubjectFromContent(name: string, content: string | Buffer): AttestationSubject {
    const digest = this.generateDigest(content);
    return {
      name,
      digest: {
        sha256: digest,
      },
    };
  }

  /**
   * Create attestation subject from existing digest
   */
  public createSubjectFromDigest(name: string, sha256Digest: string): AttestationSubject {
    return {
      name,
      digest: {
        sha256: sha256Digest,
      },
    };
  }

  /**
   * Verify provenance attestation
   */
  public async verifyProvenance(provenance: unknown): Promise<boolean> {
    try {
      SLSAProvenanceSchema.parse(provenance);
      return true;
    } catch (error) {
      console.error('Provenance verification failed:', error);
      return false;
    }
  }

  /**
   * Generate build metadata for contract deployment
   */
  public generateContractBuildMetadata(
    contractName: string,
    version: string,
    deployer: string
  ): BuildMetadata {
    return {
      buildType: 'https://synergymesh.dev/contracts/build/v1',
      invocationId: randomUUID(),
      startedOn: new Date().toISOString(),
      builder: {
        id: 'https://synergymesh.dev/builder/contracts-l1',
        version: {
          'synergymesh-contracts': version,
          node: process.version,
        },
      },
      externalParameters: {
        contractName,
        deployer,
        environment: process.env.NODE_ENV || 'development',
      },
    };
  }
}
