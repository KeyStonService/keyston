# ═══════════════════════════════════════════════════════════════════════════════
#                    Unmanned Island System - Makefile
#                    MN-DOC & Knowledge Graph Generation Automation
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   make mndoc           - Generate MN-DOC from README.md
#   make kg              - Build Knowledge Graph from repository
#   make superroot       - Project entities to SuperRoot format
#   make all-kg          - Run all generation tasks
#   make check-drift     - Check if generated files are up-to-date
#   make clean-generated - Remove all generated YAML files
#   make analyze-reports - Analyze root-level reports
#
# ═══════════════════════════════════════════════════════════════════════════════

.PHONY: mndoc kg superroot all-kg check-drift clean-generated analyze-reports help

# Default target
.DEFAULT_GOAL := help

# Python interpreter
PYTHON := python3

# Source files (source of truth)
README := README.md
MNDOC_OUTPUT := docs/generated/generated-mndoc.yaml
KG_OUTPUT := docs/generated/knowledge-graph.yaml
SUPERROOT_OUTPUT := docs/generated/superroot-entities.yaml
REPORTS_ANALYSIS_MD := docs/reports-analysis.md
REPORTS_ANALYSIS_JSON := docs/reports-analysis.json

# ─────────────────────────────────────────────────────────────────────────────
# MN-DOC Generation
# ─────────────────────────────────────────────────────────────────────────────
mndoc:
	@echo "🔄 Generating MN-DOC from README.md..."
	$(PYTHON) tools/docs/generate_mndoc_from_readme.py \
		--readme $(README) \
		--output $(MNDOC_OUTPUT) \
		--verbose
	@echo "✅ MN-DOC generated: $(MNDOC_OUTPUT)"

# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Graph Generation
# ─────────────────────────────────────────────────────────────────────────────
kg: mndoc
	@echo "🔄 Building Knowledge Graph..."
	$(PYTHON) tools/docs/generate_knowledge_graph.py \
		--repo-root . \
		--output $(KG_OUTPUT) \
		--verbose
	@echo "✅ Knowledge Graph generated: $(KG_OUTPUT)"

# ─────────────────────────────────────────────────────────────────────────────
# SuperRoot Entity Projection
# ─────────────────────────────────────────────────────────────────────────────
superroot: kg
	@echo "🔄 Projecting to SuperRoot entities..."
	@if [ -f "tools/docs/project_to_superroot.py" ]; then \
		$(PYTHON) tools/docs/project_to_superroot.py \
			--kg $(KG_OUTPUT) \
			--output $(SUPERROOT_OUTPUT) \
			--verbose; \
		echo "✅ SuperRoot entities generated: $(SUPERROOT_OUTPUT)"; \
	else \
		echo "⚠️  SuperRoot projection tool not found (optional)"; \
	fi

# ─────────────────────────────────────────────────────────────────────────────
# All Knowledge Graph Tasks
# ─────────────────────────────────────────────────────────────────────────────
all-kg: mndoc kg superroot
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  ✅ All MN-DOC & Knowledge Graph artifacts generated!"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Generated files:"
	@echo "  - $(MNDOC_OUTPUT)"
	@echo "  - $(KG_OUTPUT)"
	@if [ -f "$(SUPERROOT_OUTPUT)" ]; then echo "  - $(SUPERROOT_OUTPUT)"; fi
	@echo ""
	@echo "Next steps:"
	@echo "  1. Review generated files: git diff"
	@echo "  2. Commit changes: git add . && git commit -m 'Update MN-DOC & KG'"
	@echo ""

# ─────────────────────────────────────────────────────────────────────────────
# Check for Drift (CI use)
# ─────────────────────────────────────────────────────────────────────────────
check-drift: all-kg
	@echo "🔍 Checking for drift in generated files..."
	@if git diff --quiet $(MNDOC_OUTPUT) $(KG_OUTPUT) 2>/dev/null; then \
		echo "✅ Generated files are up-to-date"; \
	else \
		echo "❌ Generated files have drifted from source!"; \
		echo ""; \
		echo "The following files need to be regenerated and committed:"; \
		git diff --name-only $(MNDOC_OUTPUT) $(KG_OUTPUT) 2>/dev/null || true; \
		echo ""; \
		echo "Run 'make all-kg' and commit the changes."; \
		exit 1; \
	fi

# ─────────────────────────────────────────────────────────────────────────────
# Clean Generated Files
# ─────────────────────────────────────────────────────────────────────────────
clean-generated:
	@echo "🧹 Removing generated files..."
	rm -f $(MNDOC_OUTPUT) $(KG_OUTPUT) $(SUPERROOT_OUTPUT)
	@echo "✅ Generated files removed"

# ─────────────────────────────────────────────────────────────────────────────
# Reports Analysis
# ─────────────────────────────────────────────────────────────────────────────
analyze-reports:
	@echo "📊 Analyzing root-level reports..."
	$(PYTHON) tools/docs/analyze_root_reports.py \
		--repo-root . \
		--output $(REPORTS_ANALYSIS_MD) \
		--json-output $(REPORTS_ANALYSIS_JSON) \
		--verbose
	@echo "✅ Reports analysis complete!"
	@echo "   - Markdown: $(REPORTS_ANALYSIS_MD)"
	@echo "   - JSON: $(REPORTS_ANALYSIS_JSON)"

