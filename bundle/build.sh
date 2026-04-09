#!/usr/bin/env bash
# Build dist/miinto-secoda-analyst.mcpb from bundle/ config + live source.
# Always creates a fresh zip — no incremental updates, no stale pycache.
#
# Prerequisites:
#   - bundle/manifest.json must exist and contain no placeholder values
#   - python3
set -euo pipefail

BUNDLE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$BUNDLE_DIR")"

if [[ ! -f "$BUNDLE_DIR/manifest.json" ]]; then
  echo "Error: bundle/manifest.json not found."
  echo "  cp bundle/manifest.template.json bundle/manifest.json"
  echo "  # then fill in your org credentials"
  exit 1
fi

python3 - <<EOF
import zipfile, pathlib, json, sys

bundle = pathlib.Path("$BUNDLE_DIR")
repo   = pathlib.Path("$REPO_ROOT")

manifest = json.loads((bundle / "manifest.json").read_text())
name     = manifest["name"]
out      = repo / "dist" / f"{name}.mcpb"
out.parent.mkdir(parents=True, exist_ok=True)

config_files = ["manifest.json", "pyproject.toml", ".python-version"]
missing = [f for f in config_files if not (bundle / f).exists()]
if missing:
    sys.exit(f"Missing bundle/ files: {missing}")

# Package source is in src/secoda_analysis_mcp — bundle as secoda_analysis_mcp/
src_pkg = repo / "src" / "secoda_analysis_mcp"

with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in config_files:
        z.write(bundle / f, f)
    for p in sorted(src_pkg.rglob("*")):
        if "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        # Strip src/ prefix: src/secoda_analysis_mcp/x.py → secoda_analysis_mcp/x.py
        z.write(p, p.relative_to(repo / "src"))

names = zipfile.ZipFile(out).namelist()
print(f"Built {out} ({len(names)} files)")
for n in names:
    print(f"  {n}")
EOF
