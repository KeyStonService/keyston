package chatops.naming

default allow := true

# Naming pattern example (required by spec):
# ^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\d+\.\d+\.\d+(-[A-Za-z0-9]+)?$
name_pattern := "^(dev|staging|prod)-[a-z0-9-]+-(deploy|svc|ing|cm|secret)-v\\d+\\.\\d+\\.\\d+(-[A-Za-z0-9]+)?$"

deny[msg] {
  input.kind == "Deployment"
  not re_match(name_pattern, input.metadata.name)
  msg := sprintf("invalid name for Deployment: %s", [input.metadata.name])
}

deny[msg] {
  input.kind == "Service"
  not re_match(name_pattern, input.metadata.name)
  msg := sprintf("invalid name for Service: %s", [input.metadata.name])
}

deny[msg] {
  input.kind == "Ingress"
  not re_match(name_pattern, input.metadata.name)
  msg := sprintf("invalid name for Ingress: %s", [input.metadata.name])
}

deny[msg] {
  input.kind == "ConfigMap"
  not re_match(name_pattern, input.metadata.name)
  msg := sprintf("invalid name for ConfigMap: %s", [input.metadata.name])
}

deny[msg] {
  input.kind == "Secret"
  not re_match(name_pattern, input.metadata.name)
  msg := sprintf("invalid name for Secret: %s", [input.metadata.name])
}
