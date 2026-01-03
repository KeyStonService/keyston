package chatops.conftest.naming

pattern := "^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\\d+\\.\\d+\\.\\d+(-[A-Za-z0-9]+)?$"

deny[msg] {
  input.kind != ""
  name := input.metadata.name
  not regex.match(pattern, name)
  msg := sprintf("deny: %s/%s name=%s violates naming pattern", [input.apiVersion, input.kind, name])
}
