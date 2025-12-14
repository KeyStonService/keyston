# Supply Chain Directory

This directory contains supply chain security artifacts for SynergyMesh.

## Structure

```
supply-chain/
├── sbom/          # Software Bill of Materials
├── attestations/  # SLSA/L3 evidence
└── registry/      # Component registry (optional)
```

## Components

### SBOM (`sbom/`)
Software Bill of Materials containing:
- SPDX format SBOMs
- Provenance information
- Signing policies

### Attestations (`attestations/`)
SLSA Level 3 attestation evidence:
- Build attestations
- Provenance records
- Verification artifacts

### Registry (`registry/`)
Optional component registry for:
- Module versions
- Service definitions
- Contract schemas

## SLSA Compliance

SynergyMesh follows SLSA (Supply-chain Levels for Software Artifacts) framework:
- Level 1: Documentation of build process
- Level 2: Tamper resistance through hosted build
- Level 3: Security against specific threats

## See Also

- [SLSA Framework](https://slsa.dev/)
- [Migration Guide](../docs/MIGRATION.md)
- [Sigstore Documentation](https://docs.sigstore.dev/)
