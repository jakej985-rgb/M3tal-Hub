#!/usr/bin/env bash
# ==============================================================================
# Setup M3tal Plugin Page Release Artifacts
# Prepares scripts/build_web_release.sh, .github/workflows/dispatch-hub.yml,
# assets/css/m3tal.css, assets/js/m3tal.js, and path adjustments in m3tal-plugin-page.
# ==============================================================================
set -euo pipefail

TARGET_DIR="${1:-/home/m3tal/apps/m3tal-plugin-page}"

if [ ! -d "$TARGET_DIR" ]; then
  echo "Error: Target directory '$TARGET_DIR' does not exist." >&2
  exit 1
fi

echo "Configuring release artifacts in $TARGET_DIR..."

# 1. Create scripts/build_web_release.sh
mkdir -p "$TARGET_DIR/scripts"
cat << 'EOF' > "$TARGET_DIR/scripts/build_web_release.sh"
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
EOF
chmod +x "$TARGET_DIR/scripts/build_web_release.sh"

# 2. Create .github/workflows/dispatch-hub.yml
mkdir -p "$TARGET_DIR/.github/workflows"
cat << 'EOF' > "$TARGET_DIR/.github/workflows/dispatch-hub.yml"
name: Dispatch M3tal-Hub Release

on:
  push:
    branches: [ main ]
    paths:
      - 'index.html'
      - 'plugins.json'
      - 'catalog.json'
      - 'catalog.json.sig'
      - 'assets/**'
      - 'projects/**'
      - 'scripts/**'
      - '.github/workflows/dispatch-hub.yml'
  workflow_dispatch:
    inputs:
      version:
        description: 'Version tag or release label (defaults to commit SHA)'
        required: false
        default: ''

jobs:
  dispatch:
    name: Notify M3tal-Hub of Release
    runs-on: ubuntu-latest
    steps:
      - name: Validate Dispatch Token
        id: check-token
        run: |
          TOKEN="${{ secrets.HUB_DISPATCH_TOKEN || secrets.M3TAL_HUB_TOKEN }}"
          if [ -z "$TOKEN" ]; then
            echo "::warning ::HUB_DISPATCH_TOKEN / M3TAL_HUB_TOKEN secret is not configured in repository settings. Skipping automatic dispatch to M3tal-Hub."
            echo "configured=false" >> $GITHUB_OUTPUT
          else
            echo "configured=true" >> $GITHUB_OUTPUT
          fi

      - name: Dispatch Release Event to M3tal-Hub
        if: steps.check-token.outputs.configured == 'true'
        uses: peter-evans/repository-dispatch@v3
        with:
          token: ${{ secrets.HUB_DISPATCH_TOKEN || secrets.M3TAL_HUB_TOKEN }}
          repository: jakej985-rgb/M3tal-Hub
          event-type: app-release
          client-payload: >-
            {
              "app_id": "m3tal-plugin-page",
              "repo": "m3tal-plugin-page",
              "ref": "${{ github.sha }}",
              "version": "${{ github.event.inputs.version || github.ref_name }}"
            }

      - name: Confirm Dispatch
        if: steps.check-token.outputs.configured == 'true'
        run: |
          echo "Successfully dispatched app-release event for m3tal-plugin-page to jakej985-rgb/M3tal-Hub."
EOF

# 3. Create assets/css/m3tal.css
mkdir -p "$TARGET_DIR/assets/css"
cat << 'EOF' > "$TARGET_DIR/assets/css/m3tal.css"
:root {
  --bg: #0d1117;
  --surface: #161b22;
  --surface-hover: #21262d;
  --panel-bg: rgba(22, 27, 34, 0.85);
  --panel-border: #30363d;
  --text-main: #e6edf3;
  --text-muted: #8b949e;
  --accent-cyan: #00f2fe;
  --accent-emerald: #10b981;
  --font-display: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  --transition-fast: 0.2s ease;
  --shadow-glow: 0 0 12px rgba(0, 242, 254, 0.4);
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--bg);
  color: var(--text-main);
  font-family: var(--font-display);
  min-height: 100vh;
  line-height: 1.5;
}

.m3tal-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem 1.5rem 4rem 1.5rem;
}

.m3tal-hero {
  margin-bottom: 2rem;
}

