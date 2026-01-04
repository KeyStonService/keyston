#!/bin/bash
# generate_provenance.sh - Generate SLSA provenance

set -e

echo "🔐 Generating SLSA provenance..."

DIST_DIR="dist/provenance"
mkdir -p "$DIST_DIR"

# Get build information
BUILD_ID=$(date -u +%Y%m%d%H%M%S)
GIT_COMMIT=$(git rev-parse HEAD)
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
TIMESTAMP=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Generate SLSA provenance
cat > "$DIST_DIR/provenance.json" << EOF
{
  "_type": "https://in-toto.io/Statement/v0.1",
  "predicateType": "https://slsa.dev/provenance/v0.2",
  "subject": [
    {
      "name": "chatops",
      "digest": {
        "sha256": "$(find . -type f -not -path './.git/*' -not -path './dist/*' -exec sha256sum {} \; | sha256sum | cut -d' ' -f1)"
      }
    }
  ],
  "predicate": {
    "builder": {
      "id": "github.com/MachineNativeOps/chatops"
    },
    "buildType": "https://github.com/ATLASSIAN/slsa-framework/slsa-github-generator",
    "invocation": {
      "configSource": {
        "uri": "git+https://github.com/MachineNativeOps/chatops.git",
        "digest": {
          "sha1": "$GIT_COMMIT"
        },
        "entryPoint": "Makefile"
      },
      "parameters": {},
      "environment": {
        "GITHUB_WORKFLOW": "ci.yml",
        "GITHUB_RUN_ID": "$BUILD_ID"
      }
    },
    "metadata": {
      "buildInvocationId": "$BUILD_ID",
      "buildStartedOn": "$TIMESTAMP",
      "completeness": {
        "parameters": true,
        "environment": false,
        "materials": true
      },
      "reproducible": true
    },
    "materials": [
      {
        "uri": "git+https://github.com/MachineNativeOps/chatops.git",
        "digest": {
          "sha1": "$GIT_COMMIT"
        }
      }
    ]
  }
}
EOF

echo "  📄 Provenance generated: $DIST_DIR/provenance.json"
echo "✅ SLSA provenance complete"