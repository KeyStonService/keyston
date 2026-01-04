package chatops.naming_test

import data.chatops.naming

test_valid_name_allow {
  obj := {"kind":"Service","metadata":{"name":"prod-axiom-svc-v1.0.0"}}
  not naming.deny[_] with input as obj
}

test_invalid_name_deny {
  obj := {"kind":"Deployment","metadata":{"name":"badName"}}
  naming.deny[_] with input as obj
}
