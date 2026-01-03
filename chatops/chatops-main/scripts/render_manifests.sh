#!/bin/bash
# render_manifests.sh - Render Kubernetes manifests with Kustomize

set -e

echo "🏗️ Rendering manifests..."

# Check for required tools
if ! command -v kubectl >/dev/null 2>&1; then
    echo "  ⚠️  kubectl not found, skipping Kubernetes rendering"
    exit 0
fi

if ! command -v kustomize >/dev/null 2>&1; then
    echo "  ⚠️  kustomize not found, skipping Kustomize rendering"
    exit 0
fi

# Check if deploy directory exists
if [ ! -d "deploy" ]; then
    echo "  ⚠️  No deploy directory found, skipping render"
    exit 0
fi

# Render base manifests
echo "  📄 Rendering base manifests..."
if [ -d "deploy/base" ]; then
    kustomize build deploy/base -o dist/rendered-base.yaml
    echo "    ✅ Base manifests rendered to dist/rendered-base.yaml"
fi

# Render overlays
for overlay in deploy/overlays/*/; do
    if [ -d "$overlay" ]; then
        overlay_name=$(basename "$overlay")
        echo "  📄 Rendering overlay: $overlay_name"
        kustomize build "$overlay" -o "dist/rendered-${overlay_name}.yaml"
        echo "    ✅ Overlay $overlay_name rendered to dist/rendered-${overlay_name}.yaml"
    fi
done

echo "✅ Manifest rendering complete"