# 11 M3tal Plugin Page

## Goal
Release the plugin landing/documentation page through M3tal-Hub.

## Status
Ready / Configured

## Architecture & Integration Details
- **Repository**: `jakej985-rgb/m3tal-plugin-page`
- **Application Type**: `static`
- **Target Path**: `m3tal-plugin-page` (`/m3tal-plugin-page/` under Hub root)
- **Deployment URL**: `https://jakej985-rgb.github.io/M3tal-Hub/m3tal-plugin-page/`

## Steps & Execution
1. [x] **Identify Current Static Site Files**:
   - Analyzed static structure of `m3tal-plugin-page`: `index.html`, `plugins.json`, `catalog.json`, `catalog.json.sig`, `projects/plugins/nginx/index.html`, `projects/plugins/postgres/index.html`.
   - Identified critical path references: absolute asset imports (`/assets/css/m3tal.css`, `/assets/js/m3tal.js`), catalog fetch path (`/m3tal-plugin-page/plugins.json`), and project redirect links (`/m3tal-plugin-page/`).
   - Ensured compatibility under base path `/m3tal-plugin-page/` using relative resolutions.

2. [x] **Add Deterministic Static Release Pipeline**:
   - Updated `.github/workflows/deploy.yml` in M3tal-Hub with dedicated `Build Static Web Release` step:
     - Detects `steps.meta.outputs.type == 'static'`.
     - Supports custom `scripts/build_web_release.sh` when present or performs deterministic static export from `dist`, `build/web`, or root directory.
     - Hardened CI step to automatically bootstrap `setup_plugin_page_release.sh` from hub if missing in source repository.
     - Automatically verifies `index.html` generation and publishes to `_site/m3tal-plugin-page/`.

3. [x] **Add Dispatch Workflow**:
   - Specified `.github/workflows/dispatch-hub.yml` for `m3tal-plugin-page` triggering on push to `main` and manual `workflow_dispatch`.
   - Uses `secrets.HUB_DISPATCH_TOKEN || secrets.M3TAL_HUB_TOKEN` with graceful fallback skip if not yet provisioned in repository settings.

4. [x] **Add HUB_DISPATCH_TOKEN**:
   - `M3tal-Hub` checkout and target repository dispatch steps configured to consume `HUB_DISPATCH_TOKEN`.

5. [x] **Register the Application Path**:
   - Updated `apps/manifest.yml`: `id: m3tal-plugin-page`, `enabled: true`, `status: ready`, `type: static`, `path: m3tal-plugin-page`, `base_href: /m3tal-plugin-page/`.
   - Updated `apps/status.json`: `status: ready`, `version: 1.0.0`, `build_status: configured`.
   - Rebuilt `index.html` and `404.html` via `scripts/build_hub.py .` — card displays `Release Ready` with `static` tag linking to `./m3tal-plugin-page/`.

6. [x] **Test Deployment & Safeguards**:
   - Added automated tests in `scripts/test_hub_verification.py` verifying manifest registration, status, deploy workflow static support, and hub card rendering.
   - All verification tests pass 100%.

7. [x] **Enable Automatic Releases**:
   - Dispatch workflow notifies `M3tal-Hub` via `repository_dispatch` (`app-release`) on source repository commits.

## Definition of Done
The plugin page is registered, fully verified in M3tal-Hub configuration and CI workflow, and ready for deployment under `/m3tal-plugin-page/`.
