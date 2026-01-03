package chatops.naming

default deny = []

pattern := "^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\\d+\\.\\d+\\.\\d+(-[A-Za-z0-9]+)?$"

# Supports objects that look like K8s manifests:
# input.metadata.name
deny[msg] {
  name := input.metadata.name
  not regex.match(pattern, name)
  msg := sprintf("naming policy deny: %s does not match %s", [name, pattern])
}
