# OPA Policy Template for Governance Enforcement

package {{ POLICY_NAME }}

violation[{"msg": msg}] {
  input.review.object.kind == "{{ TARGET_KIND }}"
  {{ VALIDATION_RULES }}
  msg := sprintf("Policy violation: %v", [input.review.object.metadata.name])
}