# ─────────────────────────────────────────────────────────────────────────────
# Governance Validation
# ─────────────────────────────────────────────────────────────────────────────
validate-governance:
	@echo "🔍 Validating Architecture Governance Matrix..."
	$(PYTHON) tools/governance/validate-governance-matrix.py --verbose

validate-governance-ci:
	@echo "🔍 Validating Architecture Governance Matrix (CI mode)..."
	$(PYTHON) tools/governance/validate-governance-matrix.py

# ─────────────────────────────────────────────────────────────────────────────
# Cross-Platform Build System
# ─────────────────────────────────────────────────────────────────────────────
.PHONY: build build-windows build-macos build-linux build-docker build-all clean package

# Detect OS
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    DETECTED_OS := linux
endif
ifeq ($(UNAME_S),Darwin)
    DETECTED_OS := macos
endif
ifeq ($(OS),Windows_NT)
    DETECTED_OS := windows
endif

build:
	@echo "🔨 Building for $(DETECTED_OS)..."
	$(PYTHON) build/build.py $(DETECTED_OS)

build-windows:
	@echo "🪟 Building Windows installers..."
	@cd build/windows && ./build-windows.bat

build-macos:
	@echo "🍎 Building macOS installers..."
	@cd build/macos && chmod +x build-macos.sh && ./build-macos.sh

build-linux:
	@echo "🐧 Building Linux packages..."
	@cd build/linux && chmod +x build-linux.sh && ./build-linux.sh

build-docker:
	@echo "🐳 Building Docker images..."
	$(PYTHON) build/build.py docker

build-all: build-windows build-macos build-linux build-docker
	@echo ""
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  ✅ All platform builds completed!"
	@echo "════════════════════════════════════════════════════════════════"

clean:
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/windows/dist build/windows/build
	@rm -rf build/macos/dist build/macos/build
	@rm -rf build/linux/dist build/linux/build
	@rm -rf build/linux/debian/synergymesh-governance_*
	@rm -rf build/linux/redhat/*.rpm
	@rm -f build/linux/*.AppImage
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete"

package: build
	@echo "📦 Packaging build artifacts..."
	@mkdir -p dist
	@if [ -d "build/windows/dist" ]; then cp -r build/windows/dist/* dist/ 2>/dev/null || true; fi
	@if [ -d "build/macos" ]; then cp build/macos/*.dmg build/macos/*.pkg dist/ 2>/dev/null || true; fi
	@if [ -d "build/linux" ]; then cp build/linux/*.AppImage dist/ 2>/dev/null || true; fi
	@echo "✅ Packages copied to dist/"

# ─────────────────────────────────────────────────────────────────────────────
# Help
# ─────────────────────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "═══════════════════════════════════════════════════════════════════"
	@echo "           Unmanned Island System - Build & Automation"
	@echo "═══════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "📦 Build Targets:"
	@echo ""
	@echo "  make build           Build for current platform ($(DETECTED_OS))"
	@echo "  make build-windows   Build Windows EXE/MSI installers"
	@echo "  make build-macos     Build macOS DMG/PKG installers"
	@echo "  make build-linux     Build Linux AppImage/DEB/RPM packages"
	@echo "  make build-docker    Build Docker images"
	@echo "  make build-all       Build for all platforms"
	@echo "  make clean           Remove build artifacts"
	@echo "  make package         Package build artifacts to dist/"
	@echo ""
	@echo "📚 Documentation Targets:"
	@echo ""
	@echo "  make mndoc           Generate MN-DOC from README.md"
	@echo "  make kg              Build Knowledge Graph (includes mndoc)"
	@echo "  make superroot       Project to SuperRoot entities (includes kg)"
	@echo "  make all-kg          Run all generation tasks"
	@echo "  make check-drift     Check if generated files are up-to-date"
	@echo "  make clean-generated Remove all generated YAML files"
	@echo "  make analyze-reports Analyze root-level reports"
	@echo ""
	@echo "🔍 Validation Targets:"
	@echo ""
	@echo "  make validate-governance     Validate Architecture Governance Matrix"
	@echo "  make validate-governance-ci  Validate governance (CI mode)"
	@echo ""
	@echo "ℹ️  General:"
	@echo ""
	@echo "  make help            Show this help message"
	@echo ""
	@echo "Source of Truth:"
	@echo "  - README.md, code, config, docs = source"
	@echo "  - generated-mndoc.yaml, knowledge-graph.yaml = build artifacts"
	@echo ""
	@echo "Build Workflow:"
	@echo "  1. Run: make build (or make build-<platform>)"
	@echo "  2. Test locally"
	@echo "  3. Run: make package"
	@echo "  4. Create release: git tag v1.0.0 && git push --tags"
	@echo ""
