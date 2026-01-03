# Security Documentation

## Path Traversal Protection

### Overview

The contracts service implements robust path traversal protection to prevent unauthorized file system access. All file operations are restricted to a designated safe directory.

### Implementation

#### Safe Root Directory

All file operations are confined to the `safefiles/` directory:

```typescript
const SAFE_ROOT = path.resolve(process.cwd(), 'safefiles');
```

#### Path Validation Algorithm

The service uses a multi-layered validation approach:

1. **Path Resolution**: User-provided paths are resolved against `SAFE_ROOT`
2. **Relative Path Check**: Ensures the resolved path doesn't escape the safe directory
3. **Absolute Path Detection**: Blocks any absolute path attempts

```typescript
// Normalize and resolve against the SAFE_ROOT
const resolvedPath = path.resolve(SAFE_ROOT, userPath);

// Cross-platform security check using path.relative()
const relativePath = path.relative(SAFE_ROOT, resolvedPath);

if (relativePath.startsWith('..') || path.isAbsolute(relativePath)) {
  throw new PathValidationError();
}
```

### Protected Operations

The following operations enforce path validation:

1. **Provenance Service**
   - `generateFileDigest(filePath)` - Generate SHA256 digest of files
   - `createBuildAttestation(subjectPath, builder, metadata)` - Create SLSA build attestations

2. **SLSA Controller**
   - `createAttestation(req, res)` - Create SLSA attestations from file paths

3. **Provenance Controller**
   - `getFileDigest(req, res)` - HTTP endpoint for file digest generation
   - `createAttestation(req, res)` - HTTP endpoint for attestation creation

### Attack Vectors Blocked

| Attack Vector | Example | Status |
|---------------|---------|--------|
| Directory Traversal | `../../../etc/passwd` | ✅ Blocked |
| Absolute Unix Path | `/etc/passwd` | ✅ Blocked |
| Absolute Windows Path | `C:\Windows\System32\config` | ✅ Blocked |
| UNC Path (Windows) | `\\server\share\file` | ✅ Blocked |
| Symbolic Link Escape | (symlinks outside safe root) | ✅ Blocked |
| Path Encoding | `%2e%2e%2f` (URL encoded) | ✅ Blocked |

### Error Handling

#### PathValidationError

Custom error class that returns HTTP 404 to prevent information disclosure:

```typescript
export class PathValidationError extends AppError {
  constructor(message = 'File not found') {
    super(message, ErrorCode.NOT_FOUND, 404);
    Object.setPrototypeOf(this, PathValidationError.prototype);
  }
}
```

**Why 404?** Returning 404 instead of 403 prevents attackers from enumerating valid paths outside the safe directory.

### Cross-Platform Compatibility

The implementation uses Node.js `path` module methods that handle platform-specific separators:

- **Windows**: `\` and `/` both handled correctly
- **Unix/Linux**: `/` handled correctly  
- **macOS**: `/` handled correctly

### Testing

Security validation is enforced through comprehensive test coverage:

```bash
npm test -- provenance.test.ts slsa.test.ts api.test.ts
```

Test coverage includes:

- Valid paths within safe directory ✅
- Directory traversal attempts ❌
- Absolute path attempts ❌
- Symlink escape attempts ❌
- Cross-platform path separators ✅

### Deployment Considerations

#### Safe Directory Setup

The `safefiles/` directory is created automatically on first use. For production deployments:

1. **Pre-create the directory** with appropriate permissions:

   ```bash
   mkdir -p safefiles
   chmod 755 safefiles
   ```

2. **Limit user permissions**: Ensure the service runs with minimal file system permissions

3. **Monitor access**: Log all file operations for audit purposes

#### Container Deployment

When deploying in containers (Docker/Kubernetes):

```dockerfile
# Create safe directory with restricted permissions
RUN mkdir -p /app/safefiles && \
    chown app:app /app/safefiles && \
    chmod 755 /app/safefiles

# Run as non-root user
USER app
WORKDIR /app
```

### Security Audit Trail

All path validation failures are logged but return generic 404 errors to clients. Monitor logs for suspicious patterns:

```typescript
// Example log entry (internal only)
{
  "timestamp": "2025-12-12T08:33:59.932Z",
  "event": "path_validation_failed",
  "requestedPath": "../../../etc/passwd",
  "resolvedPath": "/app/safefiles/../../../etc/passwd",
  "clientIP": "192.168.1.100"
}
```

### Best Practices

1. **Never disable validation**: Path validation is security-critical
2. **Review safe directory permissions**: Ensure only necessary files are accessible
3. **Rotate logs regularly**: Audit logs can contain sensitive path information
4. **Update dependencies**: Keep Node.js and path handling libraries current
5. **Monitor for bypasses**: New attack techniques emerge regularly

### Vulnerability Disclosure

If you discover a security vulnerability in this implementation, please report it responsibly:

1. **Do not** create a public GitHub issue
2. Email <security@synergymesh.dev> with details
3. Allow time for patching before public disclosure
4. We will credit security researchers in our security advisories

### References

- [CWE-22: Path Traversal](https://cwe.mitre.org/data/definitions/22.html)
- [OWASP Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- [SLSA Framework](https://slsa.dev/)
- [Node.js Path Module Documentation](https://nodejs.org/api/path.html)

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-12 | Initial path traversal protection implementation |

---

**Last Updated**: 2025-12-12  
**Maintainer**: SynergyMesh Security Team
