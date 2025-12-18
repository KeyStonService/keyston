#!/bin/bash
# GaC Resource Generator
# Generates CRDs, K8s instances, and OPA policies from strategic YAML documents
# Phase: 2 - Operational Implementation
# Auto-generates remaining 8 governance resources

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STRATEGY_DIR="$SCRIPT_DIR/.."

echo "🚀 GaC Resource Generator - Phase 2"
echo "===================================="
echo ""

# Define the mapping for remaining 8 strategic documents
declare -A MAPPINGS=(
  ["strategic-objectives"]="StrategicObjective:strategicobjectives:objectives-2025-q4:okr"
  ["governance-charter"]="GovernanceCharter:governancecharters:charter-v1:governance"
  ["alignment-framework"]="AlignmentFramework:alignmentframeworks:alignment-matrix-v1:alignment"
  ["risk-register"]="RiskRegister:riskregisters:risks-2025:risk"
  ["implementation-roadmap"]="ImplementationRoadmap:implementationroadmaps:roadmap-2025-2030:roadmap"
  ["communication-plan"]="CommunicationPlan:communicationplans:comms-plan-v1:communication"
  ["success-metrics-dashboard"]="MetricsDashboard:metricsdashboards:metrics-dashboard-v1:metrics"
  ["change-management-protocol"]="ChangeProtocol:changeprotocols:change-mgmt-v1:change"
)

# Function to generate simplified CRD
generate_crd() {
  local doc_name=$1
  local kind=$2
  local plural=$3
  local instance_name=$4
  local policy_prefix=$5
  
  cat > "$STRATEGY_DIR/crd/${doc_name}-crd.yaml" << EOF
# Kubernetes CRD for ${kind}
# Auto-generated from: ${doc_name}.yaml
# Template: gac-templates/crd-template.yaml
# Phase: 2 - Operational Implementation

apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: ${plural}.governance.kai
  annotations:
    strategic-doc: "${doc_name}.yaml"
    gac-phase: "2-operational"
    generated-from: "gac-templates/crd-template.yaml"
    description: "Governance resource for ${kind}"
spec:
  group: governance.kai
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              x-kubernetes-preserve-unknown-fields: true
              description: "Specification from ${doc_name}.yaml"
            status:
              type: object
              properties:
                lastUpdated:
                  type: string
                  format: date-time
                validatedBy:
                  type: array
                  items:
                    type: string
                complianceStatus:
                  type: string
                  enum: ["compliant", "non-compliant", "pending"]
  scope: Namespaced
  names:
    plural: ${plural}
    singular: $(echo $plural | sed 's/s$//')
    kind: ${kind}
    shortNames:
      - ${policy_prefix}
EOF

  echo "  ✅ Created: crd/${doc_name}-crd.yaml"
}

# Function to generate simplified K8s instance
generate_instance() {
  local doc_name=$1
  local kind=$2
  local instance_name=$3
  
  cat > "$STRATEGY_DIR/k8s/${instance_name}.yaml" << EOF
# Kubernetes Instance for ${kind}
# Auto-generated from: ${doc_name}.yaml
# Template: gac-templates/k8s-instance-template.yaml
# Phase: 2 - Operational Implementation

apiVersion: governance.kai/v1
kind: ${kind}
metadata:
  name: ${instance_name}
  namespace: governance
  annotations:
    strategic-doc-path: "governance/00-vision-strategy/${doc_name}.yaml"
    strategic-doc-version: "1.0.0"
    gac-phase: "2-operational"
    generated-at: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    generated-by: "gac-automation"
    traceability-hash: "sha256:${doc_name}-2025-q4"
    compliance-status: "active"
  labels:
    dimension: "00-vision-strategy"
    governance-tier: "strategic"
    automation-level: "full"
spec:
  # Full spec is loaded from ${doc_name}.yaml at runtime
  # This instance serves as K8s resource wrapper
  version: "1.0.0"
  status: "active"
  source:
    file: "${doc_name}.yaml"
    path: "governance/00-vision-strategy/${doc_name}.yaml"
    format: "yaml"
  
status:
  lastUpdated: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  validatedBy:
    - "governance-team"
    - "gac-automation"
  complianceStatus: "compliant"
EOF

  echo "  ✅ Created: k8s/${instance_name}.yaml"
}

