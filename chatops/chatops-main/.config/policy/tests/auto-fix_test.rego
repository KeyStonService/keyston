package chatops.autofix

test_allow_scopes {
  allow with input as {"scope":"naming"}
  allow with input as {"scope":"workflows"}
}

test_deny_unknown {
  not allow with input as {"scope":"unknown"}
}