.m3tal-hero h1 {
  font-size: 2.25rem;
  font-weight: 700;
  margin: 0 0 0.5rem 0;
  color: var(--text-main);
}

.m3tal-hero p {
  color: var(--text-muted);
  font-size: 1.1rem;
  margin: 0;
}

.m3tal-card {
  background: var(--panel-bg);
  border: 1px solid var(--panel-border);
  border-radius: 12px;
  padding: 1.5rem;
  transition: transform var(--transition-fast), border-color var(--transition-fast), box-shadow var(--transition-fast);
  backdrop-filter: blur(8px);
}

.m3tal-card:hover {
  transform: translateY(-2px);
  border-color: var(--accent-cyan);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}

a {
  color: var(--accent-cyan);
  text-decoration: none;
  transition: color var(--transition-fast);
}

a:hover {
  text-decoration: underline;
}

#m3tal-global-header {
  border-bottom: 1px solid var(--panel-border);
  background: rgba(13, 17, 23, 0.9);
  backdrop-filter: blur(12px);
  position: sticky;
  top: 0;
  z-index: 100;
  padding: 0.75rem 1.5rem;
}

.m3tal-nav {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.m3tal-nav-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--text-main);
  text-decoration: none;
}

.m3tal-nav-links {
  display: flex;
  gap: 1.25rem;
  align-items: center;
}

.m3tal-nav-link {
  color: var(--text-muted);
  font-size: 0.9rem;
  transition: color var(--transition-fast);
}

.m3tal-nav-link:hover {
  color: var(--text-main);
  text-decoration: none;
}

#m3tal-global-footer {
  border-top: 1px solid var(--panel-border);
  padding: 2rem 1.5rem;
  color: var(--text-muted);
  font-size: 0.85rem;
  text-align: center;
  margin-top: 4rem;
}
EOF

# 4. Create assets/js/m3tal.js
mkdir -p "$TARGET_DIR/assets/js"
cat << 'EOF' > "$TARGET_DIR/assets/js/m3tal.js"
document.addEventListener('DOMContentLoaded', () => {
  const header = document.getElementById('m3tal-global-header');
  if (header && !header.hasChildNodes()) {
    header.innerHTML = `
      <nav class="m3tal-nav">
        <a class="m3tal-nav-brand" href="../">
          <span>⚙️</span>
          <span>M3TAL HUB</span>
        </a>
        <div class="m3tal-nav-links">
          <a class="m3tal-nav-link" href="../">Hub Home</a>
          <a class="m3tal-nav-link" href="https://github.com/jakej985-rgb/m3tal-plugin-page" target="_blank" rel="noopener noreferrer">Plugin Repo</a>
          <a class="m3tal-nav-link" href="https://github.com/jakej985-rgb/m3tal-core" target="_blank" rel="noopener noreferrer">M3tal Core</a>
        </div>
      </nav>
    `;
  }

  const footer = document.getElementById('m3tal-global-footer');
  if (footer && !footer.hasChildNodes()) {
    footer.innerHTML = `
      <div class="m3tal-container" style="padding: 0;">
        <p>M3TAL Plugins Directory &bull; Part of the M3tal Application Ecosystem</p>
      </div>
    `;
  }
});
EOF

# 5. Fix paths in index.html and redirect pages
if [ -f "$TARGET_DIR/index.html" ]; then
  sed -i 's|href="/assets/|href="assets/|g' "$TARGET_DIR/index.html"
  sed -i 's|src="/assets/|src="assets/|g' "$TARGET_DIR/index.html"
  sed -i "s|fetch('/m3tal-plugin-page/plugins.json')|fetch(new URL('plugins.json', window.location.href.endsWith('/') ? window.location.href : window.location.href + '/').href)|g" "$TARGET_DIR/index.html"
fi

if [ -f "$TARGET_DIR/projects/plugins/nginx/index.html" ]; then
  sed -i 's|window.location.replace("/m3tal-plugin-page/");|window.location.replace("../../../");|g' "$TARGET_DIR/projects/plugins/nginx/index.html"
fi

if [ -f "$TARGET_DIR/projects/plugins/postgres/index.html" ]; then
  sed -i 's|window.location.replace("/m3tal-plugin-page/");|window.location.replace("../../../");|g' "$TARGET_DIR/projects/plugins/postgres/index.html"
fi

echo "M3tal Plugin Page successfully configured."
