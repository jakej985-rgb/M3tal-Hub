#!/usr/bin/env bash
# ==============================================================================
# M3tal Plugin Page - Production Web Release Build for M3tal-Hub
# ==============================================================================
set -euo pipefail

BASE_HREF="${1:-/m3tal-plugin-page/}"
[[ "$BASE_HREF" != */ ]] && BASE_HREF="${BASE_HREF}/"
[[ "$BASE_HREF" != /* ]] && BASE_HREF="/${BASE_HREF}"

echo "============================================="
echo "Building M3tal Plugin Page Static Release"
echo "Target Base HREF: ${BASE_HREF}"
echo "============================================="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

rm -rf dist build/web
mkdir -p dist build/web

# Copy available static assets and catalog files
for item in index.html plugins.json catalog.json catalog.json.sig .nojekyll README.md; do
  if [ -f "$item" ]; then
    cp "$item" dist/
  fi
done

touch dist/.nojekyll

if [ -d "assets" ]; then
  cp -r assets dist/
fi

if [ -d "projects" ]; then
  cp -r projects dist/
fi

# Ensure assets/css/m3tal.css and assets/js/m3tal.js exist in dist
mkdir -p dist/assets/css dist/assets/js
if [ -f "assets/css/m3tal.css" ]; then
  cp "assets/css/m3tal.css" dist/assets/css/m3tal.css
fi
if [ -f "assets/js/m3tal.js" ]; then
  cp "assets/js/m3tal.js" dist/assets/js/m3tal.js
fi

# Sanitize path references in dist/index.html for hosting under hub subpath
if [ -f "dist/index.html" ]; then
  sed -i 's|href="/assets/|href="assets/|g' dist/index.html
  sed -i 's|src="/assets/|src="assets/|g' dist/index.html
  sed -i "s|fetch('/m3tal-plugin-page/plugins.json')|fetch(new URL('plugins.json', window.location.href.endsWith('/') ? window.location.href : window.location.href + '/').href)|g" dist/index.html
fi

# Sanitize redirect pages
if [ -f "dist/projects/plugins/nginx/index.html" ]; then
  sed -i 's|window.location.replace("/m3tal-plugin-page/");|window.location.replace("../../../");|g' dist/projects/plugins/nginx/index.html
fi

if [ -f "dist/projects/plugins/postgres/index.html" ]; then
  sed -i 's|window.location.replace("/m3tal-plugin-page/");|window.location.replace("../../../");|g' dist/projects/plugins/postgres/index.html
fi

# Mirror output to build/web for universal hub compatibility
cp -r dist/* build/web/

test -f dist/index.html || {
  echo "Error: dist/index.html was not generated!" >&2
  exit 1
}

echo "M3tal Plugin Page release build completed successfully."
