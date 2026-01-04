SHELL := /usr/bin/env bash
.ONESHELL:
.SHELLFLAGS := -euo pipefail -c

ROOT ?= .
ARTIFACTS ?= artifacts
REPORTS ?= $(ARTIFACTS)/reports
SBOM ?= $(ARTIFACTS)/sbom
ATTEST ?= $(ARTIFACTS)/attestations
NAMING ?= $(REPORTS)/naming
AUTOFIX ?= $(REPORTS)/auto-fix

.PHONY: help
help:
	@printf "%s\n" \
	"Targets:" \
	"  bootstrap           Setup local folders + basic checks" \
	"  lint                Run local lint (shellcheck/hadolint optional)" \
	"  policy              Run OPA/Conftest naming checks (if conftest installed)" \
	"  naming              Run naming discovery->verify->report" \
	"  sbom                Generate SBOM (stub)" \
	"  provenance          Generate provenance (stub)" \
	"  freeze              Create freeze gate file" \
	"  unfreeze            Remove freeze gate file"

.PHONY: bootstrap
bootstrap:
	mkdir -p $(SBOM) $(ATTEST) $(REPORTS) $(AUTOFIX)/details $(NAMING)
	bash scripts/bootstrap.sh

.PHONY: lint
lint:
	bash scripts/gitleaks-scan.sh || true
	bash scripts/semgrep-scan.sh || true
	bash scripts/openapi-lint.sh || true

.PHONY: policy
policy:
	bash scripts/policy-validate.sh

.PHONY: naming
naming:
	bash scripts/naming/discover.sh
	bash scripts/naming/conftest-verify.sh
	bash scripts/naming/remediate.sh || true
	bash scripts/naming/dry-run.sh
	bash scripts/naming/staged-rename.sh
	bash scripts/naming/cutover.sh
	bash scripts/naming/rollback.sh
	bash scripts/naming/verify-post-rollback.sh || true
	node scripts/naming/report-sla.mjs || true

.PHONY: sbom
sbom:
	bash scripts/gen-sbom.sh

.PHONY: provenance
provenance:
	bash scripts/slsa-attest.sh

.PHONY: freeze
freeze:
	bash scripts/freeze-deploy.sh

.PHONY: unfreeze
unfreeze:
	bash scripts/unfreeze-deploy.sh
