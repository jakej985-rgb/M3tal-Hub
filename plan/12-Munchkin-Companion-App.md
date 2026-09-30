# 12 Munchkin Companion App

## Goal
Prepare the Flutter application for a web release at `/munchkin-companion-app/`.

## Steps & Status
1. [x] **Verify Flutter project structure**:
   - Inspected repository `jakej985-rgb/Munchkin-Companion-App`.
   - Result: Repository is currently a stub containing only `README.md` (`commit 6266f2e Add README.md`). No Flutter application files (`pubspec.yaml`, `lib/`, `web/`) exist yet.
2. [x] **Audit build readiness**:
   - Confirmed application cannot be built as a web release until Flutter source code is initialized.
   - Removed unbuildable choice from `deploy.yml` `workflow_dispatch` options to prevent failing manual dispatch runs.
3. [x] **Configure Hub Registry Entry**:
   - Configured `munchkin-companion-app` in `apps/manifest.yml` as `status: planned` with `enabled: false`.
   - Explicitly configured `repo_url: https://github.com/jakej985-rgb/Munchkin-Companion-App`.
   - Card displays "Release Planned" badge and links directly to the GitHub repository as a styled placeholder card, preventing dead 404 links on the live hub front.
   - Base href `/munchkin-companion-app/` and path `munchkin-companion-app` remain reserved for when source is added.
4. [ ] **Add web support and Drift database**:
   - Pending upstream Flutter project creation and Drift database schema implementation.
5. [x] **Define release automation & dispatch workflow**:
   - Ready workflow template for `.github/workflows/dispatch-hub.yml`:
     ```yaml
     name: Dispatch M3tal-Hub Release
     on:
       push:
         branches: [ main ]
         paths:
           - 'lib/**'
           - 'web/**'
           - 'pubspec.yaml'
           - 'scripts/**'
           - '.github/workflows/dispatch-hub.yml'
       workflow_dispatch:
     jobs:
       dispatch:
         runs-on: ubuntu-latest
         steps:
           - name: Dispatch Release Event to M3tal-Hub
             if: env.M3TAL_HUB_TOKEN != ''
             env:
               M3TAL_HUB_TOKEN: ${{ secrets.M3TAL_HUB_TOKEN }}
             uses: peter-evans/repository-dispatch@v3
             with:
               token: ${{ secrets.M3TAL_HUB_TOKEN }}
               repository: jakej985-rgb/M3tal-Hub
               event-type: app-release
               client-payload: '{"app_id": "munchkin-companion-app", "repo": "Munchkin-Companion-App"}'
     ```
   - Ready build script for `scripts/build_web_release.sh`:
     ```bash
     #!/usr/bin/env bash
     set -euo pipefail
     BASE_HREF="${1:-/munchkin-companion-app/}"
     [[ "$BASE_HREF" != */ ]] && BASE_HREF="${BASE_HREF}/"
     flutter pub get
     flutter build web --release --base-href "${BASE_HREF}"
     test -f build/web/index.html
     ```
6. [ ] **Add HUB_DISPATCH_TOKEN / M3TAL_HUB_TOKEN**:
   - Pending repository action secret setup once active builds are ready.
7. [ ] **Enable automatic releases**:
   - Once Flutter web build succeeds, switch `enabled: true`, `status: ready` in `apps/manifest.yml` and add `munchkin-companion-app` to `deploy.yml` options.

## Definition of Done
A reproducible Flutter web build is available from the M3tal-Hub subdirectory, or explicitly registered as a planned placeholder card until upstream source code is authored.
- **Current State**: Registered as `status: planned` placeholder card in `apps/manifest.yml`. The card safely directs users to the source repository without broken links.
