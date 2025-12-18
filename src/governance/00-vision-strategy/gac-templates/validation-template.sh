#!/bin/bash
# Validation Script for GaC Deployment

set -e

echo "Validating Governance-as-Code deployment..."

# Check CRDs
kubectl get crd | grep governance.kai || exit 1

# Check instances
kubectl get visionstatement,strategicobjective -n governance || exit 1

# Check OPA policies
kubectl get constrainttemplates || echo "OPA Gatekeeper not found"

echo "Validation complete!"
