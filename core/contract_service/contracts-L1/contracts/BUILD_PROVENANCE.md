# Build Provenance Integration

## Overview

This integration provides SLSA (Supply Chain Levels for Software Artifacts) build provenance capabilities to SynergyMesh, ensuring secure and verifiable software supply chain management.

## Features

### Core Capabilities

- **Build Attestation Generation**: Create cryptographically signed attestations for build artifacts
- **Provenance Tracking**: Record detailed information about the build process and environment
- **Integrity Verification**: Verify the authenticity and integrity of build attestations
- **Multiple Subject Support**: Support for files, digests, and checksums as attestation subjects

### API Endpoints

#### 1. Create Build Attestation

```http
POST /api/v1/provenance/attestations
Content-Type: application/json

{
  "subjectPath": "/path/to/artifact",
  "builder": {
    "id": "https://github.com/synergymesh/builder",
    "version": "1.0.0"
  },
  "metadata": {
    "reproducible": true,
    "buildInvocationId": "build-123"
  }
}
```

#### 2. Verify Attestation

```http
POST /api/v1/provenance/verify
Content-Type: application/json

{
  "attestation": {
    // Attestation object
  }
}
```

#### 3. Get File Digest

```http
GET /api/v1/provenance/digest/path/to/file
```

#### 4. Import Attestation

```http
POST /api/v1/provenance/import
Content-Type: application/json

{
  "jsonData": "{\\"id\\": \\"att_123\\", ...}"
}
```

## Data Structures

### BuildAttestation

```typescript
interface BuildAttestation {
  id: string;                // Unique attestation identifier
  timestamp: string;         // ISO 8601 timestamp
  subject: {
    name: string;           // Relative path or name
    digest: string;         // SHA256 digest with 'sha256:' prefix
    path?: string;          // Optional absolute file path
  };
  predicate: {
    type: string;           // SLSA predicate type
    builder: BuilderInfo;   // Builder information
    recipe: RecipeInfo;     // Build recipe details
    metadata: MetadataInfo; // Build metadata
    materials?: Material[]; // Optional build materials
  };
  signature?: string;       // Optional digital signature
}
```

### BuilderInfo

```typescript
interface BuilderInfo {
  id: string;                        // Builder identifier URI
  version: string;                   // Builder version
  builderDependencies?: Dependency[]; // Optional dependencies
}
```

### Security Features

1. **Cryptographic Integrity**: SHA256 hashing for file integrity verification
2. **Structured Attestations**: SLSA-compliant provenance format
3. **Timestamping**: All attestations include creation timestamps
4. **Traceability**: Unique identifiers for tracking and auditing

### Integration Benefits for SynergyMesh

1. **Supply Chain Security**: Verify the integrity of contract deployments and updates
2. **Compliance**: Meet regulatory requirements for software provenance
3. **Audit Trail**: Maintain detailed records of all build and deployment activities
4. **Trust Verification**: Enable third parties to verify the authenticity of deployed contracts

### Usage Examples

#### Basic Attestation Creation

```typescript
import { ProvenanceService } from './services/provenance';

const service = new ProvenanceService();
const attestation = await service.createBuildAttestation(
  '/path/to/contract.wasm',
  {
    id: 'https://github.com/synergymesh/builder',
    version: '1.0.0'
  }
);
```

#### Verification

```typescript
const isValid = await service.verifyAttestation(attestation);
console.log('Attestation valid:', isValid);
```

### Error Handling

All API endpoints follow the standard SynergyMesh error response format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Subject path and builder information are required",
    "traceId": "att_1234567890_abc123",
    "timestamp": "2025-11-21T15:20:00.000Z"
  }
}
```

### Future Enhancements

1. **Digital Signatures**: Integration with signing services (Sigstore, GPG)
2. **Registry Support**: Push attestations to container/artifact registries  
3. **Policy Enforcement**: Automated policy checking against attestations
4. **Batch Operations**: Support for batch attestation creation and verification