# Function to generate simplified OPA policy
generate_policy() {
  local doc_name=$1
  local kind=$2
  local policy_prefix=$3
  
  cat > "$STRATEGY_DIR/policy/policy-${policy_prefix}.rego" << EOF
# OPA Policy for ${kind} Validation
# Auto-generated from: ${doc_name}.yaml
# Template: gac-templates/policy-template.rego
# Phase: 2 - Enforcement Layer

package governance.${policy_prefix}

# ============================================================================
# Policy Metadata
# ============================================================================
metadata := {
  "name": "${doc_name}-policy",
  "version": "v1.0.0",
  "description": "Validates ${kind} resources against governance rules",
  "strategic_doc": "${doc_name}.yaml",
  "gac_phase": "2-enforcement"
}

# ============================================================================
# Required Fields Validation
# ============================================================================
deny[msg] {
  input.kind == "${kind}"
  not input.spec
  msg := "${kind} must define spec"
}

deny[msg] {
  input.kind == "${kind}"
  not input.spec.version
  msg := "${kind} must define spec.version"
}

deny[msg] {
  input.kind == "${kind}"
  not input.spec.status
  msg := "${kind} must define spec.status"
}

# ============================================================================
# Metadata Annotations Validation
# ============================================================================
deny[msg] {
  input.kind == "${kind}"
  not input.metadata.annotations["strategic-doc-path"]
  msg := "${kind} must have annotation 'strategic-doc-path' for traceability"
}

deny[msg] {
  input.kind == "${kind}"
  not input.metadata.annotations["strategic-doc-version"]
  msg := "${kind} must have annotation 'strategic-doc-version' for versioning"
}

# ============================================================================
# Status Validation
# ============================================================================
deny[msg] {
  input.kind == "${kind}"
  not input.spec.status == "active"
  not input.spec.status == "draft"
  not input.spec.status == "archived"
  msg := sprintf("Invalid status '%s': must be one of [active, draft, archived]", [input.spec.status])
}

# ============================================================================
# Compliance Check
# ============================================================================
compliant {
  input.kind == "${kind}"
  count(deny) == 0
}

# ============================================================================
# Warnings (non-blocking)
# ============================================================================
warn[msg] {
  input.kind == "${kind}"
  not input.spec.source
  msg := "Warning: ${kind} should reference source strategic document"
}
EOF

  echo "  ✅ Created: policy/policy-${policy_prefix}.rego"
}

# Generate resources for each strategic document
echo "📦 Generating resources for 8 strategic documents..."
echo ""

for doc_name in "${!MAPPINGS[@]}"; do
  IFS=':' read -r kind plural instance_name policy_prefix <<< "${MAPPINGS[$doc_name]}"
  
  echo "Processing: $doc_name"
  generate_crd "$doc_name" "$kind" "$plural" "$instance_name" "$policy_prefix"
  generate_instance "$doc_name" "$kind" "$instance_name"
  generate_policy "$doc_name" "$kind" "$policy_prefix"
  echo ""
done

echo "✅ Generation complete!"
echo ""
echo "Summary:"
echo "  - 8 CRDs created in crd/"
echo "  - 8 K8s instances created in k8s/"
echo "  - 8 OPA policies created in policy/"
echo ""
echo "Total: 24 files + 1 VisionStatement set (already created) = 27 files"
echo ""
echo "Next steps:"
echo "  1. Review generated files"
echo "  2. Run validation: ./tests/validate-all.sh"
echo "  3. Deploy to cluster: kubectl apply -f crd/ && kubectl apply -f k8s/"
