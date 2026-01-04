package chatops.autofix

default allow = false

# Simple policy: only allow fixes for whitelisted scopes
allow {
  input.scope == "workflows"
}
allow {
  input.scope == "naming"
}
allow {
  input.scope == "formatting"
}
allow {
  input.scope == "dependencies"
}
allow {
  input.scope == "artifacts"
}
