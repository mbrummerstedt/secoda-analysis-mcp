#!/usr/bin/env bash
# build.sh — builds the Miinto-specific .mcpb bundle
# Requires: bundle/manifest.json (gitignored, contains org credentials)
# Output:   dist/miinto-secoda-analyst.mcpb

set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$BUNDLE_DIR")"
DIST_DIR="$REPO_ROOT/dist"
OUTPUT="$DIST_DIR/miinto-secoda-analyst.mcpb"

if [ ! -f "$BUNDLE_DIR/manifest.json" ]; then
  echo "Error: bundle/manifest.json not found."
  echo "Copy bundle/manifest.template.json to bundle/manifest.json and fill in your org credentials."
  exit 1
fi

mkdir -p "$DIST_DIR"

# Build from bundle directory so paths inside the zip are relative
cd "$BUNDLE_DIR"
zip -r "$OUTPUT" manifest.json server/ README.md 2>/dev/null || \
  zip -r "$OUTPUT" manifest.json server/

echo ""
echo "Bundle created: $OUTPUT"
echo ""
echo "To install:"
echo "  1. Open Claude Desktop → Settings → Developer"
echo "  2. Drag and drop $OUTPUT onto the window"
echo "  OR"
echo "  3. Share $OUTPUT with colleagues — they drag and drop it the same way"
