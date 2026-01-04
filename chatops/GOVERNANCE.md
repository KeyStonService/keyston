# Governance

## Principles
- Least privilege by default
- Policy-as-Code enforced on PR
- Evidence required for production changes (SBOM/attest/provenance)
- Naming governance is mandatory for K8s and platform artifacts

## Exceptions
Exceptions must be:
- filed as PR with label `governance-exception`
- include scope, justification, expiration date
- approved by CODEOWNERS security + platform

## Freeze / Unfreeze
- Freeze creates `gate-lock-attest.yaml` gate file
- CI freeze-gate blocks deployments while gate is present
