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
5. **Path Traversal Protection**: Comprehensive validation to prevent unauthorized file access
   - All file paths are validated and normalized using `path.resolve()` and `realpath()`
   - Strict boundary checking ensures paths remain within the designated safe root directory
   - Protection against attacks using `../`, symbolic links, and encoded characters
   - Separate validation for production and test environments
   - See: [OWASP Path Traversal Prevention](https://owasp.org/www-community/attacks/Path_Traversal)

### Integration Benefits for SynergyMesh

1. **Supply Chain Security**: Verify the integrity of contract deployments and updates
2. **Compliance**: Meet regulatory requirements for software provenance
3. **Audit Trail**: Maintain detailed records of all build and deployment activities
4. **Trust Verification**: Enable third parties to verify the authenticity of deployed contracts

## Security Architecture

### Path Validation and Access Control

The provenance service implements comprehensive path validation to prevent path traversal attacks and unauthorized file access:

#### Safe Root Directory

- **Production**: All file operations are restricted to `process.cwd()/safefiles/`
- **Test Environment**: Allows access to `process.cwd()` and `/tmp/` for testing purposes
- Environment-specific configuration via `NODE_ENV` variable

#### Validation Process

1. **Input Validation**: Verify the path is a non-empty string
2. **Path Resolution**: Normalize paths using `path.resolve()` to eliminate `.` and `..` segments
3. **Symbolic Link Resolution**: Use `realpath()` to resolve symbolic links to their canonical paths
4. **Boundary Checking**: Ensure the canonical path starts with the safe root directory
5. **Error Handling**: Reject any paths that attempt to escape the safe root

#### Protection Against Common Attacks

- **Relative Path Attacks**: `../../../etc/passwd` → Rejected
- **Absolute Path Escapes**: `/etc/passwd` → Rejected (or resolved within safe root)
- **Symbolic Link Escapes**: `/tmp/../../../etc/passwd` → Rejected
- **Encoded Characters**: `..%2F..%2Fetc%2Fpasswd` → Rejected

#### Example: Secure File Access

```typescript
// ✅ SECURE: Paths are validated before use
const service = new ProvenanceService();
const digest = await service.generateFileDigest('contracts/my-contract.wasm');
// Internally validates and resolves to: /app/safefiles/contracts/my-contract.wasm

// ❌ REJECTED: Path traversal attempt
await service.generateFileDigest('../../../etc/passwd');
// Throws: "Invalid file path: Access outside of allowed directory is not permitted"
```

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
